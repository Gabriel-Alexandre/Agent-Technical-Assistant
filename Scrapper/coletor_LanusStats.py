"""
Coletor para obter partidas ao vivo usando SofaScore
"""

import asyncio
import json
import requests
from datetime import datetime
from playwright.async_api import async_playwright
from pathlib import Path

class ColetorPartidasAoVivo:
    """Coletor para obter partidas ao vivo do SofaScore"""
    
    def __init__(self):
        self.sofascore_base_url = "https://api.sofascore.com/api/v1/"
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        
    async def obter_partidas_ao_vivo_sofascore(self):
        """Obtém partidas ao vivo do SofaScore usando Playwright"""
        partidas_ao_vivo = []
        
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                ]
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                extra_http_headers={
                    'Accept': 'application/json',
                    'Accept-Language': 'pt-BR,pt;q=0.9',
                    'Referer': 'https://www.sofascore.com/'
                }
            )
            
            page = await context.new_page()
            
            try:
                # URL para partidas ao vivo do SofaScore
                url = f"{self.sofascore_base_url}sport/football/events/live"
                
                response = await page.goto(url, wait_until='networkidle', timeout=30000)
                
                if response.status == 200:
                    content = await page.content()
                    
                    # Extrair JSON do conteúdo
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    
                    if json_start != -1 and json_end > json_start:
                        json_content = content[json_start:json_end]
                        data = json.loads(json_content)
                        
                        if 'events' in data:
                            # Salvar todos os dados completos da API
                            partidas_ao_vivo = data['events']
                    
            except Exception as e:
                print(f"❌ Erro ao obter partidas do SofaScore: {e}")
                
            finally:
                await browser.close()
        
        return partidas_ao_vivo
    
    async def listar_todas_partidas_ao_vivo(self):
        """Lista todas as partidas ao vivo do SofaScore e salva em JSON"""
        
        # Obter partidas do SofaScore
        partidas_sofascore = await self.obter_partidas_ao_vivo_sofascore()
        
        # Preparar dados para salvar (mantendo estrutura completa da API)
        dados_para_salvar = {
            'timestamp': datetime.now().isoformat(),
            'total_partidas': len(partidas_sofascore),
            'fonte': 'SofaScore',
            'api_endpoint': 'sport/football/events/live',
            'events': partidas_sofascore
        }
        
        # Salvar JSON na pasta results
        timestamp_arquivo = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"partidas_ao_vivo_{timestamp_arquivo}.json"
        caminho_arquivo = self.results_dir / nome_arquivo
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados_para_salvar, f, indent=2, ensure_ascii=False)
        
        return partidas_sofascore

async def main():
    """Função principal"""
    print("🏆 COLETOR DE PARTIDAS DE FUTEBOL - SofaScore")
    print("=" * 50)
    print("🚀 Iniciando busca por partidas ao vivo...")
    
    try:
        coletor = ColetorPartidasAoVivo()
        partidas = await coletor.listar_todas_partidas_ao_vivo()
        
        print(f"✅ {len(partidas)} partidas ao vivo encontradas e salvas")
        print("=" * 50)
        print("🏁 Busca concluída!")
        
        return partidas
            
    except KeyboardInterrupt:
        print("\n⏹️ Execução interrompida pelo usuário.")
        return None
    except Exception as e:
        print(f"❌ Erro na execução: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(main())
