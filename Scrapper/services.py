"""
Serviços de Coleta e Análise de Dados
Adaptação dos scripts existentes para uso em API
"""

import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

# Importar classes existentes
from important_scripts.get_game_info import SofaScoreLiveCollector
from important_scripts.simplify_match_data import MatchDataSimplifier
# from important_scripts.agent_assitant import TechnicalAssistant
from database_service import DatabaseService

# Importar TechnicalAssistant com tratamento especial devido ao nome do arquivo
try:
    import importlib.util
    from pathlib import Path
    current_dir = Path(__file__).parent
    agent_path = current_dir / "important_scripts" / "agent-assitant.py"
    spec = importlib.util.spec_from_file_location("technical_assistant", agent_path)
    technical_assistant_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(technical_assistant_module)
    TechnicalAssistant = technical_assistant_module.TechnicalAssistant
except Exception as e:
    print(f"⚠️ Erro ao importar TechnicalAssistant: {e}")
    TechnicalAssistant = None

class MatchDataService:
    """Serviço principal para coleta e processamento de dados de partidas"""
    
    def __init__(self):
        self.database = DatabaseService()
        self.simplifier = MatchDataSimplifierAPI()
        
        # Inicializar assistente técnico se disponível
        self.assistant = None
        if TechnicalAssistant:
            try:
                self.assistant = TechnicalAssistant()
                print("🤖 Assistente técnico inicializado!")
            except Exception as e:
                print(f"⚠️ Assistente técnico não disponível: {e}")
        else:
            print("⚠️ TechnicalAssistant não foi importado corretamente")
    
    async def get_full_match_data(self, match_id: str) -> Dict[str, Any]:
        """Coleta dados completos da partida do SofaScore"""
        try:
            print(f"🔄 Coletando dados completos para partida {match_id}")
            
            # Usar o coletor existente adaptado
            collector = SofaScoreLiveCollectorAPI()
            match_data = await collector.get_live_match_data_api(match_id)
            
            if not match_data:
                raise Exception("Falha na coleta de dados do SofaScore")
            
            # Salvar no banco de dados
            record_id = await self.database.save_match_data(
                match_id=match_id,
                full_data=match_data
            )
            
            return {
                "success": True,
                "message": "Dados coletados com sucesso",
                "data": match_data,
                "record_id": record_id,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro na coleta de dados: {str(e)}",
                "data": None,
                "record_id": None,
                "timestamp": datetime.now()
            }
    
    async def get_simplified_match_data(self, match_id: str) -> Dict[str, Any]:
        """Coleta e simplifica dados da partida"""
        try:
            print(f"🔄 Coletando e simplificando dados para partida {match_id}")
            
            # Coletar dados completos
            collector = SofaScoreLiveCollectorAPI()
            full_data = await collector.get_live_match_data_api(match_id)
            
            if not full_data:
                raise Exception("Falha na coleta de dados do SofaScore")
            
            # Simplificar dados
            simplified_data = self.simplifier.simplify_raw_data(full_data)
            
            if not simplified_data:
                raise Exception("Falha na simplificação dos dados")
            
            # Salvar no banco
            record_id = await self.database.save_match_data(
                match_id=match_id,
                full_data=full_data,
                simplified_data=simplified_data
            )
            
            return {
                "success": True,
                "message": "Dados simplificados com sucesso",
                "data": simplified_data,
                "record_id": record_id,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro na simplificação: {str(e)}",
                "data": None,
                "record_id": None,
                "timestamp": datetime.now()
            }
    
    async def get_match_analysis(self, match_id: str) -> Dict[str, Any]:
        """Coleta dados, simplifica e gera análise técnica"""
        try:
            print(f"🔄 Iniciando análise completa para partida {match_id}")
            
            if not self.assistant:
                raise Exception("Assistente técnico não disponível - configure OPENAI_API_KEY")
            
            # Coletar dados completos
            collector = SofaScoreLiveCollectorAPI()
            full_data = await collector.get_live_match_data_api(match_id)
            
            if not full_data:
                raise Exception("Falha na coleta de dados do SofaScore")
            
            # Simplificar dados
            simplified_data = self.simplifier.simplify_raw_data(full_data)
            
            if not simplified_data:
                raise Exception("Falha na simplificação dos dados")
            
            # Gerar análise técnica
            analysis = self.assistant.analyze_match(simplified_data)
            
            if not analysis:
                raise Exception("Falha na geração da análise técnica")
            
            # Salvar tudo no banco
            record_id = await self.database.save_match_data(
                match_id=match_id,
                full_data=full_data,
                simplified_data=simplified_data,
                analysis=analysis
            )
            
            return {
                "success": True,
                "message": "Análise completa realizada com sucesso",
                "match_data": full_data,
                "simplified_data": simplified_data,
                "analysis": analysis,
                "record_id": record_id,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro na análise: {str(e)}",
                "match_data": None,
                "simplified_data": None,
                "analysis": None,
                "record_id": None,
                "timestamp": datetime.now()
            }

