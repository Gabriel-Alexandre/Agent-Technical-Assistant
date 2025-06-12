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
    ErrorResponse,
    LinksCollectionResponse,
    ScreenshotRequest,
    ScreenshotResponse,
    ScreenshotAnalysisRequest,
    ScreenshotAnalysisResponse,
    ScreenshotAnalysisListResponse,
    ScreenshotAnalysisDetailResponse
)
from services import MatchDataService, SofaScoreLinksService, SofaScoreScreenshotService, ScreenshotAnalysisService
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
    
    # Inicializar serviços
    match_service = MatchDataService()
    links_service = SofaScoreLinksService()
    screenshot_service = SofaScoreScreenshotService()
    analysis_service = ScreenshotAnalysisService()
    
    yield
    
    # Finalização
    pass

# Criar aplicação FastAPI
app = FastAPI(
    title="SofaScore Data Collector API",
    description="""
    ## API de Coleta de Dados do SofaScore para Análise Técnica

    Esta API permite coletar dados em tempo real do SofaScore e gerar análises técnicas automáticas usando IA.

    ### Funcionalidades Ativas:
    - 🔗 **Coleta de Links**: Busca links de partidas na homepage do SofaScore
    - 📸 **Screenshots**: Captura imagens das páginas de partidas
    - 🔍 **Análise Visual**: Análise técnica baseada em screenshots

    ### ⚠️ Funcionalidades em Manutenção:
    - ~~📊 **Dados Completos**: Coleta todos os dados disponíveis de uma partida~~
    - ~~🎯 **Dados Simplificados**: Extrai apenas informações relevantes para análise~~
    - ~~🤖 **Análise com IA**: Gera sugestões táticas usando GPT-4o-mini~~
    - ~~📋 **Histórico**: Recupera histórico de coletas~~

    ### Como usar (Rotas Ativas):
    1. **Coletar Links**: `POST /sofascore/collect-links`
    2. **Screenshot**: `POST /match/{match_identifier}/screenshot`
    3. **Análise Visual**: `POST /match/{match_identifier}/screenshot-analysis`
    4. **Consultar Análises**: `GET /match/{match_id}/screenshot-analyses`

    ### Banco de Dados:
    - Todos os dados são salvos no Supabase
    - Suporte a múltiplas coletas da mesma partida
    - Ideal para monitoramento em tempo real (coleta a cada 30s)
    
    ### Status do Sistema:
    - ✅ **Screenshots e Análise Visual**: Totalmente funcionais
    - ⚠️ **Coleta de Dados Diretos**: Em manutenção temporária
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
links_service = SofaScoreLinksService()
screenshot_service = SofaScoreScreenshotService()
analysis_service = ScreenshotAnalysisService()

@app.get("/", tags=["Status"])
async def root():
    """Endpoint raiz - Status da API"""
    return {
        "message": "🏆 SofaScore Data Collector API",
        "version": "2.0.0",
        "status": "✅ Online",
        "timestamp": datetime.now(),
        "active_endpoints": {
            "collect_links": "/sofascore/collect-links",
            "screenshot": "/match/{match_identifier}/screenshot",
            "screenshot_analysis": "/match/{match_identifier}/screenshot-analysis",
            "list_analyses": "/match/{match_id}/screenshot-analyses",
            "latest_analysis": "/match/{match_id}/screenshot-analysis/latest"
        },
        "disabled_endpoints": {
            "full_data": "/match/{match_id}/full-data [DESABILITADA]",
            "simplified_data": "/match/{match_id}/simplified-data [DESABILITADA]",
            "analysis": "/match/{match_id}/analysis [DESABILITADA]",
            "history": "/match/{match_id}/history [DESABILITADA]"
        },
        "system_status": {
            "screenshots": "✅ Funcionais",
            "visual_analysis": "✅ Funcionais", 
            "data_collection": "⚠️ Em manutenção",
            "database": "✅ Conectado"
        }
    }

@app.get("/health", tags=["Status"])
async def health_check():
    """Verificação de saúde da API"""
    try:
        # Testar conexão com banco
        db_service = DatabaseService()
        db_connected = await db_service.test_connection()
        
        return {
            "status": "healthy" if db_connected else "degraded",
            "timestamp": datetime.now(),
            "services": {
                "database": "✅ Connected" if db_connected else "❌ Connection failed",
                "ai_assistant": "✅ Available" if match_service.assistant else "⚠️ Not configured"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Serviço indisponível: {str(e)}"
        )

@app.get("/test/database", tags=["Status"])
async def test_database_connection():
    """Teste específico de conectividade com o Supabase"""
    try:
        db_service = DatabaseService()
        
        # Teste de conectividade com Supabase
        connectivity_ok = await db_service.test_connection()
        
        if connectivity_ok:
            # Tentar também buscar estatísticas do banco
            try:
                stats = await db_service.get_database_stats()
                return {
                    "status": "success",
                    "message": "Conectividade com Supabase confirmada",
                    "connectivity": True,
                    "database_stats": stats,
                    "timestamp": datetime.now()
                }
            except Exception as stats_error:
                return {
                    "status": "partial",
                    "message": "Conectividade básica OK, mas erro ao obter estatísticas",
                    "connectivity": True,
                    "stats_error": str(stats_error),
                    "timestamp": datetime.now()
                }
        else:
            return {
                "status": "error",
                "message": "Falha na conectividade com Supabase",
                "connectivity": False,
                "timestamp": datetime.now()
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro no teste de conectividade: {str(e)}"
        )

@app.post("/match/{match_id}/full-data", 
          response_model=MatchDataResponse,
          tags=["Rotas Desabilitadas"],
          summary="[DESABILITADA] Obter Dados Completos da Partida",
          description="""
          ⚠️ **ROTA TEMPORARIAMENTE DESABILITADA**
          
          Esta rota está temporariamente desabilitada para manutenção.
          
          ~~Coleta todos os dados disponíveis do SofaScore para uma partida específica.~~
          
          **Status:** Desabilitada
          **Motivo:** Manutenção do sistema
          """,
          include_in_schema=False)
async def get_full_match_data(match_id: str):
    """Endpoint 1: Obter todos os dados do SofaScore para uma partida específica - DESABILITADO"""
    raise HTTPException(
        status_code=503,
        detail="Esta rota está temporariamente desabilitada para manutenção. Use as rotas de screenshot para análise de partidas."
    )
    
    # Código original comentado para manutenção
    # try:
    #     print(f"🎯 Requisição para dados completos - Match ID: {match_id}")
    #     
    #     # Validar match_id
    #     if not match_id or not match_id.isdigit():
    #         raise HTTPException(
    #             status_code=400,
    #             detail="Match ID deve ser um número válido"
    #         )
    #     
    #     # Coletar dados
    #     result = await match_service.get_full_match_data(match_id)
    #     
    #     if result["success"]:
    #         return MatchDataResponse(**result)
    #     else:
    #         raise HTTPException(
    #             status_code=500,
    #             detail=result["message"]
    #         )
    # 
    # except HTTPException:
    #     raise
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500,
    #         detail=f"Erro interno: {str(e)}"
    #     )

@app.post("/match/{match_id}/simplified-data",
          response_model=SimplifiedDataResponse,
          tags=["Rotas Desabilitadas"],
          summary="[DESABILITADA] Obter Dados Simplificados da Partida",
          description="""
          ⚠️ **ROTA TEMPORARIAMENTE DESABILITADA**
          
          Esta rota está temporariamente desabilitada para manutenção.
          
          ~~Coleta e simplifica dados da partida, extraindo apenas informações relevantes para análise técnica.~~
          
          **Status:** Desabilitada
          **Motivo:** Manutenção do sistema
          """,
          include_in_schema=False)
async def get_simplified_match_data(match_id: str):
    """Endpoint 2: Obter dados simplificados para uma partida específica - DESABILITADO"""
    raise HTTPException(
        status_code=503,
        detail="Esta rota está temporariamente desabilitada para manutenção. Use as rotas de screenshot para análise de partidas."
    )
    
    # Código original comentado para manutenção
    # try:
    #     print(f"🎯 Requisição para dados simplificados - Match ID: {match_id}")
    #     
    #     # Validar match_id
    #     if not match_id or not match_id.isdigit():
    #         raise HTTPException(
    #             status_code=400,
    #             detail="Match ID deve ser um número válido"
    #         )
    #     
    #     # Processar dados
    #     result = await match_service.get_simplified_match_data(match_id)
    #     
    #     if result["success"]:
    #         return SimplifiedDataResponse(**result)
    #     else:
    #         raise HTTPException(
    #             status_code=500,
    #             detail=result["message"]
    #         )
    # 
    # except HTTPException:
    #     raise
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500,
    #         detail=f"Erro interno: {str(e)}"
    #     )

@app.post("/match/{match_id}/analysis",
          response_model=AnalysisResponse,
          tags=["Rotas Desabilitadas"],
          summary="[DESABILITADA] Obter Análise Completa com IA",
          description="""
          ⚠️ **ROTA TEMPORARIAMENTE DESABILITADA**
          
          Esta rota está temporariamente desabilitada para manutenção.
          
          ~~Coleta dados da partida, simplifica e gera análise técnica completa usando GPT-4o-mini.~~
          
          **Status:** Desabilitada
          **Motivo:** Manutenção do sistema
          **Alternativa:** Use `/match/{match_identifier}/screenshot-analysis` para análise baseada em screenshot
          """,
          include_in_schema=False)
async def get_match_analysis(match_id: str):
    """Endpoint 3: Obter dados + sugestão do agente para uma partida específica - DESABILITADO"""
    raise HTTPException(
        status_code=503,
        detail="Esta rota está temporariamente desabilitada para manutenção. Use a rota /match/{match_identifier}/screenshot-analysis para análise de partidas."
    )
    
    # Código original comentado para manutenção
    # try:
    #     print(f"🤖 Requisição para análise completa - Match ID: {match_id}")
    #     
    #     # Validar match_id
    #     if not match_id or not match_id.isdigit():
    #         raise HTTPException(
    #             status_code=400,
    #             detail="Match ID deve ser um número válido"
    #         )
    #     
    #     # Verificar se assistente está disponível
    #     if not match_service.assistant:
    #         raise HTTPException(
    #             status_code=503,
    #             detail="Assistente técnico não disponível. Configure OPENAI_API_KEY no arquivo .env"
    #         )
    #     
    #     # Gerar análise completa
    #     result = await match_service.get_match_analysis(match_id)
    #     
    #     if result["success"]:
    #         return AnalysisResponse(**result)
    #     else:
    #         raise HTTPException(
    #             status_code=500,
    #             detail=result["message"]
    #         )
    # 
    # except HTTPException:
    #     raise
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500,
    #         detail=f"Erro interno: {str(e)}"
    #     )

@app.get("/match/{match_id}/history",
         tags=["Rotas Desabilitadas"],
         summary="[DESABILITADA] Histórico de Coletas da Partida",
         description="""
         ⚠️ **ROTA TEMPORARIAMENTE DESABILITADA**
         
         Esta rota está temporariamente desabilitada para manutenção.
         
         ~~Recupera o histórico de coletas de dados de uma partida específica~~
         
         **Status:** Desabilitada
         **Motivo:** Manutenção do sistema
         """,
         include_in_schema=False)
async def get_match_history(match_id: str, limit: int = 10):
    """Endpoint para recuperar histórico de coletas de uma partida - DESABILITADO"""
    raise HTTPException(
        status_code=503,
        detail="Esta rota está temporariamente desabilitada para manutenção."
    )
    
    # Código original comentado para manutenção
    # try:
    #     db_service = DatabaseService()
    #     
    #     # Buscar histórico no banco
    #     history = await db_service.get_match_history(match_id, limit)
    #     
    #     return {
    #         "success": True,
    #         "match_id": match_id,
    #         "total_records": len(history),
    #         "history": history
    #     }
    #     
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500,
    #         detail=f"Erro ao buscar histórico: {str(e)}"
    #     )

@app.post("/sofascore/collect-links",
          response_model=LinksCollectionResponse,
          tags=["Coleta de Links"],
          summary="Coletar Links de Partidas do SofaScore",
          description="""
          Acessa a página inicial do SofaScore e coleta todos os links de partidas disponíveis.
          
          **Processo:**
          1. Acessa a homepage do SofaScore
          2. Coleta todos os links da página
          3. Filtra apenas links de partidas (formato: 7letras#id:8números)
          4. Salva os links filtrados no banco de dados Supabase
          
          **Dados salvos:**
          - URL completa da partida
          - Texto do link
          - Título (se disponível)
          - Match ID extraído
          - Timestamp da coleta
          
          **Uso recomendado:** Para descobrir partidas ativas e monitoramento automático.
          """)
async def collect_sofascore_links():
    """Rota 1: Buscar links no SofaScore e salvar links filtrados no Supabase"""
    try:
        print("🔗 Iniciando coleta de links do SofaScore...")
        
        # Coletar e filtrar links
        result = await links_service.collect_and_filter_links()
        
        if result["success"]:
            return LinksCollectionResponse(**result)
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
            detail=f"Erro interno na coleta de links: {str(e)}"
        )

@app.post("/match/{match_identifier:path}/screenshot",
          response_model=ScreenshotResponse,
          tags=["Screenshots"],
          summary="Capturar Screenshot de Partida",
          description="""
          Captura screenshot da página completa de uma partida específica do SofaScore.
          
          **Parâmetros aceitos:**
          - Match ID (8 dígitos): `13970328`
          - URL completa: `https://www.sofascore.com/pt/football/match/...`
          - Slug da partida: `slovakia-u21-spain-u21/QXbscwc#id:13197555`
          
          **Processo:**
          1. Constrói a URL da partida baseada no identificador
          2. Acessa a página da partida
          3. Captura screenshot da página completa
          4. Salva o arquivo na pasta `screenshots/`
          5. Registra log da partida no banco de dados
          
          **Dados salvos no banco:**
          - Informações da partida (times, URL, match_id)
          - Detalhes do screenshot (nome do arquivo, tamanho)
          - Status da captura
          
          **Modo:** Single (página completa)
          
          **Exemplo de uso:**
          - `/match/slovakia-u21-spain-u21/QXbscwc#id:13197555/screenshot`
          - `/match/13197555/screenshot`
          """)
async def take_match_screenshot(match_identifier: str):
    """Rota 2: Tirar screenshot de uma partida e salvar log no Supabase"""
    try:
        print(f"📸 Iniciando captura de screenshot para: {match_identifier}")
        
        # Capturar screenshot
        result = await screenshot_service.take_match_screenshot(match_identifier)
        
        if result["success"]:
            return ScreenshotResponse(**result)
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
            detail=f"Erro interno na captura de screenshot: {str(e)}"
        )

@app.post("/match/{match_identifier:path}/screenshot-analysis",
          response_model=ScreenshotAnalysisResponse,
          tags=["Análise de Screenshots"],
          summary="Análise Técnica a partir de Screenshot",
          description="""
          Captura screenshot de uma partida e gera análise técnica baseada no contexto visual.
          
          **Processo completo:**
          1. Captura screenshot da página da partida
          2. Extrai informações contextuais (times, match_id, URL)
          3. Gera análise técnica especializada considerando:
             - Situação atual da partida
             - Contexto tático observável
             - Recomendações para ambos os times
             - Alertas críticos
             - Previsão tática
          
          **Análise inclui:**
          - 📊 Situação atual da partida
          - 🎯 Análise visual do screenshot
          - ⚽ Contexto tático
          - 🔍 Recomendações técnicas específicas
          - ⚠️ Alertas críticos
          - 📈 Previsão tática
          
          **Requisitos:** 
          - Playwright funcionando para captura
          - Screenshot salvo com sucesso
          
          **Nota:** Esta análise é baseada no contexto da partida e informações visuais disponíveis no momento da captura.
          """)
async def analyze_match_from_screenshot(match_identifier: str):
    """Rota 3: Análise técnica do momento da partida a partir do screenshot"""
    try:
        print(f"🤖 Iniciando análise técnica via screenshot para: {match_identifier}")
        
        # Gerar análise a partir do screenshot
        result = await analysis_service.analyze_match_from_screenshot(match_identifier)
        
        if result["success"]:
            return ScreenshotAnalysisResponse(**result)
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
            detail=f"Erro interno na análise de screenshot: {str(e)}"
        )

# Novas rotas para consultar análises de screenshot
@app.get("/match/{match_id}/screenshot-analyses",
         response_model=ScreenshotAnalysisListResponse,
         tags=["Análise de Screenshots"],
         summary="Listar Análises de Screenshot de uma Partida",
         description="""
         Recupera todas as análises de screenshot realizadas para uma partida específica.
         
         **Retorna:**
         - Lista de análises ordenadas por data (mais recente primeiro)
         - Informações básicas de cada análise
         - Metadados da análise
         - Timestamps de criação
         
         **Parâmetros:**
         - match_id: ID da partida (8 dígitos)
         - limit: Número máximo de análises a retornar (padrão: 10)
         """)
async def get_match_screenshot_analyses(match_id: str, limit: int = 10):
    """Recupera análises de screenshot de uma partida específica"""
    try:
        database = DatabaseService()
        analyses = await database.get_screenshot_analysis(match_id, limit)
        
        return ScreenshotAnalysisListResponse(
            success=True,
            message=f"Encontradas {len(analyses)} análise(s) para a partida {match_id}",
            data=analyses,
            total_analyses=len(analyses),
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar análises: {str(e)}"
        )

@app.get("/match/{match_id}/screenshot-analysis/latest",
         response_model=ScreenshotAnalysisDetailResponse,
         tags=["Análise de Screenshots"],
         summary="Obter Análise de Screenshot Mais Recente",
         description="""
         Recupera a análise de screenshot mais recente de uma partida específica.
         
         **Retorna:**
         - Análise completa mais recente
         - Texto da análise técnica
         - Informações da partida
         - Metadados da análise
         """)
async def get_latest_screenshot_analysis(match_id: str):
    """Recupera a análise de screenshot mais recente de uma partida"""
    try:
        database = DatabaseService()
        analysis = await database.get_latest_screenshot_analysis(match_id)
        
        if not analysis:
            raise HTTPException(
                status_code=404,
                detail=f"Nenhuma análise de screenshot encontrada para a partida {match_id}"
            )
        
        return ScreenshotAnalysisDetailResponse(
            success=True,
            message="Análise mais recente recuperada com sucesso",
            analysis_data=analysis,
            match_info={
                "match_id": analysis.get("match_id"),
                "home_team": analysis.get("home_team"),
                "away_team": analysis.get("away_team"),
                "match_url": analysis.get("match_url")
            },
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar análise mais recente: {str(e)}"
        )

@app.get("/screenshot-analyses",
         response_model=ScreenshotAnalysisListResponse,
         tags=["Análise de Screenshots"],
         summary="Listar Todas as Análises de Screenshot",
         description="""
         Recupera todas as análises de screenshot realizadas no sistema.
         
         **Retorna:**
         - Lista de todas as análises ordenadas por data
         - Informações básicas de cada análise
         - Filtros por tipo de análise
         - Paginação com limite configurável
         """)
async def get_all_screenshot_analyses(limit: int = 50):
    """Recupera todas as análises de screenshot do sistema"""
    try:
        database = DatabaseService()
        analyses = await database.get_all_screenshot_analyses(limit)
        
        return ScreenshotAnalysisListResponse(
            success=True,
            message=f"Encontradas {len(analyses)} análise(s) no sistema",
            data=analyses,
            total_analyses=len(analyses),
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar análises: {str(e)}"
        )

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
