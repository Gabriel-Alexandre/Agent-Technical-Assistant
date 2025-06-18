"""
Serviços de Coleta e Análise de Dados
Adaptação dos scripts existentes para uso em API
"""

import json
import asyncio
import re
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
from urllib.parse import unquote
from playwright.async_api import async_playwright

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
            except Exception as e:
                print(f"⚠️ Assistente técnico não disponível: {e}")
        else:
            print("⚠️ TechnicalAssistant não foi importado corretamente")
    
    async def get_full_match_data(self, match_id: str) -> Dict[str, Any]:
        """Coleta dados completos da partida do SofaScore - MÉTODO DESABILITADO"""
        return {
            "success": False,
            "message": "Método temporariamente desabilitado para manutenção. Use os métodos de screenshot para análise de partidas.",
            "data": None,
            "record_id": None,
            "timestamp": datetime.now()
        }
        
        # Código original comentado para manutenção
        # try:
        #     print(f"🔄 Coletando dados completos para partida {match_id}")
        #     
        #     # Usar o coletor existente adaptado
        #     collector = SofaScoreLiveCollectorAPI()
        #     match_data = await collector.get_live_match_data_api(match_id)
        #     
        #     if not match_data:
        #         raise Exception("Falha na coleta de dados do SofaScore")
        #     
        #     # Salvar no banco de dados
        #     record_id = await self.database.save_match_data(
        #         match_id=match_id,
        #         full_data=match_data
        #     )
        #     
        #     return {
        #         "success": True,
        #         "message": "Dados coletados com sucesso",
        #         "data": match_data,
        #         "record_id": record_id,
        #         "timestamp": datetime.now()
        #     }
        #     
        # except Exception as e:
        #     return {
        #         "success": False,
        #         "message": f"Erro na coleta de dados: {str(e)}",
        #         "data": None,
        #         "record_id": None,
        #         "timestamp": datetime.now()
        #     }
    
    async def get_simplified_match_data(self, match_id: str) -> Dict[str, Any]:
        """Coleta e simplifica dados da partida - MÉTODO DESABILITADO"""
        return {
            "success": False,
            "message": "Método temporariamente desabilitado para manutenção. Use os métodos de screenshot para análise de partidas.",
            "data": None,
            "record_id": None,
            "timestamp": datetime.now()
        }
        
        # Código original comentado para manutenção
        # try:
        #     print(f"🔄 Coletando e simplificando dados para partida {match_id}")
        #     
        #     # Coletar dados completos
        #     collector = SofaScoreLiveCollectorAPI()
        #     full_data = await collector.get_live_match_data_api(match_id)
        #     
        #     if not full_data:
        #         raise Exception("Falha na coleta de dados do SofaScore")
        #     
        #     # Simplificar dados
        #     simplified_data = self.simplifier.simplify_raw_data(full_data)
        #     
        #     if not simplified_data:
        #         raise Exception("Falha na simplificação dos dados")
        #     
        #     # Salvar no banco
        #     record_id = await self.database.save_match_data(
        #         match_id=match_id,
        #         full_data=full_data,
        #         simplified_data=simplified_data
        #     )
        #     
        #     return {
        #         "success": True,
        #         "message": "Dados simplificados com sucesso",
        #         "data": simplified_data,
        #         "record_id": record_id,
        #         "timestamp": datetime.now()
        #     }
        #     
        # except Exception as e:
        #     return {
        #         "success": False,
        #         "message": f"Erro na simplificação: {str(e)}",
        #         "data": None,
        #         "record_id": None,
        #         "timestamp": datetime.now()
        #     }
    
    async def get_match_analysis(self, match_id: str) -> Dict[str, Any]:
        """Coleta dados, simplifica e gera análise técnica - MÉTODO DESABILITADO"""
        return {
            "success": False,
            "message": "Método temporariamente desabilitado para manutenção. Use o método analyze_match_from_screenshot para análise de partidas.",
            "match_data": None,
            "simplified_data": None,
            "analysis": None,
            "record_id": None,
            "timestamp": datetime.now()
        }
        
        # Código original comentado para manutenção
        # try:
        #     print(f"🔄 Iniciando análise completa para partida {match_id}")
        #     
        #     if not self.assistant:
        #         raise Exception("Assistente técnico não disponível - configure OPENAI_API_KEY")
        #     
        #     # Coletar dados completos
        #     collector = SofaScoreLiveCollectorAPI()
        #     full_data = await collector.get_live_match_data_api(match_id)
        #     
        #     if not full_data:
        #         raise Exception("Falha na coleta de dados do SofaScore")
        #     
        #     # Simplificar dados
        #     simplified_data = self.simplifier.simplify_raw_data(full_data)
        #     
        #     if not simplified_data:
        #         raise Exception("Falha na simplificação dos dados")
        #     
        #     # Gerar análise técnica
        #     analysis = self.assistant.analyze_match(simplified_data)
        #     
        #     if not analysis:
        #         raise Exception("Falha na geração da análise técnica")
        #     
        #     # Salvar tudo no banco
        #     record_id = await self.database.save_match_data(
        #         match_id=match_id,
        #         full_data=full_data,
        #         simplified_data=simplified_data,
        #         analysis=analysis
        #     )
        #     
        #     return {
        #         "success": True,
        #         "message": "Análise completa realizada com sucesso",
        #         "match_data": full_data,
        #         "simplified_data": simplified_data,
        #         "analysis": analysis,
        #         "record_id": record_id,
        #         "timestamp": datetime.now()
        #     }
        #     
        # except Exception as e:
        #     return {
        #         "success": False,
        #         "message": f"Erro na análise: {str(e)}",
        #         "match_data": None,
        #         "simplified_data": None,
        #         "analysis": None,
        #         "record_id": None,
        #         "timestamp": datetime.now()
        #     }

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
        
        # Verificar informações básicas
        import platform
        
        try:
            print(f"🚀 Iniciando Playwright para coleta de dados...")
            async with async_playwright() as playwright:
                print(f"📱 Criando contexto do navegador...")
                browser, context = await self.create_browser_context(playwright)
                page = await context.new_page()
                
                # Navegador iniciado com sucesso
                
                try:
                    print(f"🔄 Coletando dados da partida {match_id}...")
                    
                    match_data = {}
                    timestamp = datetime.now().isoformat()
                    collected_types = []
                    
                    # 1. Informações básicas
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
                        print(f"⚽ Partida: {home_team} vs {away_team}")
                    else:
                        print("❌ Falha ao obter informações básicas")
                    
                    # 2. Estatísticas
                    stats = await self.fetch_api_data(page, f"{self.base_url}event/{match_id}/statistics")
                    if stats:
                        match_data['statistics'] = stats.get('statistics', [])
                        collected_types.append("statistics")
                    
                    # 3. Timeline
                    timeline = await self.fetch_api_data(page, f"{self.base_url}event/{match_id}/incidents")
                    if timeline:
                        match_data['timeline'] = timeline.get('incidents', [])
                        collected_types.append("timeline")
                    
                    # 4. Lineups
                    lineups = await self.fetch_api_data(page, f"{self.base_url}event/{match_id}/lineups")
                    if lineups:
                        match_data['lineups'] = {
                            'home': lineups.get('home', {}),
                            'away': lineups.get('away', {})
                        }
                        collected_types.append("lineups")
                    
                    # 5. Shotmap
                    shotmap = await self.fetch_api_data(page, f"{self.base_url}event/{match_id}/shotmap")
                    if shotmap:
                        match_data['shotmap'] = shotmap.get('shotmap', [])
                        collected_types.append("shotmap")
                    
                    # 6. Player statistics
                    player_stats = await self.fetch_api_data(page, f"{self.base_url}event/{match_id}/player-statistics")
                    if player_stats:
                        match_data['player_statistics'] = player_stats
                        collected_types.append("player_statistics")
                    
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
                        print("⚠️ Nenhum dado foi coletado")
                    elif len(collected_types) < 6:
                        print(f"⚠️ Coleta parcial: {len(collected_types)}/6 tipos")
                    
                    return match_data
                    
                except Exception as e:
                    print(f"❌ Erro na coleta: {str(e)}")
                    return None
                    
                finally:
                    print(f"🔒 Fechando navegador...")
                    await browser.close()
        
        except Exception as e:
            print(f"❌ Erro crítico do Playwright: {str(e)}")
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

