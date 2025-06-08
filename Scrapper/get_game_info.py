"""
Coletor de dados ao vivo do SofaScore para Assistente Técnico
Coleta dados relevantes para análise técnica em tempo real
"""

import asyncio
import json
import sys
from datetime import datetime
from playwright.async_api import async_playwright
from pathlib import Path

class SofaScoreLiveCollector:
    """Coletor de dados ao vivo do SofaScore para assistente técnico"""
    
    def __init__(self):
        self.base_url = "https://api.sofascore.com/api/v1/"
        self.website_url = "https://www.sofascore.com/"
        self.data_dir = Path("live_data")
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
    
    async def fetch_api_data(self, page, endpoint):
        """Função auxiliar para buscar dados de uma API endpoint"""
        try:
            response = await page.goto(endpoint, wait_until='networkidle', timeout=20000)
            
            if response.status == 200:
                content = await page.content()
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_content = content[json_start:json_end]
                    return json.loads(json_content)
            return None
        except Exception as e:
            print(f"⚠️ Erro ao buscar {endpoint}: {e}")
            return None
    
    async def get_live_match_data(self, match_id):
        """Coleta todos os dados relevantes de uma partida ao vivo"""
        async with async_playwright() as playwright:
            browser, context = await self.create_browser_context(playwright)
            page = await context.new_page()
            
            try:
                print(f"🔄 Coletando dados ao vivo da partida {match_id}...")
                
                # Dados principais da partida
                match_data = {}
                timestamp = datetime.now().isoformat()
                
                # 1. Informações básicas da partida
                print("📊 Coletando informações básicas...")
                basic_info = await self.fetch_api_data(page, f"{self.base_url}event/{match_id}")
                if basic_info:
                    match_data['basic_info'] = {
                        'homeTeam': basic_info.get('event', {}).get('homeTeam', {}),
                        'awayTeam': basic_info.get('event', {}).get('awayTeam', {}),
                        'homeScore': basic_info.get('event', {}).get('homeScore', {}),
                        'awayScore': basic_info.get('event', {}).get('awayScore', {}),
                        'status': basic_info.get('event', {}).get('status', {}),
                        'startTimestamp': basic_info.get('event', {}).get('startTimestamp'),
                        'tournament': basic_info.get('event', {}).get('tournament', {}),
                        'season': basic_info.get('event', {}).get('season', {})
                    }
                
                # 2. Estatísticas da partida
                print("📈 Coletando estatísticas...")
                stats = await self.fetch_api_data(page, f"{self.base_url}event/{match_id}/statistics")
                if stats:
                    match_data['statistics'] = stats.get('statistics', [])
                
                # 3. Timeline de eventos
                print("⏱️ Coletando timeline...")
                timeline = await self.fetch_api_data(page, f"{self.base_url}event/{match_id}/incidents")
                if timeline:
                    match_data['timeline'] = timeline.get('incidents', [])
                
                # 4. Lineups e formações
                print("👥 Coletando escalações...")
                lineups = await self.fetch_api_data(page, f"{self.base_url}event/{match_id}/lineups")
                if lineups:
                    match_data['lineups'] = {
                        'home': lineups.get('home', {}),
                        'away': lineups.get('away', {})
                    }
                
                # 5. Heatmap removido (não necessário para o assistente técnico)
                
                # 6. Shotmap (mapa de chutes)
                print("🎯 Coletando shotmap...")
                shotmap = await self.fetch_api_data(page, f"{self.base_url}event/{match_id}/shotmap")
                if shotmap:
                    match_data['shotmap'] = shotmap.get('shotmap', [])
                
                # 7. Estatísticas dos jogadores
                print("⚽ Coletando stats dos jogadores...")
                player_stats = await self.fetch_api_data(page, f"{self.base_url}event/{match_id}/player-statistics")
                if player_stats:
                    match_data['player_statistics'] = player_stats
                
                # 8. Dados de momentum/pressão (gráfico)
                print("📊 Coletando momentum...")
                momentum_endpoints = [
                    f"{self.base_url}event/{match_id}/graph",  # URL correta sugerida
                    f"{self.base_url}event/{match_id}/momentum",  # fallback
                    f"{self.base_url}event/{match_id}/graph/momentum"  # alternativa
                ]
                
                momentum = None
                for endpoint in momentum_endpoints:
                    print(f"   🔄 Tentando: {endpoint}")
                    momentum = await self.fetch_api_data(page, endpoint)
                    if momentum:
                        print(f"   ✅ Momentum encontrado em: {endpoint}")
                        # Extrair apenas dados de momentum se existirem
                        if isinstance(momentum, dict) and 'momentum' in momentum:
                            match_data['momentum'] = momentum['momentum']
                        else:
                            match_data['momentum'] = momentum
                        break
                
                if not momentum:
                    print("   ⚠️ Momentum não disponível (normal para ligas menores)")
                
                # 9. Passes dos jogadores
                print("🎯 Coletando passes...")
                passes = await self.fetch_api_data(page, f"{self.base_url}event/{match_id}/passes")
                if passes:
                    match_data['passes'] = passes
                
                # 10. Dados de posicionamento tático
                print("🗺️ Coletando posicionamento...")
                positions = await self.fetch_api_data(page, f"{self.base_url}event/{match_id}/average-positions")
                if positions:
                    match_data['average_positions'] = positions
                
                # Adicionar metadados
                match_data['metadata'] = {
                    'collected_at': timestamp,
                    'match_id': match_id,
                    'collector_version': '1.0'
                }
                
                # Salvar dados com timestamp
                filename = f"match_{match_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                filepath = self.data_dir / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(match_data, f, indent=2, ensure_ascii=False)
                
                print(f"💾 Dados salvos em: {filepath.absolute()}")
                print(f"📊 Coletados {len([k for k, v in match_data.items() if v and k != 'metadata'])} tipos de dados")
                
                return match_data
                
            except Exception as e:
                print(f"❌ Erro geral na coleta: {e}")
                return None
                
            finally:
                await browser.close()
    
    async def collect_live_data_loop(self, match_id, interval_seconds=30, max_iterations=None):
        """Coleta dados em loop para simular tempo real"""
        iteration = 0
        
        print(f"🚀 Iniciando coleta em tempo real para partida {match_id}")
        print(f"⏰ Intervalo: {interval_seconds} segundos")
        if max_iterations:
            print(f"🔄 Máximo de iterações: {max_iterations}")
        print("=" * 60)
        
        while True:
            iteration += 1
            print(f"\n🔄 Iteração #{iteration} - {datetime.now().strftime('%H:%M:%S')}")
            
            # Coletar dados
            data = await self.get_live_match_data(match_id)
            
            if data:
                print("✅ Dados coletados com sucesso!")
            else:
                print("❌ Falha na coleta")
            
            # Verificar se deve parar
            if max_iterations and iteration >= max_iterations:
                print(f"\n🏁 Concluído! {iteration} iterações realizadas")
                break
            
            # Aguardar próxima coleta
            print(f"⏳ Aguardando {interval_seconds} segundos...")
            await asyncio.sleep(interval_seconds)

async def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("❌ Uso: python get_game_info.py <match_id> [interval_seconds] [max_iterations]")
        print("📝 Exemplo: python get_game_info.py 11161648")
        print("📝 Exemplo com intervalo: python get_game_info.py 11161648 15")
        print("📝 Exemplo com limite: python get_game_info.py 11161648 30 20")
        return
    
    match_id = sys.argv[1]
    interval_seconds = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    max_iterations = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    collector = SofaScoreLiveCollector()
    
    if max_iterations == 1:
        # Coleta única
        await collector.get_live_match_data(match_id)
    else:
        # Coleta em loop
        await collector.collect_live_data_loop(match_id, interval_seconds, max_iterations)

if __name__ == "__main__":
    asyncio.run(main())
