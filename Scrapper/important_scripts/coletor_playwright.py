# coletor_playwright.py
"""
Coletor SofaScore usando Playwright para obter shotmap de partidas
"""

import asyncio
import json
import sys
from playwright.async_api import async_playwright
from pathlib import Path

class PlaywrightSofaScoreCollector:
    """Coletor usando Playwright para obter shotmap"""
    
    def __init__(self):
        self.base_url = "https://api.sofascore.com/api/v1/"
        self.website_url = "https://www.sofascore.com/"
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
    async def create_browser_context(self, playwright):
        """Cria contexto do navegador com configurações realistas"""
        browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='pt-BR',
            timezone_id='America/Sao_Paulo',
            extra_http_headers={
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        
        return browser, context
    
    async def get_shotmap(self, match_id):
        """Obtém shotmap de uma partida específica"""
        async with async_playwright() as playwright:
            browser, context = await self.create_browser_context(playwright)
            page = await context.new_page()
            
            try:
                # Construir URL da API
                url = f"{self.base_url}event/{match_id}/shotmap"
                print(f"🎯 Acessando: {url}")
                
                # Fazer requisição para shotmap
                response = await page.goto(url, wait_until='networkidle', timeout=30000)
                print(f"📡 Status da resposta: {response.status}")
                
                if response.status == 200:
                    # Obter conteúdo da página
                    content = await page.content()
                    
                    # Tentar extrair JSON do conteúdo
                    try:
                        json_start = content.find('{')
                        json_end = content.rfind('}') + 1
                        
                        if json_start != -1 and json_end > json_start:
                            json_content = content[json_start:json_end]
                            data = json.loads(json_content)
                            print("✅ Dados JSON extraídos com sucesso!")
                            
                            # Salvar dados
                            filename = f"shotmap_{match_id}.json"
                            filepath = self.data_dir / filename
                            
                            with open(filepath, 'w', encoding='utf-8') as f:
                                json.dump(data, f, indent=2, ensure_ascii=False)
                            
                            print(f"💾 Dados salvos em: {filepath.absolute()}")
                            return data
                        else:
                            print("⚠️ Conteúdo não parece ser JSON válido")
                            return None
                            
                    except json.JSONDecodeError as e:
                        print(f"⚠️ Erro ao decodificar JSON: {e}")
                        return None
                        
                else:
                    print(f"❌ Erro na requisição: Status {response.status}")
                    return None
                    
            except Exception as e:
                print(f"❌ Erro na requisição: {e}")
                return None
                
            finally:
                await browser.close()

async def main():
    """Função principal"""
    if len(sys.argv) != 2:
        print("❌ Uso: python coletor_playwright.py <match_id>")
        print("📝 Exemplo: python coletor_playwright.py 11161648")
        return
    
    match_id = sys.argv[1]
    print(f"🚀 Iniciando coleta de shotmap para partida ID: {match_id}")
    print("=" * 50)
    
    collector = PlaywrightSofaScoreCollector()
    result = await collector.get_shotmap(match_id)
    
    if result:
        print("✅ Coleta realizada com sucesso!")
        if isinstance(result, dict):
            shots = result.get('shotmap', [])
            print(f"📊 Shots encontrados: {len(shots)}")
    else:
        print("❌ Falha na coleta")
    
    print("=" * 50)
    print("🏁 Processo concluído!")

if __name__ == "__main__":
    asyncio.run(main()) 