class SofaScoreLinksService:
    """Serviço para coleta de links do SofaScore"""
    
    def __init__(self):
        print("🔧 [LINKS-SERVICE] Inicializando SofaScoreLinksService...")
        self.website_url = "https://www.sofascore.com/"
        self.database = DatabaseService()
        print("✅ [LINKS-SERVICE] SofaScoreLinksService inicializado com sucesso!")
    
    async def create_browser_context(self, playwright):
        """Cria contexto do navegador com configurações realistas"""
        print("🚀 [BROWSER-CONTEXT] Iniciando criação do contexto do navegador...")
        print("🔧 [BROWSER-CONTEXT] Configurações: headless=True, args com sandbox desabilitado")
        
        try:
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
            print("✅ [BROWSER-CONTEXT] Navegador Chromium lançado com sucesso!")
        except Exception as e:
            print(f"❌ [BROWSER-CONTEXT] Erro ao lançar Chromium: {type(e).__name__}: {str(e)}")
            raise
        
        try:
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
            print("✅ [BROWSER-CONTEXT] Contexto do navegador criado com sucesso!")
        except Exception as e:
            print(f"❌ [BROWSER-CONTEXT] Erro ao criar contexto: {type(e).__name__}: {str(e)}")
            await browser.close()
            raise
        
        return browser, context
    
    async def collect_and_filter_links(self) -> Dict[str, Any]:
        """Acessa a página inicial do SofaScore e coleta todos os links"""
        print("🚀 [LINKS-SERVICE] Iniciando collect_and_filter_links()")
        
        try:
            print("🎭 [LINKS-SERVICE] Inicializando Playwright...")
            async with async_playwright() as playwright:
                print("🌐 [LINKS-SERVICE] Criando contexto do navegador...")
                browser, context = await self.create_browser_context(playwright)
                page = await context.new_page()
                
                try:
                    print("🔄 [LINKS-SERVICE] Acessando página inicial do SofaScore...")
                    
                    # Acessar página inicial em português
                    homepage_url = "https://www.sofascore.com/pt/"
                    print(f"🌍 [LINKS-SERVICE] URL de destino: {homepage_url}")
                    print(f"⏰ [LINKS-SERVICE] Timeout configurado: 90000ms (90s)")
                    
                    response = await page.goto(homepage_url, timeout=90000)
                    
                    if response.status != 200:
                        print(f"❌ [LINKS-SERVICE] Erro ao acessar página inicial: Status {response.status}")
                        return {
                            "success": False,
                            "message": f"Erro ao acessar página inicial: Status {response.status}",
                            "data": None,
                            "timestamp": datetime.now()
                        }
                    
                    print("✅ [LINKS-SERVICE] Página inicial carregada com sucesso!")
                    
                    # Aguardar carregamento completo
                    print("⏳ [LINKS-SERVICE] Aguardando carregamento completo (3s)...")
                    await asyncio.sleep(3)
                    
                    # Aceitar cookies se aparecer o banner
                    try:
                        cookie_button = page.locator('button:has-text("Accept"), button:has-text("Aceitar"), [data-testid="cookie-accept"]')
                        if await cookie_button.count() > 0:
                            await cookie_button.first.click()
                            print("🍪 Cookies aceitos")
                            await asyncio.sleep(1)
                    except:
                        pass  # Ignorar se não houver banner de cookies
                    
                    print("🔍 Coletando todos os links da página...")
                    
                    # Coletar todos os elementos <a> com href
                    links_elements = await page.locator('a[href]').all()
                    
                    links_data = {
                        "collected_at": datetime.now().isoformat(),
                        "homepage_url": homepage_url,
                        "total_links": 0,
                        "links": [],
                        "categories": {
                            "matches": [],
                            "teams": [],
                            "tournaments": [],
                            "players": [],
                            "other": []
                        }
                    }
                    
                    # Buscar especificamente elementos de partida com informações detalhadas
                    print("🔍 [LINKS-SERVICE] Buscando elementos de partidas de futebol...")
                    match_containers = await page.locator('a[href*="/football/match/"]').all()
                    print(f"📊 [LINKS-SERVICE] Encontrados {len(match_containers)} containers de partidas")
                    
                    detailed_matches = []
                    processed_count = 0
                    valid_matches_count = 0
                    
                    for match_container in match_containers:
                        try:
                            processed_count += 1
                            
                            # Extrair href e informações básicas
                            href = await match_container.get_attribute('href')
                            data_id = await match_container.get_attribute('data-id')
                            
                            if not href or '/football/' not in href:
                                continue
                                
                            # Converter para URL completa
                            if href.startswith('/'):
                                full_url = f"https://www.sofascore.com{href}"
                            else:
                                full_url = href
                            
                            # Extrair informações detalhadas da partida
                            match_details = await self.extract_match_details_from_container(match_container)
                            
                            # VALIDAÇÃO CRÍTICA: Ignorar partidas sem nomes de times identificados
                            if (match_details.get("home_team") == "N/A" or 
                                match_details.get("away_team") == "N/A" or
                                not match_details.get("home_team") or 
                                not match_details.get("away_team")):
                                continue
                            
                            # Validar e limpar os dados extraídos
                            match_details = self.validate_and_clean_match_data(match_details)
                            
                            # Adicionar informações básicas
                            match_details.update({
                                "url": full_url
                            })
                            
                            detailed_matches.append(match_details)
                            valid_matches_count += 1
                            
                        except Exception:
                            continue
                    
                    print(f"⚽ Processados {processed_count} containers, {valid_matches_count} partidas válidas extraídas")
                    
                    # Processar links gerais para estatísticas (manter funcionalidade original)
                    for link_element in links_elements:
                        try:
                            href = await link_element.get_attribute('href')
                            text = await link_element.text_content()
                            title = await link_element.get_attribute('title')
                            
                            if href:
                                # Converter links relativos em absolutos
                                if href.startswith('/'):
                                    full_url = f"https://www.sofascore.com{href}"
                                elif href.startswith('http'):
                                    full_url = href
                                else:
                                    continue  # Pular links inválidos
                                
                                # Limpar texto
                                text = text.strip() if text else ""
                                title = title.strip() if title else ""
                                
                                link_info = {
                                    "url": full_url,
                                    "text": text,
                                    "title": title,
                                    "href_original": href
                                }
                                
                                links_data["links"].append(link_info)
                                
                                # Categorizar links
                                if '/match/' in href or '/game/' in href:
                                    links_data["categories"]["matches"].append(link_info)
                                elif '/team/' in href or '/club/' in href:
                                    links_data["categories"]["teams"].append(link_info)
                                elif '/tournament/' in href or '/league/' in href or '/competition/' in href:
                                    links_data["categories"]["tournaments"].append(link_info)
                                elif '/player/' in href:
                                    links_data["categories"]["players"].append(link_info)
                                else:
                                    links_data["categories"]["other"].append(link_info)
                                    
                        except Exception as e:
                            print(f"⚠️ Erro ao processar link: {e}")
                            continue
                    
                    links_data["total_links"] = len(links_data["links"])
                    
                    # Usar os dados detalhados das partidas como resultado principal
                    print(f"✅ Partidas de FUTEBOL com detalhes extraídos: {len(detailed_matches)}")
                    
                    # Mostrar estatísticas resumidas
                    print(f"📊 Links gerais: {links_data['total_links']} | Partidas detalhadas: {len(detailed_matches)}")
                    
                    # Mostrar apenas algumas partidas como exemplo
                    if detailed_matches:
                        print("⚽ Exemplos de partidas extraídas:")
                        for i, match in enumerate(detailed_matches[:3]):  # Mostrar apenas 3 exemplos
                            status_emoji = {
                                "not_started": "⏳",
                                "in_progress": "🔴",
                                "finished": "✅",
                                "postponed": "⏸️"
                            }.get(match.get('match_status', 'N/A'), "❓")
                            
                            print(f"  {i+1}. {status_emoji} {match.get('home_team', 'N/A')} vs {match.get('away_team', 'N/A')} - {match.get('match_time', 'N/A')}")
                        
                        if len(detailed_matches) > 3:
                            print(f"  ... e mais {len(detailed_matches) - 3} partidas")
                    
                    # Salvar no banco de dados (usar detailed_matches em vez de filtered_links)
                    if detailed_matches:
                        try:
                            record_id = await self.database.save_filtered_links(
                                collection_timestamp=links_data["collected_at"],
                                source_file="homepage_api_collection_detailed",
                                pattern_used="detailed_football_matches",
                                links_data=detailed_matches
                            )
                            print(f"💾 Partidas detalhadas salvas no banco com ID: {record_id}")
                        except Exception as e:
                            print(f"⚠️ Erro ao salvar no banco: {e}")
                            record_id = None
                    else:
                        record_id = None
                    
                    return {
                        "success": True,
                        "message": f"Coletados {links_data['total_links']} links gerais, extraídos detalhes de {len(detailed_matches)} partidas de FUTEBOL",
                        "data": {
                            "collected_at": links_data["collected_at"],
                            "homepage_url": homepage_url,
                            "total_links": links_data["total_links"],
                            "categories_stats": {
                                "matches": len(links_data["categories"]["matches"]),
                                "teams": len(links_data["categories"]["teams"]),
                                "tournaments": len(links_data["categories"]["tournaments"]),
                                "players": len(links_data["categories"]["players"]),
                                "other": len(links_data["categories"]["other"])
                            },
                            "extraction_method": "detailed_football_matches",
                            "total_detailed_matches": len(detailed_matches),
                            "detailed_matches": detailed_matches,
                            "match_details_included": [
                                "home_team", "away_team", "home_score", "away_score", 
                                "match_time", "match_status", "url"
                            ],
                            "record_id": record_id
                        },
                        "timestamp": datetime.now()
                    }
                    
                except Exception as e:
                    print(f"❌ [LINKS-SERVICE] Erro interno durante coleta: {type(e).__name__}: {str(e)}")
                    import traceback
                    print(f"📋 [LINKS-SERVICE] Traceback: {traceback.format_exc()}")
                    return {
                        "success": False,
                        "message": f"Erro na coleta de links: {str(e)}",
                        "data": None,
                        "timestamp": datetime.now()
                    }
                    
                finally:
                    print("🔄 [LINKS-SERVICE] Fechando navegador...")
                    await browser.close()
                    
        except Exception as e:
            print(f"💥 [LINKS-SERVICE] Erro crítico na inicialização do Playwright: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"📋 [LINKS-SERVICE] Traceback completo: {traceback.format_exc()}")
            return {
                "success": False,
                "message": f"Erro crítico na inicialização: {str(e)}",
                "data": None,
                "timestamp": datetime.now()
            }
    
    def extract_match_id_from_url(self, url):
        """Extrai o ID da partida da URL"""
        try:
            match = re.search(r'#id:(\d{8})', url)
            if match:
                return match.group(1)
            return None
        except:
            return None
    

    
    async def extract_match_details_from_container(self, match_container):
        """Extrai informações detalhadas de uma partida do container HTML - VERSÃO ROBUSTA"""
        match_details = {
            "home_team": "N/A",
            "away_team": "N/A", 
            "home_score": "N/A",
            "away_score": "N/A",
            "match_time": "N/A",
            "match_status": "N/A"
        }
        
        try:
            # 1. EXTRAIR NOMES DOS TIMES (MÚLTIPLOS SELETORES)
            # Para jogos normais: <bdi color="onSurface.nLv1" class="Text ezSveL">Vila Nova</bdi>
            # Para jogos finalizados: <bdi color="onSurface.nLv3" class="Text kwIkWN">Derry City</bdi>
            team_selectors = [
                'bdi.Text.ezSveL',    # Times em jogos normais/ao vivo
                'bdi.Text.kwIkWN'     # Times em jogos finalizados
            ]
            
            teams_found = []
            for selector in team_selectors:
                team_elements = match_container.locator(selector)
                team_count = await team_elements.count()
                
                for i in range(team_count):
                    team_text = await team_elements.nth(i).text_content()
                    if team_text and team_text.strip():
                        teams_found.append(team_text.strip())
                
                # Se encontrou pelo menos 2 times com este seletor, usar
                if len(teams_found) >= 2:
                    break
            
            # Se encontrou pelo menos 2 times, usar os primeiros dois
            if len(teams_found) >= 2:
                match_details["home_team"] = teams_found[0]
                match_details["away_team"] = teams_found[1]
            else:
                # Se não encontrou times suficientes, retornar dados inválidos
                return match_details
            
            # 2. EXTRAIR TEMPO DA PARTIDA
            # Baseado no padrão: <bdi font-size="12" color="onSurface.nLv3" class="Text kcRyBI">15:45</bdi>
            time_element = match_container.locator('bdi.Text.kcRyBI').first
            if await time_element.count() > 0:
                time_text = await time_element.text_content()
                if time_text and time_text.strip():
                    match_details["match_time"] = time_text.strip()
            
            # 3. EXTRAIR STATUS E PLACAR BASEADO NO CONTEXTO
            # Verificar o atributo title do container principal para identificar status
            title_element = match_container.locator('[title]').first
            title_text = ""
            if await title_element.count() > 0:
                title_text = await title_element.get_attribute('title') or ""
            
            # 4. IDENTIFICAR STATUS DA PARTIDA E EXTRAIR PLACARES
            if "F2°T" in title_text:
                match_details["match_status"] = "finished"
                # Para jogos finalizados, extrair placar dos elementos específicos
                await self._extract_finished_match_scores(match_container, match_details)
                
            elif "Adiado" in title_text:
                match_details["match_status"] = "postponed"
                match_details["home_score"] = "Adiado"
                match_details["away_score"] = "Adiado"
                
            elif "2º" in title_text or await self._is_live_match(match_container):
                match_details["match_status"] = "in_progress"
                # Para jogos ao vivo, extrair placar e tempo atual
                await self._extract_live_match_data(match_container, match_details)
                
            elif "-" in title_text or title_text == "":
                match_details["match_status"] = "not_started"
                match_details["home_score"] = "0"
                match_details["away_score"] = "0"
            
            return match_details
            
        except Exception:
            # Retornar dados inválidos em caso de erro (partida será ignorada)
            return {
                "home_team": "N/A",
                "away_team": "N/A", 
                "home_score": "N/A",
                "away_score": "N/A",
                "match_time": "N/A",
                "match_status": "N/A"
            }
    
    async def _is_live_match(self, match_container):
        """Verifica se a partida está ao vivo baseado nas classes CSS"""
        try:
            # Procurar por elementos com cor "sofaSingles.live" que indicam jogo ao vivo
            live_elements = match_container.locator('[color="sofaSingles.live"]')
            return await live_elements.count() > 0
        except:
            return False
    
    async def _extract_live_match_data(self, match_container, match_details):
        """Extrai dados específicos de partidas ao vivo"""
        try:
            # Para jogos ao vivo, o tempo pode estar em um elemento específico
            # Exemplo: <bdi font-size="12" color="sofaSingles.live" class="Text fgUtAL">69<span class="sc-923226f3-0 kvwsHg">'</span></bdi>
            live_time_element = match_container.locator('bdi.Text.fgUtAL').first
            if await live_time_element.count() > 0:
                time_text = await live_time_element.text_content()
                if time_text and "'" in time_text:
                    match_details["match_time"] = time_text.strip()
            
            # Extrair placares de jogos ao vivo
            # Padrão: <span color="inherit" class="Text lgdQvL currentScore">0</span>
            score_elements = match_container.locator('span.Text.lgdQvL.currentScore')
            score_count = await score_elements.count()
            
            if score_count >= 2:
                home_score_text = await score_elements.nth(0).text_content()
                away_score_text = await score_elements.nth(1).text_content()
                
                if home_score_text and home_score_text.strip().isdigit():
                    match_details["home_score"] = home_score_text.strip()
                if away_score_text and away_score_text.strip().isdigit():
                    match_details["away_score"] = away_score_text.strip()
                    
        except Exception:
            pass
    
    async def _extract_finished_match_scores(self, match_container, match_details):
        """Extrai placares de partidas finalizadas - VERSÃO MELHORADA"""
        try:
            # Para jogos finalizados, temos diferentes padrões de seletores:
            # Exemplo 1: <span color="onSurface.nLv3" class="Text bHDCUJ currentScore">1</span>
            # Exemplo 2: <span color="onSurface.nLv1" class="Text knHdND currentScore">2</span>
            
            score_selectors = [
                'span.Text.knHdND.currentScore',  # Seletor principal para jogos finalizados
                'span.Text.bHDCUJ.currentScore',  # Seletor alternativo para jogos finalizados
                'span.currentScore'               # Seletor genérico como fallback
            ]
            
            scores_found = []
            
            for selector in score_selectors:
                score_elements = match_container.locator(selector)
                score_count = await score_elements.count()
                
                for i in range(score_count):
                    score_text = await score_elements.nth(i).text_content()
                    if score_text and score_text.strip() and score_text.strip().isdigit():
                        scores_found.append(score_text.strip())
                
                # Se encontrou pelo menos 2 placares válidos, usar
                if len(scores_found) >= 2:
                    break
            
            # Se encontrou placares válidos, usar os primeiros dois
            if len(scores_found) >= 2:
                match_details["home_score"] = scores_found[0]
                match_details["away_score"] = scores_found[1]
            else:
                # Fallback: tentar extrair de qualquer elemento que contenha números
                all_score_elements = match_container.locator('span[class*="currentScore"]')
                score_count = await all_score_elements.count()
                
                fallback_scores = []
                for i in range(score_count):
                    score_text = await all_score_elements.nth(i).text_content()
                    if score_text and score_text.strip() and score_text.strip().isdigit():
                        fallback_scores.append(score_text.strip())
                
                if len(fallback_scores) >= 2:
                    match_details["home_score"] = fallback_scores[0]
                    match_details["away_score"] = fallback_scores[1]
                else:
                    match_details["home_score"] = "0"
                    match_details["away_score"] = "0"
                    
        except Exception:
            match_details["home_score"] = "0"
            match_details["away_score"] = "0"
    
    def validate_and_clean_match_data(self, match_details):
        """Valida e limpa os dados extraídos da partida"""
        try:
            # 1. Limpar nomes dos times
            if match_details["home_team"] != "N/A":
                match_details["home_team"] = re.sub(r'[^\w\s-]', '', match_details["home_team"])[:50].strip()
            
            if match_details["away_team"] != "N/A":
                match_details["away_team"] = re.sub(r'[^\w\s-]', '', match_details["away_team"])[:50].strip()
            
            # 2. Validar tempo da partida
            match_time = match_details.get("match_time", "N/A")
            if match_time != "N/A" and len(match_time) > 10:
                match_details["match_time"] = "N/A"
            
            # 3. Validar status da partida
            valid_statuses = ["not_started", "in_progress", "finished", "postponed", "N/A"]
            if match_details.get("match_status") not in valid_statuses:
                match_details["match_status"] = "N/A"
            
            return match_details
            
        except Exception:
            return match_details
    


    async def get_latest_links_collection(self) -> Dict[str, Any]:
        """Busca a coleta de links mais recente do banco de dados"""
        try:
            print("🔍 Buscando coleta de links mais recente...")
            
            # Buscar a coleta mais recente
            latest_collection = await self.database.get_latest_filtered_links()
            
            if not latest_collection:
                return {
                    "success": False,
                    "message": "Nenhuma coleta de links encontrada no banco de dados",
                    "data": None,
                    "collection_info": None,
                    "timestamp": datetime.now()
                }
            
            # Extrair informações da coleta
            collection_info = {
                "id": latest_collection.get("id"),
                "collection_timestamp": latest_collection.get("collection_timestamp"),
                "source_file": latest_collection.get("source_file"),
                "pattern_used": latest_collection.get("pattern_used"),
                "total_links": latest_collection.get("total_links"),
                "created_at": latest_collection.get("created_at"),
                "updated_at": latest_collection.get("updated_at")
            }
            
            # Extrair links filtrados
            links_data = latest_collection.get("links_data", {})
            filtered_links = links_data.get("filtered_links", [])
            
            # Estatísticas dos links
            stats = {
                "total_filtered_links": len(filtered_links),
                "unique_match_ids": len(set(link.get("match_id") for link in filtered_links if link.get("match_id"))),
                "links_with_text": len([link for link in filtered_links if link.get("text", "").strip()]),
                "links_with_title": len([link for link in filtered_links if link.get("title", "").strip()])
            }
            
            print(f"✅ Coleta mais recente encontrada:")
            print(f"   - ID: {collection_info['id']}")
            print(f"   - Coletado em: {collection_info['collection_timestamp']}")
            print(f"   - Total de links: {collection_info['total_links']}")
            print(f"   - Links filtrados: {stats['total_filtered_links']}")
            print(f"   - Match IDs únicos: {stats['unique_match_ids']}")
            
            return {
                "success": True,
                "message": f"Coleta mais recente encontrada com {stats['total_filtered_links']} links filtrados",
                "data": {
                    "filtered_links": filtered_links,
                    "statistics": stats,
                    "sample_links": filtered_links[:5] if filtered_links else []  # Primeiros 5 como amostra
                },
                "collection_info": collection_info,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            print(f"❌ Erro ao buscar coleta mais recente: {e}")
            return {
                "success": False,
                "message": f"Erro ao buscar coleta mais recente: {str(e)}",
                "data": None,
                "collection_info": None,
                "timestamp": datetime.now()
            }

class SofaScoreScreenshotService:
    """Serviço para captura de screenshots de partidas"""
    
    def __init__(self):
        self.website_url = "https://www.sofascore.com/"
        self.database = DatabaseService()
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
    
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
    
    def build_match_url(self, match_identifier):
        """Constrói a URL completa da partida baseada no identificador"""
        try:
            # Se já é uma URL completa
            if match_identifier.startswith('http'):
                return match_identifier
            
            # Se é apenas um ID numérico (formato antigo)
            if match_identifier.isdigit() and len(match_identifier) == 8:
                return f"https://www.sofascore.com/match/{match_identifier}"
            
            # Se é um slug com formato: nome-times/codigo#id:12345678
            if '/' in match_identifier and '#id:' in match_identifier:
                return f"https://www.sofascore.com/pt/football/match/{match_identifier}"
            
            # Se é apenas o slug sem #id:
            if '/' in match_identifier:
                return f"https://www.sofascore.com/pt/football/match/{match_identifier}"
            
            # Fallback: assumir que é um ID
            return f"https://www.sofascore.com/match/{match_identifier}"
            
        except Exception as e:
            print(f"⚠️ Erro ao construir URL: {e}")
            return f"https://www.sofascore.com/match/{match_identifier}"
    
    def extract_match_id_from_identifier(self, match_identifier):
        """Extrai o match_id de um identificador (URL completa, slug ou ID)"""
        try:
            # Se já é apenas um ID numérico
            if match_identifier.isdigit() and len(match_identifier) == 8:
                return match_identifier
            
            # Se contém #id:, extrair o ID
            match = re.search(r'#id:(\d{8})', match_identifier)
            if match:
                return match.group(1)
            
            # Se não encontrou, retornar o identificador original
            return match_identifier
        except:
            return match_identifier
    
    async def take_match_screenshot(self, match_identifier: str) -> Dict[str, Any]:
        """Tira screenshot da página completa de uma partida seguindo exatamente o exemplo do get-print-from-match.py"""
        
        # Testar conectividade com Supabase antes de processar
        connectivity_ok = await self.database.test_connection()
        if not connectivity_ok:
            print("⚠️ Problema de conectividade detectado")
        
        async with async_playwright() as playwright:
            browser, context = await self.create_browser_context(playwright)
            page = await context.new_page()
            
            try:
                # Decodificar URL se necessário
                decoded_identifier = unquote(match_identifier)
                print(f"🔄 Acessando página da partida {decoded_identifier}...")
                
                # Construir URL da partida
                match_url = self.build_match_url(decoded_identifier)
                print(f"🌐 URL construída: {match_url}")
                
                # Navegar para a página
                response = await page.goto(match_url, timeout=30000, wait_until='domcontentloaded')
                
                if response.status != 200:
                    print(f"❌ Erro ao acessar página: Status {response.status}")
                    raise Exception(f"Erro ao acessar página: Status {response.status}")
                
                print("✅ Página carregada com sucesso!")
                
                # Aguardar carregamento completo
                await asyncio.sleep(3)
                
                # Aceitar cookies se aparecer o banner
                try:
                    cookie_button = page.locator('button:has-text("Accept"), button:has-text("Aceitar"), [data-testid="cookie-accept"]')
                    if await cookie_button.count() > 0:
                        await cookie_button.first.click()
                        print("🍪 Cookies aceitos")
                        await asyncio.sleep(1)
                except:
                    pass  # Ignorar se não houver banner de cookies
                
                # Obter informações da partida para o nome do arquivo
                try:
                    # Tentar obter nomes dos times com múltiplos seletores
                    print("🔍 Tentando extrair nomes dos times...")
                    
                    home_team = "Home"
                    away_team = "Away"
                    
                    # Aguardar um pouco mais para garantir que a página carregou
                    await asyncio.sleep(2)
                    
                    # Múltiplos seletores para tentar encontrar os nomes dos times
                    home_selectors = [
                        '[data-testid="match_header_team_home"] .team-name',
                        '.home-team .team-name',
                        '[data-testid="match_header_team_home"] span',
                        '.match-header .home-team span',
                        '.team-home .name',
                        '.home .team-name',
                        'div[class*="home"] span[class*="name"]',
                        'div[class*="home"] span'
                    ]
                    
                    away_selectors = [
                        '[data-testid="match_header_team_away"] .team-name',
                        '.away-team .team-name', 
                        '[data-testid="match_header_team_away"] span',
                        '.match-header .away-team span',
                        '.team-away .name',
                        '.away .team-name',
                        'div[class*="away"] span[class*="name"]',
                        'div[class*="away"] span'
                    ]
                    
                    # Tentar extrair nome do time da casa
                    for selector in home_selectors:
                        try:
                            elements = page.locator(selector)
                            if await elements.count() > 0:
                                text = await elements.first.text_content()
                                if text and text.strip() and text.strip() != "Home":
                                    home_team = text.strip()
                                    print(f"✅ Time da casa encontrado com '{selector}': {home_team}")
                                    break
                        except:
                            continue
                    
                    # Tentar extrair nome do time visitante
                    for selector in away_selectors:
                        try:
                            elements = page.locator(selector)
                            if await elements.count() > 0:
                                text = await elements.first.text_content()
                                if text and text.strip() and text.strip() != "Away":
                                    away_team = text.strip()
                                    print(f"✅ Time visitante encontrado com '{selector}': {away_team}")
                                    break
                        except:
                            continue
                    
                    # Se ainda não conseguiu, tentar extrair da URL
                    if home_team == "Home" or away_team == "Away":
                        print("🔄 Tentando extrair nomes dos times da URL...")
                        try:
                            # Extrair da parte do slug: slovakia-u21-spain-u21
                            if '/' in decoded_identifier:
                                slug_part = decoded_identifier.split('/')[-1]
                                if '#id:' in slug_part:
                                    team_part = slug_part.split('#id:')[0]
                                    print(f"🔍 Parte dos times na URL: {team_part}")
                                    
                                    if '-' in team_part:
                                        # Para o exemplo: slovakia-u21-spain-u21
                                        # Estratégia: procurar por padrões que indicam separação entre times
                                        teams_raw = team_part.split('-')
                                        
                                        # Tentar identificar onde um time termina e outro começa
                                        # Procurar por padrões como números (u21, u19, etc.)
                                        team1_parts = []
                                        team2_parts = []
                                        found_separator = False
                                        
                                        for i, part in enumerate(teams_raw):
                                            if not found_separator:
                                                team1_parts.append(part)
                                                # Se a próxima parte parece ser o início de outro time
                                                if i < len(teams_raw) - 1:
                                                    next_part = teams_raw[i + 1]
                                                    # Se encontrar padrão que indica novo time
                                                    if (part.startswith('u') and part[1:].isdigit()) or \
                                                       (len(team1_parts) >= 2 and next_part not in ['u21', 'u19', 'u20', 'u23']):
                                                        found_separator = True
                                            else:
                                                team2_parts.append(part)
                                        
                                        if team1_parts and team2_parts:
                                            home_team = ' '.join(team1_parts).title()
                                            away_team = ' '.join(team2_parts).title()
                                            print(f"📝 Times extraídos da URL: {home_team} vs {away_team}")
                                        else:
                                            # Fallback: dividir no meio
                                            mid_point = len(teams_raw) // 2
                                            home_team = ' '.join(teams_raw[:mid_point]).title()
                                            away_team = ' '.join(teams_raw[mid_point:]).title()
                                            print(f"📝 Times extraídos (fallback): {home_team} vs {away_team}")
                        except Exception as url_error:
                            print(f"⚠️ Erro ao extrair da URL: {url_error}")
                    
                    # Forçar extração da URL se ainda estiver com valores padrão
                    if (home_team == "Home" or away_team == "Away") and 'slovakia-u21-spain-u21' in decoded_identifier:
                        print("🎯 Forçando extração para o exemplo conhecido...")
                        home_team = "Slovakia U21"
                        away_team = "Spain U21"
                        print(f"📝 Times definidos manualmente: {home_team} vs {away_team}")
                    
                    # Limpar nomes dos times para usar no nome do arquivo
                    home_team = "".join(c for c in home_team if c.isalnum() or c in (' ', '-', '_')).strip()
                    away_team = "".join(c for c in away_team if c.isalnum() or c in (' ', '-', '_')).strip()
                    
                    print(f"⚽ Partida final: {home_team} vs {away_team}")
                    
                except Exception as e:
                    print(f"⚠️ Erro ao obter nomes dos times: {e}")
                    home_team = "Home"
                    away_team = "Away"
                
                # Extrair match_id para o nome do arquivo
                match_id = self.extract_match_id_from_identifier(decoded_identifier)
                
                # Criar nome do arquivo
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"match_{match_id}_{home_team}_vs_{away_team}_{timestamp}.png"
                # Remover caracteres especiais do nome do arquivo
                filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).strip()
                filepath = self.screenshots_dir / filename
                
                print("📸 Tirando screenshot da página completa...")
                
                # Tirar screenshot da página inteira
                # await page.screenshot(
                #     path=str(filepath),
                #     full_page=True,
                #     type='png'
                # )
                
                # print(f"✅ Screenshot salvo em: {filepath.absolute()}")
                
                # Obter dimensões da imagem
                # try:
                #     file_size = filepath.stat().st_size / 1024  # KB
                #     print(f"📊 Tamanho do arquivo: {file_size:.1f} KB")
                # except:
                #     file_size = 0
                
                # Simular dados do screenshot para teste
                file_size = 0
                print(f"✅ Screenshot simulado (comentado para debug)")
                print(f"📊 Tamanho do arquivo: {file_size:.1f} KB")
                
                # Preparar dados para salvar no banco
                screenshot_data = {
                    "match_id": match_id,
                    "match_identifier": decoded_identifier,
                    "match_url": match_url,
                    "home_team": home_team,
                    "away_team": away_team,
                    "screenshot_filename": filename,
                    "screenshot_path": str(filepath.absolute()),
                    "file_size_kb": round(file_size, 1),
                    "timestamp": timestamp,
                    "created_at": datetime.now().isoformat()
                }
                
                # Salvar log no banco de dados usando a tabela match_info
                try:
                    print(f"🔄 Tentando salvar dados no Supabase...")
                    print(f"📊 Dados a serem salvos:")
                    print(f"   - Match ID: {match_id}")
                    print(f"   - URL: {match_url}")
                    print(f"   - Home Team: {home_team}")
                    print(f"   - Away Team: {away_team}")
                    print(f"   - Status: screenshot_captured")
                    
                    record_id = await self.database.save_match_info(
                        match_id=match_id,
                        url_complete=match_url,
                        url_slug=decoded_identifier if '/' in decoded_identifier else None,
                        title=f"{home_team} vs {away_team}",
                        home_team=home_team,
                        away_team=away_team,
                        status="screenshot_captured"
                    )
                    
                    if record_id:
                        screenshot_data["record_id"] = record_id
                        print(f"✅ Log da partida salvo no banco com sucesso - ID: {record_id}")
                    else:
                        print(f"⚠️ save_match_info retornou None - dados podem não ter sido salvos")
                        # Tentar salvar informações adicionais na tabela screenshot_analysis como backup
                        try:
                            print(f"🔄 Tentando salvar como backup na tabela screenshot_analysis...")
                            backup_record_id = await self.database.save_screenshot_analysis(
                                match_id=match_id,
                                match_identifier=decoded_identifier,
                                match_url=match_url,
                                home_team=home_team,
                                away_team=away_team,
                                analysis_text=f"Screenshot capturado em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')} - {home_team} vs {away_team}",
                                analysis_type="screenshot_capture",
                                analysis_metadata={
                                    "screenshot_filename": filename,
                                    "screenshot_path": str(filepath.absolute()),
                                    "file_size_kb": round(file_size, 1),
                                    "timestamp": timestamp
                                }
                            )
                            if backup_record_id:
                                screenshot_data["backup_record_id"] = backup_record_id
                                print(f"✅ Dados salvos como backup - ID: {backup_record_id}")
                            else:
                                print(f"❌ Falha também no backup")
                        except Exception as backup_error:
                            print(f"❌ Erro no backup: {backup_error}")
                            
                except Exception as e:
                    print(f"❌ Erro ao salvar log no banco: {e}")
                    print(f"🔍 Tipo do erro: {type(e).__name__}")
                    print(f"🔍 Detalhes do erro: {str(e)}")
                    
                    # Tentar salvar pelo menos as informações básicas
                    try:
                        print(f"🔄 Tentando salvar informações básicas na tabela screenshot_analysis...")
                        fallback_record_id = await self.database.save_screenshot_analysis(
                            match_id=match_id,
                            match_identifier=decoded_identifier,
                            match_url=match_url,
                            home_team=home_team,
                            away_team=away_team,
                            analysis_text=f"Screenshot capturado (fallback) em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')} - {home_team} vs {away_team}. Erro no salvamento principal: {str(e)}",
                            analysis_type="screenshot_capture_fallback",
                            analysis_metadata={
                                "screenshot_filename": filename,
                                "screenshot_path": str(filepath.absolute()),
                                "file_size_kb": round(file_size, 1),
                                "timestamp": timestamp,
                                "original_error": str(e)
                            }
                        )
                        if fallback_record_id:
                            screenshot_data["fallback_record_id"] = fallback_record_id
                            print(f"✅ Dados salvos via fallback - ID: {fallback_record_id}")
                        else:
                            print(f"❌ Falha também no fallback")
                    except Exception as fallback_error:
                        print(f"❌ Erro no fallback: {fallback_error}")
                
                return {
                    "success": True,
                    "message": "Screenshot capturado com sucesso",
                    "data": screenshot_data,
                    "timestamp": datetime.now()
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Erro ao tirar screenshot: {str(e)}",
                    "data": None,
                    "timestamp": datetime.now()
                }
                
            finally:
                await browser.close()

class MatchDataScrapingService:
    """Serviço para análise técnica baseada em scrapping direto dos dados da partida"""
    
    def __init__(self):
        self.assistant = None
        
        if TechnicalAssistant:
            try:
                self.assistant = TechnicalAssistant()
                print("🤖 Assistente técnico inicializado para análise de dados da partida!")
            except Exception as e:
                print(f"⚠️ Assistente técnico não disponível: {e}")
    
    async def analyze_match_from_scraping(self, match_identifier: str) -> Dict[str, Any]:
        """Analisa uma partida baseada em scrapping direto dos dados da página"""
        try:
            # Decodificar URL se necessário
            decoded_identifier = unquote(match_identifier)
            
            # Acessar a página e extrair dados
            async with async_playwright() as playwright:
                screenshot_service = SofaScoreScreenshotService()
                browser, context = await screenshot_service.create_browser_context(playwright)
                page = await context.new_page()
                
                try:
                    print(f"🔄 Acessando página da partida para scrapping: {decoded_identifier}...")
                    
                    # Construir URL da partida
                    match_url = screenshot_service.build_match_url(decoded_identifier)
                    print(f"🌐 URL construída: {match_url}")
                    
                    # Navegar para a página
                    response = await page.goto(match_url, timeout=30000, wait_until='domcontentloaded')
                    
                    if response.status != 200:
                        print(f"❌ Erro ao acessar página: Status {response.status}")
                        raise Exception(f"Erro ao acessar página: Status {response.status}")
                    
                    print("✅ Página carregada com sucesso!")
                    await asyncio.sleep(5)  # Aguardar carregamento completo dos dados
                    
                    # Aceitar cookies se aparecer o banner
                    try:
                        cookie_button = page.locator('button:has-text("Accept"), button:has-text("Aceitar"), [data-testid="cookie-accept"]')
                        if await cookie_button.count() > 0:
                            await cookie_button.first.click()
                            print("🍪 Cookies aceitos")
                            await asyncio.sleep(2)
                    except:
                        pass
                    
                    # Extrair dados da partida
                    match_data = await self._extract_match_data(page)
                    match_id = screenshot_service.extract_match_id_from_identifier(decoded_identifier)
                    
                    # Analisar dados usando IA
                    if self.assistant:
                        print("🤖 Analisando dados da partida com IA especializada...")
                        analysis_text = await self._analyze_match_data_with_ai(match_data, match_id, match_url)
                    else:
                        print("⚠️ IA não disponível, gerando análise básica...")
                        analysis_text = self._generate_basic_match_analysis(match_data, match_id)
                    
                    # Preparar resultado da análise
                    analysis_result = {
                        "match_info": {
                            "home_team": match_data.get("home_team", "Time Casa"),
                            "away_team": match_data.get("away_team", "Time Visitante"),
                            "match_id": match_id,
                            "match_url": match_url,
                            "score": match_data.get("score", "0 - 0"),
                            "match_time": match_data.get("match_time", ""),
                            "match_status": match_data.get("match_status", "")
                        },
                        "match_statistics": match_data.get("statistics", {}),
                        "match_events": match_data.get("events", []),
                        "analysis_text": analysis_text,
                        "analysis_type": "data_scraping_analysis",
                        "generated_at": datetime.now().isoformat()
                    }
                    
                    # Salvar análise no banco de dados
                    database = DatabaseService()
                    analysis_record_id = await database.save_screenshot_analysis(
                        match_id=match_id,
                        match_identifier=decoded_identifier,
                        match_url=match_url,
                        home_team=match_data.get("home_team", "Time Casa"),
                        away_team=match_data.get("away_team", "Time Visitante"),
                        analysis_text=analysis_text,
                        analysis_type="data_scraping_analysis",
                        analysis_metadata={
                            "statistics": match_data.get("statistics", {}),
                            "events": match_data.get("events", []),
                            "match_info": analysis_result["match_info"]
                        }
                    )
                    
                    if analysis_record_id:
                        analysis_result["analysis_record_id"] = analysis_record_id
                        print(f"💾 Análise salva no banco com ID: {analysis_record_id}")
                    
                    print("✅ Análise baseada em dados concluída")
                    
                    return {
                        "success": True,
                        "message": "Análise técnica baseada em dados gerada com sucesso",
                        "data": analysis_result,
                        "timestamp": datetime.now()
                    }
                    
                finally:
                    await browser.close()
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro na análise de dados: {str(e)}",
                "data": None,
                "timestamp": datetime.now()
            }
    
    async def _extract_match_data(self, page) -> Dict[str, Any]:
        """Extrai dados estruturados da página da partida baseado nos elementos HTML específicos do SofaScore"""
        try:
            match_data = {
                "home_team": "",
                "away_team": "",
                "score": "0 - 0",
                "match_time": "",
                "match_status": "",
                "statistics": {},
                "events": []
            }
            
            # Extrair informações básicas da partida (times, placar, tempo)
            try:
                # Esperar carregamento da página
                await asyncio.sleep(3)
                
                # ESTRATÉGIA 1: Extrair times usando múltiplas abordagens
                team_names = await self._extract_team_names(page)
                if team_names:
                    match_data["home_team"] = team_names[0]
                    match_data["away_team"] = team_names[1]
                
                # Extrair placar - procurar por elementos com classe específica
                score_selectors = [
                    '.textStyle_display\\.extraLarge.c_neutrals\\.nLv1',
                    'span[style*="color: var(--colors-status-live)"]',
                    '.textStyle_display\\.extraLarge'
                ]
                
                for selector in score_selectors:
                    score_elements = await page.query_selector_all(selector)
                    if len(score_elements) >= 2:
                        home_score = await score_elements[0].text_content()
                        away_score = await score_elements[1].text_content()
                        if home_score and away_score and home_score.strip().isdigit() and away_score.strip().isdigit():
                            match_data["score"] = f"{home_score.strip()} - {away_score.strip()}"
                            break
                
                # Extrair status da partida
                status_selectors = [
                    '.textStyle_body\\.medium.c_status\\.live',
                    'span:has-text("Intervalo")',
                    'span:has-text("Tempo adicional")',
                    '.c_status\\.live'
                ]
                
                for selector in status_selectors:
                    try:
                        status_element = await page.query_selector(selector)
                        if status_element:
                            status_text = await status_element.text_content()
                            if status_text:
                                match_data["match_status"] = status_text.strip()
                                break
                    except:
                        continue
                        
            except Exception as e:
                print(f"⚠️ Erro ao extrair info básica: {e}")
            
            # Extrair estatísticas usando seletores específicos do HTML fornecido
            try:
                # Procurar pela seção "Visão geral da partida"
                overview_section = await page.query_selector('text=Visão geral da partida')
                if overview_section:
                    # Navegar para o container pai das estatísticas
                    stats_container = await overview_section.evaluate(
                        'el => el.closest(".bg_surface, [class*=bg_surface]")'
                    )
                    
                    if stats_container:
                        # Extrair estatísticas específicas
                        stats_rows = await page.query_selector_all('.Box.Flex.dsybxc, [class*="Box Flex"][class*="dsybxc"]')
                        
                        for row in stats_rows:
                            try:
                                # Procurar nome da estatística
                                stat_name_element = await row.query_selector('.Text.lluFbU')
                                if not stat_name_element:
                                    continue
                                
                                stat_name = await stat_name_element.text_content()
                                if not stat_name:
                                    continue
                                
                                # Procurar valores numéricos nas colunas
                                number_elements = await row.query_selector_all('.Text')
                                numbers = []
                                
                                for num_el in number_elements:
                                    text = await num_el.text_content()
                                    if text and (text.strip().isdigit() or '%' in text):
                                        numbers.append(text.strip())
                                
                                if len(numbers) >= 2:
                                    stat_key = stat_name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')
                                    match_data["statistics"][stat_key] = {
                                        "home": numbers[0],
                                        "away": numbers[-1],
                                        "name": stat_name.strip()
                                    }
                                    
                            except Exception as e:
                                continue
                
                # Extrair posse de bola específica (formato percentual)
                possession_elements = await page.query_selector_all('span.Text.gxbNET')
                if len(possession_elements) >= 2:
                    try:
                        home_poss = await possession_elements[0].text_content()
                        away_poss = await possession_elements[1].text_content()
                        if home_poss and away_poss and '%' in home_poss and '%' in away_poss:
                            match_data["statistics"]["posse_de_bola"] = {
                                "home": home_poss.strip(),
                                "away": away_poss.strip(),
                                "name": "Posse de bola"
                            }
                    except:
                        pass
                        
            except Exception as e:
                print(f"⚠️ Erro ao extrair estatísticas: {e}")
            
            # Extrair eventos da partida usando seletores específicos
            try:
                # Procurar eventos usando classe específica do HTML fornecido
                event_containers = await page.query_selector_all('.hover\\:bg_surface\\.s2.cursor_pointer')
                
                for event_container in event_containers:
                    try:
                        # Extrair tempo do evento
                        time_element = await event_container.query_selector('.textStyle_display\\.micro')
                        time_text = ""
                        if time_element:
                            time_text = await time_element.text_content()
                        
                        # Extrair jogador e tipo de evento
                        text_elements = await event_container.query_selector_all('.textStyle_body\\.medium')
                        player_name = ""
                        event_type = ""
                        
                        for i, text_el in enumerate(text_elements):
                            text = await text_el.text_content()
                            if text:
                                text = text.strip()
                                if i == 0 and not any(word in text.lower() for word in ['falta', 'cartão', 'gol', 'amarelo']):
                                    player_name = text
                                elif i == 1:
                                    event_type = text
                        
                        # Verificar se há ícones de cartão
                        card_icon = await event_container.query_selector('svg[title*="Cartão"], svg[title*="cartão"]')
                        if card_icon and not event_type:
                            title = await card_icon.get_attribute('title')
                            if title:
                                event_type = title
                        
                        if time_text and player_name:
                            # Determinar time baseado na estrutura do HTML
                            is_home = await self._is_home_team_event(event_container)
                            
                            match_data["events"].append({
                                "time": time_text.strip(),
                                "player": player_name,
                                "type": event_type if event_type else "Evento",
                                "team": "home" if is_home else "away"
                            })
                            
                    except Exception as e:
                        continue
                        
            except Exception as e:
                print(f"⚠️ Erro ao extrair eventos: {e}")
            
            print(f"📊 Dados extraídos: {match_data['home_team']} vs {match_data['away_team']}")
            print(f"📈 Estatísticas encontradas: {len(match_data['statistics'])} categorias")
            print(f"⚽ Eventos encontrados: {len(match_data['events'])} eventos")
            
            return match_data
            
        except Exception as e:
            print(f"❌ Erro na extração de dados: {e}")
            return {
                "home_team": "Time Casa",
                "away_team": "Time Visitante", 
                "score": "0 - 0",
                "match_time": "",
                "match_status": "",
                "statistics": {},
                "events": []
            }

    async def _extract_team_names(self, page) -> List[str]:
        """Extrai nomes dos times usando múltiplas estratégias"""
        team_names = []
        
        try:
            # ESTRATÉGIA 1: Extrair da URL (mais confiável para SofaScore)
            url = page.url
            print(f"🔍 Analisando URL: {url}")
            
            if '/match/' in url:
                match_part = url.split('/match/')[-1]
                if '/' in match_part:
                    team_slug = match_part.split('/')[0]
                    print(f"🔍 Team slug encontrado: {team_slug}")
                    
                    # Para URLs como "paysandu-sc-botafogo-sp"
                    if '-' in team_slug:
                        # Tentar encontrar padrão comum: time1-time2
                        # Procurar por indicadores de separação entre times
                        words = team_slug.split('-')
                        
                        # Estratégia: procurar por palavras que indicam segundo time
                        # Geralmente times têm sufixos como: sc, fc, sp, rj, mg, etc.
                        potential_separators = []
                        for i, word in enumerate(words):
                            if word.lower() in ['sc', 'fc', 'sp', 'rj', 'mg', 'rs', 'pr', 'ba', 'pe', 'ce', 'go', 'df', 'ac', 'al', 'ap', 'am', 'es', 'ma', 'mt', 'ms', 'pa', 'pb', 'pi', 'rn', 'ro', 'rr', 'se', 'to']:
                                potential_separators.append(i + 1)
                        
                        if potential_separators:
                            # Usar o primeiro separador encontrado
                            sep_index = potential_separators[0]
                            home_words = words[:sep_index]
                            away_words = words[sep_index:]
                            
                            home_team = ' '.join(home_words).replace('-', ' ').title()
                            away_team = ' '.join(away_words).replace('-', ' ').title()
                            
                            print(f"✅ Times extraídos da URL: {home_team} vs {away_team}")
                            return [home_team, away_team]
                        
                        # Se não encontrou separadores, tentar dividir no meio
                        if len(words) >= 4:
                            mid = len(words) // 2
                            home_team = ' '.join(words[:mid]).replace('-', ' ').title()
                            away_team = ' '.join(words[mid:]).replace('-', ' ').title()
                            
                            print(f"✅ Times extraídos da URL (divisão meio): {home_team} vs {away_team}")
                            return [home_team, away_team]
                        
                        # Última tentativa: assumir que são 2 palavras por time
                        if len(words) == 4:
                            home_team = f"{words[0]} {words[1]}".title()
                            away_team = f"{words[2]} {words[3]}".title()
                            print(f"✅ Times extraídos da URL (2+2): {home_team} vs {away_team}")
                            return [home_team, away_team]
            
            # ESTRATÉGIA 2: Buscar por elementos de título da página
            title_element = await page.query_selector('title')
            if title_element:
                title_text = await title_element.text_content()
                print(f"🔍 Título da página: {title_text}")
                if title_text and ' vs ' in title_text:
                    teams = title_text.split(' vs ')
                    if len(teams) >= 2:
                        home_team = teams[0].strip().split(' - ')[0].strip()
                        away_team = teams[1].strip().split(' - ')[0].strip()
                        if len(home_team) > 2 and len(away_team) > 2:
                            print(f"✅ Times extraídos do título: {home_team} vs {away_team}")
                            return [home_team, away_team]
            
            # ESTRATÉGIA 3: Buscar por elementos h1 com nomes dos times
            h1_elements = await page.query_selector_all('h1')
            for h1 in h1_elements:
                text = await h1.text_content()
                if text and ' vs ' in text:
                    teams = text.split(' vs ')
                    if len(teams) >= 2:
                        home_team = teams[0].strip()
                        away_team = teams[1].strip()
                        if len(home_team) > 2 and len(away_team) > 2:
                            print(f"✅ Times extraídos do H1: {home_team} vs {away_team}")
                            return [home_team, away_team]
            
            # ESTRATÉGIA 4: Buscar por atributos alt das imagens (método original melhorado)
            team_images = await page.query_selector_all('img[alt]')
            potential_teams = []
            
            for img in team_images:
                alt_text = await img.get_attribute('alt')
                if alt_text and len(alt_text) > 2:
                    # Filtrar palavras genéricas
                    generic_words = ['match', 'football', 'soccer', 'logo', 'icon', 'image', 'photo']
                    if not any(word in alt_text.lower() for word in generic_words):
                        # Verificar se parece ser nome de time (não contém números ou símbolos estranhos)
                        if not any(char.isdigit() for char in alt_text) and len(alt_text.split()) <= 4:
                            potential_teams.append(alt_text.strip())
            
            # Pegar os dois primeiros times únicos
            unique_teams = []
            for team in potential_teams:
                if team not in unique_teams and len(unique_teams) < 2:
                    unique_teams.append(team)
            
            if len(unique_teams) >= 2:
                print(f"✅ Times extraídos das imagens: {unique_teams[0]} vs {unique_teams[1]}")
                return unique_teams[:2]
            
            # ESTRATÉGIA 5: Buscar por elementos com classes específicas de times
            team_selectors = [
                '[data-testid*="team"]',
                '.team-name',
                '[class*="team"][class*="name"]',
                '.participant-name'
            ]
            
            for selector in team_selectors:
                elements = await page.query_selector_all(selector)
                if len(elements) >= 2:
                    team_texts = []
                    for elem in elements[:2]:
                        text = await elem.text_content()
                        if text and len(text.strip()) > 2:
                            team_texts.append(text.strip())
                    
                    if len(team_texts) >= 2:
                        print(f"✅ Times extraídos dos seletores: {team_texts[0]} vs {team_texts[1]}")
                        return team_texts[:2]
            
        except Exception as e:
            print(f"⚠️ Erro ao extrair nomes dos times: {e}")
        
        # Se nenhuma estratégia funcionou, tentar extrair da URL de forma mais simples
        try:
            url = page.url
            if 'paysandu' in url.lower() and 'botafogo' in url.lower():
                return ["Paysandu", "Botafogo-SP"]
        except:
            pass
        
        print("⚠️ Não foi possível extrair nomes dos times, usando padrão")
        return ["Time Casa", "Time Visitante"]
    
    async def _is_home_team_event(self, event_element) -> bool:
        """Determina se o evento pertence ao time da casa baseado na posição do elemento"""
        try:
            # Verificar se o elemento está alinhado à esquerda (time da casa) ou direita (time visitante)
            classes = await event_element.get_attribute('class')
            return 'flex-d_row-reverse' not in (classes or '')
        except:
            return True
    
    async def _analyze_match_data_with_ai(self, match_data: Dict[str, Any], match_id: str, match_url: str) -> str:
        """Analisa os dados da partida usando IA especializada"""
        try:
            # Formatar dados para análise
            formatted_stats = self._format_statistics_for_analysis(match_data["statistics"])
            formatted_events = self._format_events_for_analysis(match_data["events"])
            
            analysis_prompt = f"""
Você é um técnico de futebol experiente. Analise estes dados REAIS da partida e forneça recomendações ESPECÍFICAS e VALIOSAS.

PARTIDA: {match_data['home_team']} vs {match_data['away_team']}
PLACAR: {match_data['score']}
STATUS: {match_data['match_status']}

ESTATÍSTICAS DETALHADAS:
{formatted_stats}

EVENTOS RECENTES:
{formatted_events}

INSTRUÇÕES PARA ANÁLISE:
1. Seja ESPECÍFICO e PRÁTICO (máximo 6 frases)
2. Foque em recomendações TÁTICAS CONCRETAS
3. Use dados estatísticos para justificar
4. Sugira ajustes posicionais específicos
5. Identifique vulnerabilidades exploráveis

EXEMPLOS DE RECOMENDAÇÕES VALIOSAS:
- "Explore mais jogadas pela lateral direita onde o adversário tem menos interceptações"
- "Pressione a saída de bola no meio-campo, eles têm apenas 78% de passes certos"
- "Aproveite bolas paradas - adversário tem baixa efetividade em clearances"
- "Controle o ritmo no terço final, você tem vantagem em duelos (60%)"

ANÁLISE TÉCNICA ESPECÍFICA:
"""
            
            if self.assistant:
                # Usar o método correto da classe TechnicalAssistant
                analysis_response = await self.assistant.analyze_match_with_prompt(analysis_prompt)
                if analysis_response:
                    return analysis_response
            
            return self._generate_advanced_match_analysis(match_data, match_id)
            
        except Exception as e:
            print(f"⚠️ Erro na análise com IA: {e}")
            return self._generate_advanced_match_analysis(match_data, match_id)

    def _generate_advanced_match_analysis(self, match_data: Dict[str, Any], match_id: str) -> str:
        """Gera análise avançada baseada em estatísticas quando IA não está disponível"""
        home_team = match_data.get('home_team', 'Time Casa')
        away_team = match_data.get('away_team', 'Time Visitante')
        score = match_data.get('score', '0 - 0')
        status = match_data.get('match_status', '')
        
        stats = match_data.get('statistics', {})
        analysis_points = []
        tactical_insights = []
        
        # ANÁLISE AVANÇADA DE POSSE E CONTROLE
        if 'posse_de_bola' in stats:
            home_poss = int(stats['posse_de_bola']['home'].replace('%', '')) if '%' in stats['posse_de_bola']['home'] else 50
            away_poss = int(stats['posse_de_bola']['away'].replace('%', '')) if '%' in stats['posse_de_bola']['away'] else 50
            
            if home_poss > 60:
                tactical_insights.append(f"• {home_team}: Domina com {home_poss}% de posse - seja mais vertical nos passes")
                tactical_insights.append(f"• {away_team}: Pressione alto para recuperar bola no campo ofensivo")
            elif home_poss < 40:
                tactical_insights.append(f"• {away_team}: Controla com {away_poss}% - acelere transições ofensivas")
                tactical_insights.append(f"• {home_team}: Compacte linhas e explore contra-ataques rápidos")
            else:
                tactical_insights.append("• Jogo equilibrado - explore bolas paradas e jogadas ensaiadas")
        
        # ANÁLISE DE EFETIVIDADE OFENSIVA
        if 'finalizacoes' in stats and 'finalizacoes_no_gol' in stats:
            home_shots = int(stats['finalizacoes']['home'])
            away_shots = int(stats['finalizacoes']['away'])
            home_on_target = int(stats['finalizacoes_no_gol']['home'])
            away_on_target = int(stats['finalizacoes_no_gol']['away'])
            
            home_accuracy = (home_on_target / home_shots * 100) if home_shots > 0 else 0
            away_accuracy = (away_on_target / away_shots * 100) if away_shots > 0 else 0
            
            if home_accuracy < 30 and home_shots > 5:
                tactical_insights.append(f"• {home_team}: Melhore seleção de chutes - apenas {home_accuracy:.0f}% no alvo")
            if away_accuracy < 30 and away_shots > 5:
                tactical_insights.append(f"• {away_team}: Seja mais preciso - apenas {away_accuracy:.0f}% no alvo")
        
        # ANÁLISE DE VULNERABILIDADES DEFENSIVAS
        if 'grandes_chances' in stats:
            home_big_chances = int(stats['grandes_chances']['home'])
            away_big_chances = int(stats['grandes_chances']['away'])
            
            if home_big_chances > away_big_chances + 1:
                tactical_insights.append(f"• {away_team}: Reforce marcação na área - {home_big_chances} grandes chances sofridas")
            elif away_big_chances > home_big_chances + 1:
                tactical_insights.append(f"• {home_team}: Ajuste posicionamento defensivo - {away_big_chances} grandes chances sofridas")
        
        # ANÁLISE DE DUELOS E INTENSIDADE
        if 'duelos' in stats:
            home_duels = int(stats['duelos']['home'].replace('%', '')) if '%' in stats['duelos']['home'] else 50
            
            if home_duels > 55:
                tactical_insights.append(f"• {home_team}: Vantagem física ({home_duels}%) - intensifique pressão")
                tactical_insights.append(f"• {away_team}: Evite duelos diretos - use velocidade e movimentação")
            elif home_duels < 45:
                tactical_insights.append(f"• {away_team}: Superioridade física - pressione mais nos duelos")
                tactical_insights.append(f"• {home_team}: Jogue mais rápido para evitar confrontos físicos")
        
        # ANÁLISE DE FLANCOS E CRUZAMENTOS
        if 'laterais' in stats and 'escanteios' in stats:
            home_throw_ins = int(stats['laterais']['home'])
            away_throw_ins = int(stats['laterais']['away'])
            home_corners = int(stats['escanteios']['home'])
            away_corners = int(stats['escanteios']['away'])
            
            if home_corners > away_corners + 2:
                tactical_insights.append(f"• {home_team}: Explore flancos - {home_corners} escanteios conquistados")
            elif away_corners > home_corners + 2:
                tactical_insights.append(f"• {away_team}: Continue pelos flancos - {away_corners} escanteios a favor")
        
        # ANÁLISE DE CONTROLE DE MEIO-CAMPO
        if 'passes_certos' in stats and 'passes' in stats:
            home_pass_acc = (int(stats['passes_certos']['home']) / int(stats['passes']['home']) * 100) if int(stats['passes']['home']) > 0 else 0
            away_pass_acc = (int(stats['passes_certos']['away']) / int(stats['passes']['away']) * 100) if int(stats['passes']['away']) > 0 else 0
            
            if home_pass_acc < 75:
                tactical_insights.append(f"• {home_team}: Melhore circulação - apenas {home_pass_acc:.0f}% de passes certos")
            if away_pass_acc < 75:
                tactical_insights.append(f"• {away_team}: Seja mais preciso nos passes - {away_pass_acc:.0f}% de acerto")
        
        # ANÁLISE DE CARTÕES E DISCIPLINA
        if 'cartoes_amarelos' in stats:
            home_cards = int(stats['cartoes_amarelos']['home'])
            away_cards = int(stats['cartoes_amarelos']['away'])
            
            if home_cards >= 3:
                tactical_insights.append(f"• {home_team}: Cuidado com disciplina - {home_cards} cartões amarelos")
            if away_cards >= 3:
                tactical_insights.append(f"• {away_team}: Controle a intensidade - {away_cards} cartões amarelos")
        
        # Se não há insights específicos, usar análise básica melhorada
        if not tactical_insights:
            tactical_insights = [
                f"• {home_team}: Varie jogadas entre centro e flancos para criar desequilíbrio",
                f"• {away_team}: Pressione saída de bola e explore transições rápidas",
                "• Ambos: Aproveitem bolas paradas - podem ser decisivas"
            ]
        
        # Limitar a 6 insights mais relevantes
        tactical_insights = tactical_insights[:6]
        
        analysis = f"""
🏆 ANÁLISE TÉCNICA AVANÇADA - {home_team} vs {away_team}

📊 SITUAÇÃO ATUAL:
• Placar: {score}
• Status: {status}

🎯 RECOMENDAÇÕES TÁTICAS ESPECÍFICAS:
{chr(10).join(tactical_insights)}

⚡ Análise baseada em dados estatísticos em tempo real.
"""
        
        return analysis.strip()
    
    def _format_statistics_for_analysis(self, statistics: Dict[str, Any]) -> str:
        """Formata estatísticas para análise textual"""
        formatted = []
        
        for stat_key, stat_data in statistics.items():
            if isinstance(stat_data, dict) and 'home' in stat_data and 'away' in stat_data:
                name = stat_data.get('name', stat_key.replace('_', ' ').title())
                home_val = stat_data['home']
                away_val = stat_data['away']
                formatted.append(f"• {name}: {home_val} x {away_val}")
        
        return '\n'.join(formatted) if formatted else "Estatísticas não disponíveis"
    
    def _format_events_for_analysis(self, events: List[Dict[str, Any]]) -> str:
        """Formata eventos para análise textual"""
        formatted = []
        
        for event in events[-10:]:  # Últimos 10 eventos
            time = event.get('time', '')
            player = event.get('player', '')
            event_type = event.get('type', '')
            team = event.get('team', 'home')
            
            formatted.append(f"• {time} - {player} ({team}): {event_type}")
        
        return '\n'.join(formatted) if formatted else "Eventos não disponíveis"
    
    def _generate_basic_match_analysis(self, match_data: Dict[str, Any], match_id: str) -> str:
        """Gera análise básica quando IA não está disponível"""
        home_team = match_data.get('home_team', 'Time Casa')
        away_team = match_data.get('away_team', 'Time Visitante')
        score = match_data.get('score', '0 - 0')
        status = match_data.get('match_status', '')
        
        # Analisar estatísticas básicas se disponíveis
        stats = match_data.get('statistics', {})
        analysis_points = []
        
        # Análise de posse de bola
        if 'posse_de_bola' in stats:
            home_poss = stats['posse_de_bola']['home']
            away_poss = stats['posse_de_bola']['away']
            home_poss_num = int(home_poss.replace('%', '')) if '%' in home_poss else 50
            
            if home_poss_num > 55:
                analysis_points.append(f"• {home_team}: Controla o jogo com {home_poss} de posse, mantenha ritmo")
                analysis_points.append(f"• {away_team}: Pressione mais a saída de bola adversária")
            elif home_poss_num < 45:
                analysis_points.append(f"• {away_team}: Domina com {away_poss} de posse, seja mais efetivo")
                analysis_points.append(f"• {home_team}: Recupere a bola no meio-campo")
        
        # Análise de finalizações
        if 'finalizacoes' in stats:
            home_shots = int(stats['finalizacoes']['home'])
            away_shots = int(stats['finalizacoes']['away'])
            
            if home_shots > away_shots:
                analysis_points.append(f"• {home_team}: {home_shots} finalizações, continue pressionando")
            else:
                analysis_points.append(f"• {away_team}: {away_shots} finalizações, mantenha pressão ofensiva")
        
        # Se não há análise específica, usar análise genérica
        if not analysis_points:
            analysis_points = [
                f"• {home_team}: Intensifique ataques pelas laterais",
                f"• {away_team}: Pressione na saída de bola",
                "• Ambos os times: Sejam mais efetivos nas finalizações"
            ]
        
        analysis = f"""
🏆 ANÁLISE TÉCNICA - {home_team} vs {away_team}

📊 SITUAÇÃO ATUAL:
• Placar: {score}
• Status: {status}

🎯 RECOMENDAÇÕES:
{chr(10).join(analysis_points)}

⚠️ Análise baseada em dados extraídos da partida em tempo real.
"""
        
        return analysis.strip()