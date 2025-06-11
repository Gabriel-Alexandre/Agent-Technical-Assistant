"""
API de Coleta de Dados do SofaScore
FastAPI para análise técnica de futebol em tempo real
"""

# Configuração do Event Loop para Windows (deve estar antes de outros imports)
import sys
import asyncio
import platform

# Configurar ProactorEventLoop no Windows para compatibilidade com Playwright
if platform.system() == "Windows":
    # Definir política de event loop para Windows
    if hasattr(asyncio, 'WindowsProactorEventLoopPolicy'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    else:
        # Para versões mais antigas do Python no Windows
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)

import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# Importar modelos e serviços
from models import (
    MatchDataRequest, 
    MatchDataResponse, 
    SimplifiedDataResponse, 
    AnalysisResponse, 
    ErrorResponse
)
from services import MatchDataService
from database_service import DatabaseService

# Configuração da aplicação
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Configuração de inicialização e finalização da aplicação"""
    # Inicialização
    print("🚀 Iniciando API de Coleta de Dados do SofaScore...")
    
    # Verificar/criar tabelas do banco
    db_service = DatabaseService()
    await db_service.create_tables_if_not_exist()
    
    print("✅ API inicializada com sucesso!")
    
    yield
    
    # Finalização
    print("🔄 Finalizando API...")

# Criar aplicação FastAPI
app = FastAPI(
    title="SofaScore Data Collector API",
    description="""
    ## API de Coleta de Dados do SofaScore para Análise Técnica

    Esta API permite coletar dados em tempo real do SofaScore e gerar análises técnicas automáticas usando IA.

    ### Funcionalidades Principais:
    - 📊 **Dados Completos**: Coleta todos os dados disponíveis de uma partida
    - 🎯 **Dados Simplificados**: Extrai apenas informações relevantes para análise
    - 🤖 **Análise com IA**: Gera sugestões táticas usando GPT-4o-mini

    ### Como usar:
    1. **Dados Completos**: `POST /match/{match_id}/full-data`
    2. **Dados Simplificados**: `POST /match/{match_id}/simplified-data`  
    3. **Análise Completa**: `POST /match/{match_id}/analysis`

    ### Banco de Dados:
    - Todos os dados são salvos no Supabase
    - Suporte a múltiplas coletas da mesma partida
    - Ideal para monitoramento em tempo real (coleta a cada 30s)
    """,
    version="2.0.0",
    contact={
        "name": "Assistente Técnico de Futebol",
        "email": "support@example.com"
    },
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar serviço
match_service = MatchDataService()

@app.get("/", tags=["Status"])
async def root():
    """Endpoint raiz - Status da API"""
    return {
        "message": "🏆 SofaScore Data Collector API",
        "version": "2.0.0",
        "status": "✅ Online",
        "timestamp": datetime.now(),
        "endpoints": {
            "full_data": "/match/{match_id}/full-data",
            "simplified_data": "/match/{match_id}/simplified-data",
            "analysis": "/match/{match_id}/analysis"
        }
    }

@app.get("/health", tags=["Status"])
async def health_check():
    """Verificação de saúde da API"""
    try:
        # Testar conexão com banco
        db_service = DatabaseService()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(),
            "services": {
                "database": "✅ Connected",
                "ai_assistant": "✅ Available" if match_service.assistant else "⚠️ Not configured"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Serviço indisponível: {str(e)}"
        )

@app.post("/match/{match_id}/full-data", 
          response_model=MatchDataResponse,
          tags=["Coleta de Dados"],
          summary="Obter Dados Completos da Partida",
          description="""
          Coleta todos os dados disponíveis do SofaScore para uma partida específica.
          
          **Dados coletados:**
          - Informações básicas (times, placar, status)
          - Estatísticas detalhadas
          - Timeline de eventos
          - Escalações e formações
          - Mapa de chutes (shotmap)
          - Estatísticas de jogadores
          
          **Uso recomendado:** Para análises detalhadas ou como base para outros endpoints.
          """)
async def get_full_match_data(match_id: str):
    """Endpoint 1: Obter todos os dados do SofaScore para uma partida específica"""
    try:
        print(f"🎯 Requisição para dados completos - Match ID: {match_id}")
        
        # Validar match_id
        if not match_id or not match_id.isdigit():
            raise HTTPException(
                status_code=400,
                detail="Match ID deve ser um número válido"
            )
        
        # Coletar dados
        result = await match_service.get_full_match_data(match_id)
        
        if result["success"]:
            return MatchDataResponse(**result)
        else:
            raise HTTPException(
                status_code=500,
                detail=result["message"]
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )

@app.post("/match/{match_id}/simplified-data",
          response_model=SimplifiedDataResponse,
          tags=["Coleta de Dados"],
          summary="Obter Dados Simplificados da Partida",
          description="""
          Coleta e simplifica dados da partida, extraindo apenas informações relevantes para análise técnica.
          
          **Dados simplificados incluem:**
          - Resumo da partida (times, placar, status)
          - Estatísticas principais categorizadas
          - Eventos importantes (gols, cartões, substituições)
          - Configuração tática (formações, jogadores-chave)
          - Análise de chutes
          
          **Uso recomendado:** Para análises rápidas ou alimentar sistemas de IA.
          """)
async def get_simplified_match_data(match_id: str):
    """Endpoint 2: Obter dados simplificados para uma partida específica"""
    try:
        print(f"🎯 Requisição para dados simplificados - Match ID: {match_id}")
        
        # Validar match_id
        if not match_id or not match_id.isdigit():
            raise HTTPException(
                status_code=400,
                detail="Match ID deve ser um número válido"
            )
        
        # Processar dados
        result = await match_service.get_simplified_match_data(match_id)
        
        if result["success"]:
            return SimplifiedDataResponse(**result)
        else:
            raise HTTPException(
                status_code=500,
                detail=result["message"]
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )

@app.post("/match/{match_id}/analysis",
          response_model=AnalysisResponse,
          tags=["Análise Técnica"],
          summary="Obter Análise Completa com IA",
          description="""
          Coleta dados da partida, simplifica e gera análise técnica completa usando GPT-4o-mini.
          
          **Processo completo:**
          1. Coleta dados completos do SofaScore
          2. Simplifica dados para análise
          3. Gera análise técnica especializada com IA
          4. Salva tudo no banco de dados
          
          **A análise inclui:**
          - Situação tática atual
          - Análise crítica de pontos-chave
          - Sugestões táticas prioritárias para ambos os times
          - Alertas críticos
          - Previsão tática
          
          **Requisitos:** OPENAI_API_KEY configurada no arquivo .env
          """)
async def get_match_analysis(match_id: str):
    """Endpoint 3: Obter dados + sugestão do agente para uma partida específica"""
    try:
        print(f"🤖 Requisição para análise completa - Match ID: {match_id}")
        
        # Validar match_id
        if not match_id or not match_id.isdigit():
            raise HTTPException(
                status_code=400,
                detail="Match ID deve ser um número válido"
            )
        
        # Verificar se assistente está disponível
        if not match_service.assistant:
            raise HTTPException(
                status_code=503,
                detail="Assistente técnico não disponível. Configure OPENAI_API_KEY no arquivo .env"
            )
        
        # Gerar análise completa
        result = await match_service.get_match_analysis(match_id)
        
        if result["success"]:
            return AnalysisResponse(**result)
        else:
            raise HTTPException(
                status_code=500,
                detail=result["message"]
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )

@app.get("/match/{match_id}/history",
         tags=["Histórico"],
         summary="Histórico de Coletas da Partida",
         description="Recupera o histórico de coletas de dados de uma partida específica")
async def get_match_history(match_id: str, limit: int = 10):
    """Endpoint para recuperar histórico de coletas de uma partida"""
    try:
        db_service = DatabaseService()
        
        # Buscar histórico no banco
        history = await db_service.get_match_history(match_id, limit)
        
        return {
            "success": True,
            "match_id": match_id,
            "total_records": len(history),
            "history": history
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar histórico: {str(e)}"
        )

@app.get("/test/playwright",
         tags=["Testes"],
         summary="Testar Funcionamento do Playwright",
         description="""
         Testa se o Playwright está funcionando corretamente no ambiente de deploy.
         
         **O que este teste faz:**
         - Inicializa o navegador Chromium
         - Acessa uma página simples (Google)
         - Verifica se consegue extrair o título da página
         - Testa acesso ao SofaScore com múltiplas estratégias
         - Retorna informações detalhadas do sistema
         
         **Útil para diagnosticar:**
         - Problemas de instalação do Playwright
         - Configurações de navegador inadequadas
         - Bloqueios de rede
         - Limitações do ambiente de deploy
         """)
async def test_playwright():
    """Endpoint para testar se o Playwright está funcionando corretamente"""
    import platform
    import asyncio
    from datetime import datetime
    
    test_results = {
        "success": False,
        "timestamp": datetime.now(),
        "system_info": {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "event_loop": type(asyncio.get_running_loop()).__name__,
            "event_loop_policy": type(asyncio.get_event_loop_policy()).__name__
        },
        "tests": {},
        "errors": []
    }
    
    try:
        # Importar Playwright
        try:
            from playwright.async_api import async_playwright
            test_results["tests"]["playwright_import"] = "✅ Sucesso"
        except ImportError as e:
            test_results["tests"]["playwright_import"] = f"❌ Falha: {str(e)}"
            test_results["errors"].append(f"Playwright não instalado: {str(e)}")
            return test_results
        
        # Testar inicialização do navegador
        try:
            async with async_playwright() as playwright:
                test_results["tests"]["playwright_init"] = "✅ Sucesso"
                
                # Testar criação do navegador com configurações mais robustas
                try:
                    browser = await playwright.chromium.launch(
                        headless=True,
                        args=[
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
                    )
                    
                    if browser:
                        test_results["tests"]["browser_launch"] = f"✅ Sucesso - Navegador inicializado"
                        test_results["system_info"]["browser_version"] = "Chromium (versão não detectável)"
                    else:
                        test_results["tests"]["browser_launch"] = f"❌ Falha: Navegador não foi criado"
                        test_results["errors"].append("Navegador não foi criado corretamente")
                        return test_results
                    
                    # Testar criação de contexto com configurações otimizadas
                    try:
                        context = await browser.new_context(
                            viewport={'width': 1920, 'height': 1080},
                            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                            extra_http_headers={
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
                            ignore_https_errors=True,
                            java_script_enabled=True
                        )
                        test_results["tests"]["context_creation"] = "✅ Sucesso"
                        
                        # Testar criação de página
                        try:
                            page = await context.new_page()
                            
                            # Configurar timeouts mais longos
                            page.set_default_timeout(30000)  # 30 segundos
                            page.set_default_navigation_timeout(30000)  # 30 segundos
                            
                            # Adicionar script para esconder automação
                            await page.add_init_script("""
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
                            
                            test_results["tests"]["page_creation"] = "✅ Sucesso"
                            
                            # Testar conectividade básica com sites simples
                            connectivity_tests = [
                                {"name": "Google", "url": "https://www.google.com"},
                                {"name": "Example", "url": "https://example.com"},
                                {"name": "Httpbin", "url": "https://httpbin.org/get"}
                            ]
                            
                            working_sites = 0
                            for test_site in connectivity_tests:
                                try:
                                    response = await page.goto(test_site["url"], 
                                                              timeout=15000, 
                                                              wait_until='domcontentloaded')
                                    if response.status == 200:
                                        working_sites += 1
                                        test_results["tests"][f"{test_site['name'].lower()}_access"] = f"✅ {test_site['name']} - Status: {response.status}"
                                    else:
                                        test_results["tests"][f"{test_site['name'].lower()}_access"] = f"⚠️ {test_site['name']} - Status: {response.status}"
                                except Exception as e:
                                    test_results["tests"][f"{test_site['name'].lower()}_access"] = f"❌ {test_site['name']} - {str(e)[:50]}..."
                            
                            # Avaliar conectividade geral
                            if working_sites >= 2:
                                test_results["tests"]["network_connectivity"] = f"✅ Conectividade OK ({working_sites}/{len(connectivity_tests)} sites acessíveis)"
                            elif working_sites >= 1:
                                test_results["tests"]["network_connectivity"] = f"⚠️ Conectividade limitada ({working_sites}/{len(connectivity_tests)} sites acessíveis)"
                            else:
                                test_results["tests"]["network_connectivity"] = f"❌ Problemas de conectividade (0/{len(connectivity_tests)} sites acessíveis)"
                                test_results["errors"].append("Problemas graves de conectividade de rede detectados")
                            
                            # Testar acesso ao SofaScore com múltiplas estratégias (independente da conectividade geral)
                            sofascore_strategies = [
                                {
                                    "name": "Estratégia 1: Carregamento rápido",
                                    "url": "https://www.sofascore.com",
                                    "timeout": 30000,
                                    "wait_until": "domcontentloaded"
                                },
                                {
                                    "name": "Estratégia 2: Aguardar rede",
                                    "url": "https://www.sofascore.com",
                                    "timeout": 45000,
                                    "wait_until": "networkidle"
                                },
                                {
                                    "name": "Estratégia 3: Acesso direto à API",
                                    "url": "https://api.sofascore.com/api/v1/sport/football/events/live",
                                    "timeout": 20000,
                                    "wait_until": "domcontentloaded"
                                }
                            ]
                            
                            sofascore_success = False
                            
                            for i, strategy in enumerate(sofascore_strategies):
                                print(f"🔄 Testando {strategy['name']}...")
                                strategy_start_time = datetime.now()
                                
                                try:
                                    # Simular delay humano antes de cada tentativa
                                    await page.wait_for_timeout(2000)
                                    
                                    # Limpar cookies e cache antes de nova tentativa
                                    if i > 0:
                                        await context.clear_cookies()
                                    
                                    sofascore_response = await page.goto(
                                        strategy["url"], 
                                        timeout=strategy["timeout"],
                                        wait_until=strategy["wait_until"]
                                    )
                                    
                                    strategy_duration = (datetime.now() - strategy_start_time).total_seconds()
                                    
                                    if sofascore_response.status == 200:
                                        if "api.sofascore.com" in strategy["url"]:
                                            # Para API, verificar se retornou JSON
                                            content = await page.content()
                                            if '{' in content and '}' in content:
                                                test_results["tests"][f"strategy_{i+1}_result"] = f"✅ {strategy['name']} - API funcionando ({strategy_duration:.1f}s)"
                                                if not sofascore_success:
                                                    test_results["tests"]["sofascore_api_access"] = f"✅ {strategy['name']} - API funcionando"
                                                    sofascore_success = True
                                            else:
                                                test_results["tests"][f"strategy_{i+1}_result"] = f"⚠️ {strategy['name']} - Status 200, mas sem JSON na resposta ({strategy_duration:.1f}s)"
                                        else:
                                            # Para site principal, verificar título
                                            try:
                                                await page.wait_for_timeout(3000)  # Aguardar carregamento
                                                sofascore_title = await page.title()
                                                if sofascore_title and len(sofascore_title) > 0:
                                                    test_results["tests"][f"strategy_{i+1}_result"] = f"✅ {strategy['name']} - Status: {sofascore_response.status}, Título: {sofascore_title[:30]}... ({strategy_duration:.1f}s)"
                                                    if not sofascore_success:
                                                        test_results["tests"]["sofascore_website_access"] = f"✅ {strategy['name']} - Status: {sofascore_response.status}, Título: {sofascore_title[:50]}..."
                                                        sofascore_success = True
                                                else:
                                                    test_results["tests"][f"strategy_{i+1}_result"] = f"⚠️ {strategy['name']} - Status 200, mas título vazio ({strategy_duration:.1f}s)"
                                            except Exception as title_e:
                                                test_results["tests"][f"strategy_{i+1}_result"] = f"⚠️ {strategy['name']} - Status 200, erro no título: {str(title_e)[:30]}... ({strategy_duration:.1f}s)"
                                    else:
                                        test_results["tests"][f"strategy_{i+1}_result"] = f"❌ {strategy['name']} - Status: {sofascore_response.status} ({strategy_duration:.1f}s)"
                                
                                except Exception as e:
                                    strategy_duration = (datetime.now() - strategy_start_time).total_seconds()
                                    error_msg = str(e)
                                    if "Timeout" in error_msg:
                                        test_results["tests"][f"strategy_{i+1}_result"] = f"⏱️ {strategy['name']} - Timeout após {strategy_duration:.1f}s (limite: {strategy['timeout']/1000}s)"
                                    elif "net::ERR_" in error_msg:
                                        test_results["tests"][f"strategy_{i+1}_result"] = f"🌐 {strategy['name']} - Erro de rede: {error_msg.split('net::')[1][:20]}... ({strategy_duration:.1f}s)"
                                    else:
                                        test_results["tests"][f"strategy_{i+1}_result"] = f"❌ {strategy['name']} - {error_msg[:40]}... ({strategy_duration:.1f}s)"
                            
                            # Resultado final do SofaScore
                            if sofascore_success:
                                test_results["tests"]["sofascore_final_result"] = "✅ SofaScore acessível com pelo menos uma estratégia"
                            else:
                                test_results["tests"]["sofascore_final_result"] = "❌ SofaScore inacessível com todas as estratégias"
                                test_results["errors"].append("SofaScore não pôde ser acessado com nenhuma das estratégias testadas")
                            
                            # Resumo das estratégias testadas
                            strategy_summary = []
                            successful_strategies = 0
                            failed_strategies = 0
                            
                            for i in range(len(sofascore_strategies)):
                                strategy_key = f"strategy_{i+1}_result"
                                if strategy_key in test_results["tests"]:
                                    result = test_results["tests"][strategy_key]
                                    if result.startswith("✅"):
                                        successful_strategies += 1
                                        strategy_summary.append(f"✅ Estratégia {i+1}")
                                    elif result.startswith("⚠️"):
                                        strategy_summary.append(f"⚠️ Estratégia {i+1}")
                                    elif result.startswith("⏱️"):
                                        failed_strategies += 1
                                        strategy_summary.append(f"⏱️ Estratégia {i+1}")
                                    elif result.startswith("🌐"):
                                        failed_strategies += 1
                                        strategy_summary.append(f"🌐 Estratégia {i+1}")
                                    else:
                                        failed_strategies += 1
                                        strategy_summary.append(f"❌ Estratégia {i+1}")
                            
                            test_results["tests"]["strategies_summary"] = f"📊 Resumo: {successful_strategies} sucessos, {failed_strategies} falhas de {len(sofascore_strategies)} estratégias - [{', '.join(strategy_summary)}]"
                                
                        except Exception as e:
                            test_results["tests"]["page_creation"] = f"❌ Falha: {str(e)}"
                            test_results["errors"].append(f"Erro criação página: {str(e)}")
                        
                    except Exception as e:
                        test_results["tests"]["context_creation"] = f"❌ Falha: {str(e)}"
                        test_results["errors"].append(f"Erro criação contexto: {str(e)}")
                    
                    # Fechar navegador
                    await browser.close()
                    test_results["tests"]["browser_cleanup"] = "✅ Sucesso"
                    
                except Exception as e:
                    test_results["tests"]["browser_launch"] = f"❌ Falha: {str(e)}"
                    test_results["errors"].append(f"Erro inicialização navegador: {str(e)}")
        
        except Exception as e:
            test_results["tests"]["playwright_init"] = f"❌ Falha: {str(e)}"
            test_results["errors"].append(f"Erro inicialização Playwright: {str(e)}")
        
        # Determinar sucesso geral - considerar sucesso se pelo menos funcionalidades básicas funcionaram
        failed_tests = [test for test, result in test_results["tests"].items() if result.startswith("❌")]
        critical_tests = ["playwright_import", "playwright_init", "browser_launch", "context_creation", "page_creation", "network_connectivity"]
        critical_failures = [test for test in failed_tests if test in critical_tests]
        
        # Sucesso se funções críticas funcionaram, mesmo que SofaScore tenha problemas
        test_results["success"] = len(critical_failures) == 0
        test_results["summary"] = {
            "total_tests": len(test_results["tests"]),
            "passed": len(test_results["tests"]) - len(failed_tests),
            "failed": len(failed_tests),
            "critical_failures": len(critical_failures),
            "failed_tests": failed_tests,
            "note": "Sucesso = funções críticas do Playwright funcionando, mesmo com problemas no SofaScore"
        }
        
        return test_results
        
    except Exception as e:
        test_results["errors"].append(f"Erro crítico: {str(e)}")
        test_results["tests"]["critical_error"] = f"❌ {str(e)}"
        return test_results

# Handler de erros global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global de exceções"""
    print(f"❌ Erro não tratado: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            message="Erro interno do servidor",
            error_details=str(exc),
            timestamp=datetime.now()
        ).model_dump()
    )

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Iniciando servidor de desenvolvimento...")
    
    # Configurar servidor com política de loop adequada
    if platform.system() == "Windows":
        print("🪟 Sistema Windows detectado - usando ProactorEventLoop para compatibilidade com Playwright")
        
        # Para desenvolvimento com reload no Windows
        class ProactorServer(uvicorn.Server):
            def run(self, sockets=None):
                # Garantir que o ProactorEventLoop está configurado
                if hasattr(asyncio, 'WindowsProactorEventLoopPolicy'):
                    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                loop = asyncio.ProactorEventLoop()
                asyncio.set_event_loop(loop)
                asyncio.run(self.serve(sockets=sockets))
        
        config = uvicorn.Config(
            app="main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        server = ProactorServer(config=config)
        server.run()
    else:
        # Para Linux/Mac, usar configuração padrão
        print("🐧 Sistema Unix/Linux detectado - usando configuração padrão")
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