class SofaScoreLiveCollectorAPI(SofaScoreLiveCollector):
    """Versão adaptada do coletor para uso em API"""
    
    def __init__(self):
        super().__init__()
        # Remover inicialização do assistente para evitar conflitos
        self.assistant = None
    
    async def create_browser_context(self, playwright):
        """Cria contexto do navegador com configurações otimizadas para Docker"""
        try:
            print("🚀 Iniciando browser Chromium...")
            browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-extensions',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--single-process',
                    '--no-zygote',
                    '--disable-default-apps',
                    '--disable-sync',
                    '--disable-translate',
                    '--hide-scrollbars',
                    '--mute-audio',
                    '--disable-background-networking',
                    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            )
            print("✅ Browser Chromium iniciado com sucesso!")
            
            print("🌐 Criando contexto do browser...")
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
            print("✅ Contexto do browser criado com sucesso!")
            
            return browser, context
            
        except Exception as e:
            print(f"❌ Erro ao criar browser/contexto: {type(e).__name__}: {e}")
            import traceback
            print(f"🔍 Stack trace: {traceback.format_exc()}")
            raise e

    async def fetch_api_data(self, page, endpoint):
        """Função auxiliar para buscar dados de uma API endpoint com tratamento melhorado"""
        try:
            print(f"🔗 Acessando endpoint: {endpoint}")
            
            # Configurar timeout maior e retry
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    print(f"🚀 Tentativa {attempt + 1}/{max_retries} para: {endpoint}")
                    
                    response = await page.goto(
                        endpoint, 
                        wait_until='domcontentloaded',  # Mais rápido que networkidle para Docker
                        timeout=30000
                    )
                    
                    print(f"📡 Resposta recebida - Status: {response.status}")
                    
                    if response.status == 200:
                        print("✅ Status 200 - obtendo conteúdo...")
                        content = await page.content()
                        print(f"📄 Tamanho do conteúdo: {len(content)} caracteres")
                        
                        json_start = content.find('{')
                        json_end = content.rfind('}') + 1
                        
                        if json_start != -1 and json_end > json_start:
                            json_content = content[json_start:json_end]
                            print(f"🔍 JSON extraído - tamanho: {len(json_content)} caracteres")
                            try:
                                data = json.loads(json_content)
                                print(f"✅ JSON parseado com sucesso - chaves: {list(data.keys()) if isinstance(data, dict) else 'não é dict'}")
                                return data
                            except json.JSONDecodeError as je:
                                print(f"❌ Erro ao fazer parse do JSON: {je}")
                                print(f"🔍 Primeira parte do conteúdo: {json_content[:200]}...")
                        else:
                            print("❌ Não foi possível encontrar JSON válido no conteúdo")
                            print(f"🔍 Primeira parte do conteúdo HTML: {content[:500]}...")
                    else:
                        print(f"❌ Status HTTP não é 200: {response.status}")
                        print(f"🔍 Headers da resposta: {response.headers}")
                    
                    if attempt < max_retries - 1:
                        print(f"⚠️ Tentativa {attempt + 1} falhou (Status: {response.status}), tentando novamente...")
                        await asyncio.sleep(2)  # Aguardar antes de tentar novamente
                    
                except Exception as e:
                    print(f"❌ Exceção na tentativa {attempt + 1}: {type(e).__name__}: {e}")
                    if attempt < max_retries - 1:
                        print(f"⚠️ Erro na tentativa {attempt + 1}: {e}, tentando novamente...")
                        await asyncio.sleep(2)
                    else:
                        print(f"💥 Todas as tentativas falharam para: {endpoint}")
                        raise e
            
            print(f"❌ Todas as tentativas esgotadas para: {endpoint}")
            return None
        except Exception as e:
            print(f"⚠️ Erro crítico ao buscar {endpoint}: {type(e).__name__}: {e}")
            import traceback
            print(f"🔍 Stack trace: {traceback.format_exc()}")
            return None
    
    async def get_live_match_data_api(self, match_id: str) -> Optional[Dict[str, Any]]:
        """Versão adaptada para API que retorna apenas os dados sem salvar arquivos"""
        try:
            from playwright.async_api import async_playwright
            print("✅ Playwright importado com sucesso!")
        except ImportError as e:
            print(f"❌ Playwright não está instalado: {e}")
            return None
        
        # Verificar e exibir informações do event loop e sistema
        import platform
        import os
        loop = asyncio.get_running_loop()
        print(f"🔧 Sistema: {platform.system()}")
        print(f"🔧 Arquitetura: {platform.machine()}")
        print(f"🔧 Python: {platform.python_version()}")
        print(f"🔧 Event Loop: {type(loop).__name__}")
        print(f"🔧 Event Loop Policy: {type(asyncio.get_event_loop_policy()).__name__}")
        print(f"🔧 PLAYWRIGHT_BROWSERS_PATH: {os.getenv('PLAYWRIGHT_BROWSERS_PATH', 'Não definido')}")
        print(f"🔧 USER: {os.getenv('USER', 'Não definido')}")
        
        # Verificar se o Chromium está disponível
        try:
            import subprocess
            result = subprocess.run(['which', 'chromium'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ Chromium encontrado em: {result.stdout.strip()}")
            else:
                print("⚠️ Chromium não encontrado no PATH")
        except Exception as e:
            print(f"⚠️ Erro ao verificar Chromium: {e}")
        
        try:
            print("🎭 Iniciando Playwright...")
            async with async_playwright() as playwright:
                print("🎭 Playwright iniciado com sucesso!")
                print("🔍 Verificando navegadores disponíveis...")
                print(f"🌐 Chromium disponível: {playwright.chromium}")
                
                print("🎭 Criando browser e contexto...")
                browser, context = await self.create_browser_context(playwright)
                print("📄 Criando nova página...")
                page = await context.new_page()
                print("✅ Página criada com sucesso!")
                
                try:
                    print(f"🔄 Coletando dados da partida {match_id}...")
                    print(f"🌐 Base URL configurada: {self.base_url}")
                    
                    match_data = {}
                    timestamp = datetime.now().isoformat()
                    
                    # 1. Informações básicas
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
                    
                    # 2. Estatísticas
                    print("📈 Coletando estatísticas...")
                    stats = await self.fetch_api_data(page, f"{self.base_url}event/{match_id}/statistics")
                    if stats:
                        match_data['statistics'] = stats.get('statistics', [])
                    
                    # 3. Timeline
                    print("⏱️ Coletando timeline...")
                    timeline = await self.fetch_api_data(page, f"{self.base_url}event/{match_id}/incidents")
                    if timeline:
                        match_data['timeline'] = timeline.get('incidents', [])
                    
                    # 4. Lineups
                    print("👥 Coletando escalações...")
                    lineups = await self.fetch_api_data(page, f"{self.base_url}event/{match_id}/lineups")
                    if lineups:
                        match_data['lineups'] = {
                            'home': lineups.get('home', {}),
                            'away': lineups.get('away', {})
                        }
                    
                    # 5. Shotmap
                    print("🎯 Coletando shotmap...")
                    shotmap = await self.fetch_api_data(page, f"{self.base_url}event/{match_id}/shotmap")
                    if shotmap:
                        match_data['shotmap'] = shotmap.get('shotmap', [])
                    
                    # 6. Player statistics
                    print("⚽ Coletando stats dos jogadores...")
                    player_stats = await self.fetch_api_data(page, f"{self.base_url}event/{match_id}/player-statistics")
                    if player_stats:
                        match_data['player_statistics'] = player_stats
                    
                    # Adicionar metadados
                    match_data['metadata'] = {
                        'collected_at': timestamp,
                        'match_id': match_id,
                        'collector_version': '2.0-api'
                    }
                    
                    print(f"✅ Dados coletados: {len([k for k, v in match_data.items() if v and k != 'metadata'])} tipos")
                    return match_data
                    
                except Exception as e:
                    print(f"❌ Erro na coleta: {e}")
                    return None
                    
                finally:
                    await browser.close()
        
        except Exception as e:
            print(f"❌ Erro crítico do Playwright: {e}")
            return None

# Adaptar o simplificador para trabalhar com dados em memória
class MatchDataSimplifierAPI(MatchDataSimplifier):
    """Versão adaptada do simplificador para uso em API"""
    
    def simplify_raw_data(self, raw_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Simplifica dados em memória sem usar arquivos"""
        try:
            # Extrair informações básicas
            basic_info = raw_data.get("basic_info", {})
            
            simplified_data = {
                "match_summary": {
                    "home_team": basic_info.get("homeTeam", {}).get("name", ""),
                    "away_team": basic_info.get("awayTeam", {}).get("name", ""),
                    "score": {
                        "home": basic_info.get("homeScore", {}).get("current", 0),
                        "away": basic_info.get("awayScore", {}).get("current", 0)
                    },
                    "status": basic_info.get("status", {}).get("description", ""),
                    "tournament": basic_info.get("tournament", {}).get("name", ""),
                    "managers": {
                        "home": basic_info.get("homeTeam", {}).get("manager", {}).get("name", ""),
                        "away": basic_info.get("awayTeam", {}).get("manager", {}).get("name", "")
                    }
                },
                
                "key_statistics": self.extract_key_statistics(raw_data.get("statistics", [])),
                
                "events_timeline": self.extract_goals_and_events(raw_data.get("timeline", [])),
                
                "tactical_setup": self.extract_formations_and_lineups(raw_data.get("lineups", {})),
                
                "shooting_analysis": self.extract_shot_analysis(raw_data.get("shotmap", [])),
                
                "collection_info": {
                    "collected_at": raw_data.get("metadata", {}).get("collected_at", ""),
                    "match_id": raw_data.get("metadata", {}).get("match_id", "")
                }
            }
            
            return simplified_data
            
        except Exception as e:
            print(f"❌ Erro na simplificação: {e}")
            return None 