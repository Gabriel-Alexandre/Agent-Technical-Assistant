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
         - Testa acesso ao SofaScore
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
                
                # Testar criação do navegador
                try:
                    browser = await playwright.chromium.launch(
                        headless=True,
                        args=[
                            '--no-sandbox',
                            '--disable-setuid-sandbox',
                            '--disable-dev-shm-usage',
                            '--disable-gpu',
                            '--disable-extensions'
                        ]
                    )
                    
                    browser_version = await browser.version()
                    test_results["tests"]["browser_launch"] = f"✅ Sucesso - Versão: {browser_version}"
                    test_results["system_info"]["browser_version"] = browser_version
                    
                    # Testar criação de contexto
                    try:
                        context = await browser.new_context(
                            viewport={'width': 1920, 'height': 1080},
                            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        )
                        test_results["tests"]["context_creation"] = "✅ Sucesso"
                        
                        # Testar criação de página
                        try:
                            page = await context.new_page()
                            test_results["tests"]["page_creation"] = "✅ Sucesso"
                            
                            # Testar acesso ao Google
                            try:
                                response = await page.goto('https://www.google.com', timeout=15000)
                                google_title = await page.title()
                                test_results["tests"]["google_access"] = f"✅ Sucesso - Status: {response.status}, Título: {google_title}"
                                
                                # Testar acesso ao SofaScore
                                try:
                                    sofascore_response = await page.goto('https://www.sofascore.com', timeout=15000)
                                    sofascore_title = await page.title()
                                    test_results["tests"]["sofascore_access"] = f"✅ Sucesso - Status: {sofascore_response.status}, Título: {sofascore_title[:50]}..."
                                    
                                    # Testar acesso a API do SofaScore
                                    try:
                                        api_response = await page.goto('https://www.sofascore.com/api/v1/sport/football/events/live', timeout=15000)
                                        test_results["tests"]["sofascore_api"] = f"✅ API acessível - Status: {api_response.status}"
                                        
                                        if api_response.status == 200:
                                            content = await page.content()
                                            if '{' in content and '}' in content:
                                                test_results["tests"]["sofascore_api_json"] = "✅ JSON detectado na resposta"
                                            else:
                                                test_results["tests"]["sofascore_api_json"] = "⚠️ JSON não detectado"
                                        
                                    except Exception as e:
                                        test_results["tests"]["sofascore_api"] = f"❌ Falha: {str(e)}"
                                        test_results["errors"].append(f"Erro API SofaScore: {str(e)}")
                                    
                                except Exception as e:
                                    test_results["tests"]["sofascore_access"] = f"❌ Falha: {str(e)}"
                                    test_results["errors"].append(f"Erro acesso SofaScore: {str(e)}")
                                
                            except Exception as e:
                                test_results["tests"]["google_access"] = f"❌ Falha: {str(e)}"
                                test_results["errors"].append(f"Erro acesso Google: {str(e)}")
                            
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
        
        # Determinar sucesso geral
        failed_tests = [test for test, result in test_results["tests"].items() if result.startswith("❌")]
        test_results["success"] = len(failed_tests) == 0
        test_results["summary"] = {
            "total_tests": len(test_results["tests"]),
            "passed": len(test_results["tests"]) - len(failed_tests),
            "failed": len(failed_tests),
            "failed_tests": failed_tests
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
