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
        """Cria contexto do navegador otimizado baseado nos testes bem-sucedidos"""
        print(f"🔧 Configurando navegador com configurações otimizadas...")
        
        # Argumentos otimizados baseados no teste que funcionou 100%
        browser_args = [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-extensions',
            '--disable-blink-features=AutomationControlled',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-field-trial-config',
            '--disable-ipc-flooding-protection',
            '--no-first-run',
            '--no-default-browser-check',
            '--no-pings',
            '--password-store=basic',
            '--use-mock-keychain'
        ]
        
        print(f"🚀 Iniciando navegador Chromium com {len(browser_args)} argumentos anti-detecção...")
        
        try:
            browser = await playwright.chromium.launch(
                headless=True,
                args=browser_args,
                # Configurações otimizadas baseadas no teste
                slow_mo=100,  # Reduzido para 100ms (era 500ms)
                timeout=30000  # Reduzido para 30s (era 60s)
            )
            
            print(f"✅ Navegador iniciado com sucesso")
            
            # Configurações do contexto otimizadas baseadas no teste bem-sucedido
            context_options = {
                'viewport': {'width': 1920, 'height': 1080},
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'extra_http_headers': {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache',
                    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': '"Windows"',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Upgrade-Insecure-Requests': '1'
                },
                'ignore_https_errors': True,
                'java_script_enabled': True
            }
            
            print(f"🌐 Criando contexto do navegador...")
            context = await browser.new_context(**context_options)
            
            # Configurar timeouts otimizados
            context.set_default_timeout(30000)  # 30 segundos
            context.set_default_navigation_timeout(30000)  # 30 segundos
            
            # Adicionar scripts para mascarar automação (baseados no teste bem-sucedido)
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['pt-BR', 'pt', 'en'],
                });
                window.chrome = {
                    runtime: {}
                };
            """)
            
            print(f"✅ Contexto criado com configurações anti-detecção")
            
            return browser, context
            
        except Exception as e:
            error_type = type(e).__name__
            print(f"❌ Erro ao criar contexto do navegador: {error_type} - {str(e)}")
            print(f"🔍 Possíveis soluções:")
            print(f"   - Verificar se chromium está instalado: playwright install chromium")
            print(f"   - Verificar memória disponível (Docker needs at least 2GB)")
            print(f"   - Verificar se SHM está configurado no docker-compose (shm_size: 2gb)")
            raise e

    async def fetch_api_data(self, page, endpoint):
        """Função auxiliar otimizada para buscar dados de API endpoint"""
        endpoint_name = endpoint.split('/')[-1] or endpoint.split('/')[-2]
        
        try:
            print(f"🔗 Acessando endpoint: {endpoint}")
            
            # Configurar retry otimizado (baseado no teste que funcionou)
            max_retries = 2  # Reduzido de 3 para 2
            for attempt in range(max_retries):
                try:
                    print(f"🚀 Tentativa {attempt + 1}/{max_retries} - {endpoint_name}")
                    
                    response = await page.goto(
                        endpoint, 
                        wait_until='domcontentloaded',  # Comprovadamente mais rápido
                        timeout=20000  # Reduzido de 30s para 20s baseado no teste
                    )
                    
                    print(f"📡 Resposta recebida - Status: {response.status}, URL: {response.url}")
                    
                    if response.status == 200:
                        content = await page.content()
                        content_length = len(content)
                        print(f"📄 Conteúdo recebido - Tamanho: {content_length} caracteres")
                        
                        json_start = content.find('{')
                        json_end = content.rfind('}') + 1
                        
                        if json_start != -1 and json_end > json_start:
                            json_content = content[json_start:json_end]
                            json_data = json.loads(json_content)
                            print(f"✅ JSON válido extraído - {endpoint_name} - Chaves: {list(json_data.keys())[:5]}")
                            return json_data
                        else:
                            print(f"⚠️ Não foi possível extrair JSON válido do conteúdo - {endpoint_name}")
                            print(f"📋 Primeiros 200 caracteres: {content[:200]}")
                    else:
                        print(f"❌ Status HTTP inválido: {response.status} - {endpoint_name}")
                        print(f"📝 Headers da resposta: {dict(response.headers)}")
                    
                    if attempt < max_retries - 1:
                        print(f"⚠️ Tentativa {attempt + 1} falhou para {endpoint_name}, tentando novamente em 1s...")
                        await asyncio.sleep(1)  # Reduzido de 2s para 1s baseado no teste
                    
                except Exception as retry_error:
                    error_type = type(retry_error).__name__
                    print(f"❌ Erro na tentativa {attempt + 1} para {endpoint_name}: {error_type} - {str(retry_error)}")
                    
                    if attempt < max_retries - 1:
                        print(f"🔄 Reentando em 1s... ({attempt + 2}/{max_retries})")
                        await asyncio.sleep(1)
                    else:
                        print(f"💥 Todas as tentativas falharam para {endpoint_name}")
                        raise retry_error
            
            print(f"❌ Falha definitiva em todas as tentativas para {endpoint_name}")
            return None
            
        except Exception as e:
            error_type = type(e).__name__
            print(f"❌ Erro crítico ao buscar {endpoint_name}: {error_type} - {str(e)}")
            return None
    
    async def get_live_match_data_api(self, match_id: str) -> Optional[Dict[str, Any]]:
        """Versão adaptada para API que retorna apenas os dados sem salvar arquivos"""
        try:
            from playwright.async_api import async_playwright
        except ImportError as e:
            print(f"❌ Playwright não está instalado: {e}")
            return None
        
        # Verificar e instalar navegadores se necessário
        # await self.ensure_playwright_browsers()  # Comentado temporariamente devido a conflito sync/async
        
        # Verificar e exibir informações do event loop
        import platform
        loop = asyncio.get_running_loop()
        print(f"🔧 Sistema: {platform.system()}")
        print(f"🔧 Event Loop: {type(loop).__name__}")
        print(f"🔧 Event Loop Policy: {type(asyncio.get_event_loop_policy()).__name__}")
        print(f"🔧 Match ID: {match_id}")
        print(f"🔧 Base URL: {self.base_url}")
        
        try:
            print(f"🚀 Iniciando Playwright para coleta de dados...")
            async with async_playwright() as playwright:
                print(f"📱 Criando contexto do navegador...")
                browser, context = await self.create_browser_context(playwright)
                page = await context.new_page()
                
                try:
                    # Obter versão do navegador de forma segura
                    browser_version = "Unknown"
                    try:
                        browser_version = await browser.version()
                        print(f"📊 Navegador iniciado - Versão: {browser_version}")
                    except Exception as e:
                        print(f"📊 Navegador iniciado - Versão não disponível ({str(e)})")
                    
                    # Obter User Agent de forma segura  
                    try:
                        user_agent = await page.evaluate('() => navigator.userAgent')
                        print(f"🌍 User Agent: {user_agent[:100]}...")
                    except Exception as e:
                        print(f"🌍 User Agent: Não disponível ({str(e)})")
                    
                except Exception as e:
                    print(f"⚠️ Erro ao obter informações do navegador: {str(e)}")
                
                try:
                    print(f"🔄 Coletando dados da partida {match_id}...")
                    print(f"🎯 Usando estratégia otimizada baseada no teste bem-sucedido")
                    
                    match_data = {}
                    timestamp = datetime.now().isoformat()
                    collected_types = []
                    
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
                        collected_types.append("basic_info")
                        home_team = basic_info.get('event', {}).get('homeTeam', {}).get('name', 'N/A')
                        away_team = basic_info.get('event', {}).get('awayTeam', {}).get('name', 'N/A')
                        print(f"⚽ Partida identificada: {home_team} vs {away_team}")
                    else:
                        print("❌ Falha ao obter informações básicas - dados podem estar indisponíveis")
                    
                    # 2. Estatísticas
                    print("📈 Coletando estatísticas...")
                    stats = await self.fetch_api_data(page, f"{self.base_url}event/{match_id}/statistics")
                    if stats:
                        match_data['statistics'] = stats.get('statistics', [])
                        collected_types.append("statistics")
                        print(f"📊 Estatísticas coletadas: {len(match_data['statistics'])} categorias")
                    else:
                        print("❌ Falha ao obter estatísticas")
                    
                    # 3. Timeline
                    print("⏱️ Coletando timeline...")
                    timeline = await self.fetch_api_data(page, f"{self.base_url}event/{match_id}/incidents")
                    if timeline:
                        match_data['timeline'] = timeline.get('incidents', [])
                        collected_types.append("timeline")
                        print(f"📅 Timeline coletada: {len(match_data['timeline'])} eventos")
                    else:
                        print("❌ Falha ao obter timeline")
                    
                    # 4. Lineups
                    print("👥 Coletando escalações...")
                    lineups = await self.fetch_api_data(page, f"{self.base_url}event/{match_id}/lineups")
                    if lineups:
                        match_data['lineups'] = {
                            'home': lineups.get('home', {}),
                            'away': lineups.get('away', {})
                        }
                        collected_types.append("lineups")
                        home_players = len(lineups.get('home', {}).get('players', []))
                        away_players = len(lineups.get('away', {}).get('players', []))
                        print(f"👥 Escalações coletadas: {home_players} jogadores casa, {away_players} jogadores visitante")
                    else:
                        print("❌ Falha ao obter escalações")
                    
                    # 5. Shotmap
                    print("🎯 Coletando shotmap...")
                    shotmap = await self.fetch_api_data(page, f"{self.base_url}event/{match_id}/shotmap")
                    if shotmap:
                        match_data['shotmap'] = shotmap.get('shotmap', [])
                        collected_types.append("shotmap")
                        print(f"🎯 Shotmap coletado: {len(match_data['shotmap'])} chutes")
                    else:
                        print("❌ Falha ao obter shotmap")
                    
                    # 6. Player statistics
                    print("⚽ Coletando stats dos jogadores...")
                    player_stats = await self.fetch_api_data(page, f"{self.base_url}event/{match_id}/player-statistics")
                    if player_stats:
                        match_data['player_statistics'] = player_stats
                        collected_types.append("player_statistics")
                        print(f"⚽ Stats dos jogadores coletadas")
                    else:
                        print("❌ Falha ao obter stats dos jogadores")
                    
                    # Adicionar metadados
                    match_data['metadata'] = {
                        'collected_at': timestamp,
                        'match_id': match_id,
                        'collector_version': '2.0-api',
                        'collected_types': collected_types,
                        'total_types': len(collected_types)
                    }
                    
                    print(f"✅ Dados coletados: {len(collected_types)} tipos ({', '.join(collected_types)})")
                    
                    if len(collected_types) == 0:
                        print("⚠️ ATENÇÃO: Nenhum dado foi coletado com sucesso!")
                        print("🔍 Possíveis causas:")
                        print("   - Match ID inválido ou partida não encontrada")
                        print("   - Bloqueio temporário do SofaScore")
                        print("   - Problemas de conectividade")
                        print("🎯 Recomendação: Aguardar alguns minutos e tentar novamente")
                    elif len(collected_types) < 6:
                        print(f"⚠️ Coleta parcial: {len(collected_types)}/6 tipos de dados coletados")
                        print("🎯 Alguns dados podem estar temporariamente indisponíveis")
                    
                    return match_data
                    
                except Exception as e:
                    error_type = type(e).__name__
                    print(f"❌ Erro na coleta: {error_type} - {str(e)}")
                    print(f"🔍 Detalhes do erro:")
                    print(f"   - Tipo: {error_type}")
                    print(f"   - Mensagem: {str(e)}")
                    return None
                    
                finally:
                    print(f"🔒 Fechando navegador...")
                    await browser.close()
        
        except Exception as e:
            error_type = type(e).__name__
            print(f"❌ Erro crítico do Playwright: {error_type} - {str(e)}")
            print(f"🔍 Possíveis soluções:")
            print(f"   - Verificar se o Playwright está instalado corretamente")
            print(f"   - Executar: playwright install chromium")
            print(f"   - Verificar permissões do sistema")
            print(f"   - Verificar recursos disponíveis (memória/CPU)")
            return None

    async def ensure_playwright_browsers(self):
        """Verifica e instala navegadores do Playwright se necessário"""
        try:
            from playwright.async_api import async_playwright
            
            print(f"🔍 Verificando instalação dos navegadores do Playwright...")
            
            try:
                # Usar API async em vez da sync
                async with async_playwright() as p:
                    try:
                        # Tentar obter o caminho do executável do Chromium
                        chromium_path = p.chromium.executable_path
                        print(f"✅ Chromium encontrado em: {chromium_path}")
                        
                        # Verificar se o arquivo existe
                        import os
                        if os.path.exists(chromium_path):
                            print(f"✅ Chromium executável verificado com sucesso")
                            return True
                        else:
                            print(f"❌ Chromium executável não encontrado em: {chromium_path}")
                            
                    except Exception as e:
                        print(f"❌ Erro ao verificar Chromium: {str(e)}")
                        
            except Exception as e:
                print(f"❌ Erro ao inicializar Playwright para verificação: {str(e)}")
            
            # Se chegou aqui, os navegadores podem não estar instalados ou funcionando
            print(f"🔄 Tentando instalar navegadores do Playwright automaticamente...")
            
            import subprocess
            import sys
            
            try:
                # Tentar instalar chromium
                result = subprocess.run([
                    sys.executable, '-m', 'playwright', 'install', 'chromium'
                ], capture_output=True, text=True, timeout=300)  # 5 minutos timeout
                
                if result.returncode == 0:
                    print(f"✅ Chromium instalado com sucesso!")
                    
                    # Tentar instalar dependências do sistema
                    dep_result = subprocess.run([
                        sys.executable, '-m', 'playwright', 'install-deps', 'chromium'
                    ], capture_output=True, text=True, timeout=180)  # 3 minutos timeout
                    
                    if dep_result.returncode == 0:
                        print(f"✅ Dependências do Chromium instaladas com sucesso!")
                    else:
                        print(f"⚠️ Aviso: Algumas dependências podem não ter sido instaladas")
                        print(f"Saída: {dep_result.stdout}")
                        print(f"Erro: {dep_result.stderr}")
                    
                    return True
                else:
                    print(f"❌ Falha ao instalar Chromium")
                    print(f"Saída: {result.stdout}")
                    print(f"Erro: {result.stderr}")
                    return False
                    
            except subprocess.TimeoutExpired:
                print(f"❌ Timeout na instalação do Chromium")
                return False
            except Exception as e:
                print(f"❌ Erro na instalação automática: {str(e)}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao verificar/instalar navegadores: {str(e)}")
            return False

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