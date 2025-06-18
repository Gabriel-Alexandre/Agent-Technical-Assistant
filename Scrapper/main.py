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
from typing import Dict, Any, List
from urllib.parse import unquote

# Importar modelos e serviços
from models import (
    MatchDataRequest, 
    MatchDataResponse, 
    SimplifiedDataResponse, 
    AnalysisResponse, 
    ErrorResponse,
    LinksCollectionResponse,
    LatestLinksResponse,
    ScreenshotRequest,
    ScreenshotResponse,
    ScreenshotAnalysisRequest,
    ScreenshotAnalysisResponse,
    ScreenshotAnalysisListResponse,
    ScreenshotAnalysisDetailResponse,
    DatabaseStatsResponse,
    MatchInfoResponse,
    MatchInfoListResponse,
    MatchStatusUpdateResponse
)
from services import (
    MatchDataService, 
    SofaScoreLiveCollectorAPI, 
    SofaScoreLinksService,
    SofaScoreScreenshotService,
    MatchDataScrapingService  # Novo serviço para análise de dados
)
from database_service import DatabaseService

# Variáveis globais para serviços (inicializadas no lifespan)
match_service = None
simplifier_service = None
analysis_service = None  # Agora será MatchDataScrapingService
links_service = None
screenshot_service = None
database_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    global match_service, simplifier_service, analysis_service, links_service, screenshot_service, database_service
    
    print("🚀 Inicializando serviços da aplicação...")
    
    try:
        # Inicializar DatabaseService
        print("💾 Inicializando DatabaseService...")
        database_service = DatabaseService()
        
        # Verificar se as tabelas existem e criá-las se necessário
        try:
            await database_service.create_tables_if_not_exist()
            print("✅ DatabaseService inicializado com sucesso!")
        except Exception as e:
            print(f"⚠️ Erro ao inicializar DatabaseService: {e}")
            print("⚠️ Aplicação continuará sem banco de dados")
        
        # Inicializar outros serviços
        print("🔧 Inicializando serviços principais...")
        match_service = MatchDataService()
        analysis_service = MatchDataScrapingService()  # Novo serviço de scraping
        links_service = SofaScoreLinksService()
        screenshot_service = SofaScoreScreenshotService()
        
        print("✅ Todos os serviços inicializados com sucesso!")
        
        yield
        
    except Exception as e:
        print(f"❌ Erro durante inicialização dos serviços: {e}")
        yield
    finally:
        print("🔄 Finalizando serviços...")
        # Cleanup quando a aplicação for encerrada

# Criar aplicação FastAPI
app = FastAPI(
    title="SofaScore Football Data Collector API",
    description="""
    ## API de Coleta de Dados de FUTEBOL do SofaScore para Análise Técnica

    Esta API permite coletar dados em tempo real do SofaScore (APENAS FUTEBOL) e gerar análises técnicas automáticas usando IA.

    ### Funcionalidades Ativas:
    - ⚽ **Coleta Detalhada de Partidas**: Extrai informações completas (times, placares, tempo, status) de partidas de futebol
    - 📋 **Partidas Recentes Detalhadas**: Recupera a coleta mais recente com dados completos das partidas
    - 📸 **Screenshots**: Captura imagens das páginas de partidas
    - 🔍 **Análise Visual**: Análise técnica baseada em screenshots

    ### ⚠️ Funcionalidades em Manutenção:
    - ~~📊 **Dados Completos**: Coleta todos os dados disponíveis de uma partida~~
    - ~~🎯 **Dados Simplificados**: Extrai apenas informações relevantes para análise~~
    - ~~🤖 **Análise com IA**: Gera sugestões táticas usando GPT-4o-mini~~
    - ~~📋 **Histórico**: Recupera histórico de coletas~~

    ### 🔥 EXTRAÇÃO INTELIGENTE DE DADOS:
    - ✅ **Inclui**: Partidas de futebol com informações completas (times, placares, tempo)
    - ❌ **Exclui**: Basquete, tênis, vôlei, e-sports, etc.
    - 🎯 **Método**: Análise de elementos HTML específicos do SofaScore
    - 📊 **Dados**: Times, placares, tempo, status, torneio, URLs

    ### Como usar (Rotas Ativas):
    1. **Coletar Partidas Detalhadas**: `POST /sofascore/collect-links` - Extrai dados completos das partidas
    2. **Partidas Recentes Detalhadas**: `GET /sofascore/latest-links` - Recupera dados da última coleta
    3. **Screenshot**: `POST /match/{match_identifier}/screenshot` - Captura imagem da partida
    4. **Análise Visual**: `POST /match/{match_identifier}/screenshot-analysis` - Análise técnica
    5. **Consultar Análises**: `GET /match/{match_id}/screenshot-analyses` - Histórico de análises

    ### Banco de Dados:
    - Todos os dados são salvos no Supabase
    - Suporte a múltiplas coletas da mesma partida
    - Ideal para monitoramento em tempo real (coleta a cada 30s)
    - Identificação automática do esporte (football)
    
    ### Status do Sistema:
    - ✅ **Screenshots e Análise Visual**: Totalmente funcionais
    - ✅ **Filtro de Futebol**: Ativo e funcionando
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

@app.get("/", tags=["Status"])
async def root():
    """Endpoint raiz - Status da API"""
    return {
        "message": "⚽ SofaScore Football Data Collector API",
        "version": "2.0.0",
        "status": "✅ Online",
        "timestamp": datetime.now(),
        "sport_filter": "⚽ APENAS FUTEBOL",
        "active_endpoints": {
            "collect_football_links": "/sofascore/collect-links",
            "latest_football_links": "/sofascore/latest-links",
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
            "detailed_match_collection": "✅ Funcionais (extração completa de dados)",
            "latest_detailed_matches": "✅ Funcionais (dados completos das partidas)",
            "screenshots": "✅ Funcionais",
            "visual_analysis": "✅ Funcionais", 
            "sport_filter": "✅ Ativo (apenas futebol)",
            "data_extraction": "✅ Melhorado (times, placares, tempo, status)",
            "database": "✅ Conectado"
        },
        "extraction_features": {
            "included_sports": ["football"],
            "excluded_sports": ["basketball", "tennis", "volleyball", "esports", "others"],
            "extracted_data": ["home_team", "away_team", "home_score", "away_score", "match_time", "match_status", "tournament", "match_id", "url"],
            "extraction_method": "CSS_selectors_based_on_SofaScore_HTML_structure"
        }
    }

@app.get("/health", tags=["Status"])
async def health_check():
    """Verificação de saúde da API"""
    try:
        # Testar conexão com banco
        db_connected = await database_service.test_connection()
        
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
        # Teste de conectividade com Supabase
        connectivity_ok = await database_service.test_connection()
        
        if connectivity_ok:
            # Tentar também buscar estatísticas do banco
            try:
                stats = await database_service.get_database_stats()
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

@app.post("/sofascore/collect-links", response_model=LinksCollectionResponse)
async def collect_links():
    """
    🔗 **Coleta Links da Homepage do SofaScore com Detalhes de Partidas**
    
    **FUNCIONALIDADE PRINCIPAL:**
    - Acessa a homepage do SofaScore (https://www.sofascore.com/)
    - Extrai informações detalhadas de partidas de FUTEBOL em tempo real
    - Identifica automaticamente diferentes estados das partidas
    - Ignora partidas sem informações válidas de times
    
    **INFORMAÇÕES EXTRAÍDAS POR PARTIDA:**
    - ⚽ **Times**: Nome do time da casa e visitante
    - 🏆 **Placares**: Gols de cada time (ou status especial)
    - ⏰ **Tempo**: Horário de início, minuto atual, ou tempo da partida
    - 📊 **Status**: Estado atual da partida
    - 🔗 **URL**: Link direto para a partida no SofaScore
    
    **ESTADOS DE PARTIDA SUPORTADOS:**
    - 🔴 **in_progress**: Partida em andamento (mostra minuto atual e placar)
    - ⏳ **not_started**: Partida não iniciada (placares 0-0)
    - ✅ **finished**: Partida finalizada (placar final)
    - ⏸️ **postponed**: Partida adiada
    
    **MELHORIAS IMPLEMENTADAS:**
    - ✅ Múltiplos seletores CSS para diferentes tipos de partida
    - ✅ Lógica robusta para partidas finalizadas baseada em exemplos reais
    - ✅ Validação crítica: ignora partidas sem nomes de times
    - ✅ Extração otimizada de placares para jogos finalizados
    - ✅ Logs limpos e informativos
    
    **RETORNO:**
    - Lista de partidas com informações detalhadas
    - Estatísticas da coleta
    - Exemplos das partidas encontradas
    - ID do registro salvo no banco de dados
    
    **EXEMPLO DE PARTIDA RETORNADA:**
    ```json
    {
        "home_team": "Derry City",
        "away_team": "Galway Utd", 
        "home_score": "1",
        "away_score": "1",
        "match_time": "15:45",
        "match_status": "finished",
        "url": "https://www.sofascore.com/pt/football/match/..."
    }
    ```
    
    **OBSERVAÇÕES:**
    - Foco exclusivo em partidas de futebol
    - Dados coletados em tempo real da homepage
    - Partidas inválidas são automaticamente filtradas
    - Sistema otimizado para diferentes layouts do SofaScore
    """
    try:
        print("🚀 [COLLECT-LINKS] Iniciando rota /sofascore/collect-links")
        print(f"🔍 [COLLECT-LINKS] Timestamp: {datetime.now()}")
        print(f"🔧 [COLLECT-LINKS] Verificando se links_service está inicializado: {links_service is not None}")
        
        if links_service is None:
            print("❌ [COLLECT-LINKS] ERRO: links_service não foi inicializado!")
            raise HTTPException(
                status_code=500,
                detail="Serviço de coleta de links não foi inicializado corretamente"
            )
        
        print("⚽ [COLLECT-LINKS] Iniciando coleta DETALHADA de partidas de FUTEBOL do SofaScore...")
        
        # Coletar informações detalhadas das partidas (apenas futebol)
        print("🔄 [COLLECT-LINKS] Chamando links_service.collect_and_filter_links()...")
        result = await links_service.collect_and_filter_links()
        
        print(f"✅ [COLLECT-LINKS] Resultado recebido: success={result.get('success', 'N/A')}")
        
        if result["success"]:
            print(f"🎉 [COLLECT-LINKS] Coleta bem-sucedida! Retornando resposta...")
            return LinksCollectionResponse(**result)
        else:
            print(f"❌ [COLLECT-LINKS] Coleta falhou: {result.get('message', 'Erro desconhecido')}")
            raise HTTPException(
                status_code=500,
                detail=result["message"]
            )
    
    except HTTPException as he:
        print(f"⚠️ [COLLECT-LINKS] HTTPException capturada: {he.detail}")
        raise
    except Exception as e:
        print(f"💥 [COLLECT-LINKS] Exceção não tratada: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"📋 [COLLECT-LINKS] Traceback completo:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno na coleta detalhada de partidas de futebol: {str(e)}"
        )

@app.get("/sofascore/latest-links",
         response_model=LatestLinksResponse,
         tags=["Coleta de Links"],
         summary="Obter Coleta de Links de FUTEBOL Mais Recente",
         description="""
         Retorna a coleta de partidas de FUTEBOL mais recente com informações DETALHADAS.
         
         **Retorna Informações Completas:**
         - 📊 **Partidas detalhadas** da coleta mais recente
         - 🕐 **Informações em tempo real** (times, placares, tempo)
         - 📈 **Estatísticas da coleta** (total, match IDs únicos, etc.)
         - 🎯 **Amostra das primeiras partidas** para visualização rápida
         
         **Dados Detalhados Incluídos:**
         - `detailed_matches`: Lista completa de partidas com:
           - Nomes dos times (casa e visitante)
           - Placar atual de cada time
           - Tempo da partida (horário ou minuto)
           - Status da partida (não iniciada, em andamento, etc.)
           - Torneio/competição
           - Match ID e URLs completas
         - `collection_info`: Metadados da coleta (timestamp, método, etc.)
         - `statistics`: Estatísticas da coleta (total de partidas, etc.)
         
         **Exemplo de Dados Retornados:**
         ```json
         {
           "detailed_matches": [
             {
               "home_team": "Paysandu",
               "away_team": "Botafogo-SP", 
               "home_score": "1",
               "away_score": "0",
               "match_time": "45'",
               "match_status": "in_progress",
               "tournament": "Série B",
               "match_id": "13616175",
               "url": "https://www.sofascore.com/pt/football/match/..."
             }
           ]
         }
         ```
         
         **Uso recomendado:** Verificar partidas em andamento sem executar nova coleta.
         """)
async def get_latest_sofascore_links():
    """Rota GET: Buscar a coleta de partidas de FUTEBOL mais recente com informações detalhadas do banco de dados"""
    try:
        print("⚽ Buscando coleta DETALHADA de partidas de FUTEBOL mais recente...")
        
        # Buscar coleta mais recente com dados detalhados (apenas futebol)
        result = await links_service.get_latest_links_collection()
        
        if result["success"]:
            return LatestLinksResponse(**result)
        else:
            raise HTTPException(
                status_code=404 if "Nenhuma coleta" in result["message"] else 500,
                detail=result["message"]
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao buscar coleta detalhada de futebol mais recente: {str(e)}"
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
          tags=["Análise de Partidas"],
          summary="Análise Técnica a partir de Dados da Partida",
          description="""
          Acessa a página da partida, extrai dados em tempo real e gera análise técnica especializada.
          
          **Processo completo:**
          1. Acessa a página da partida no SofaScore
          2. Extrai dados estruturados (estatísticas, eventos, placar)
          3. Filtra informações relevantes para análise técnica
          4. Gera análise técnica especializada considerando:
             - Situação atual da partida
             - Estatísticas em tempo real
             - Eventos importantes
             - Recomendações técnicas diretas
             - Justificativas baseadas em dados
          
          **Análise inclui:**
          - 📊 Dados atuais da partida (placar, tempo, status)
          - 📈 Estatísticas detalhadas (posse, finalizações, passes, etc.)
          - ⚽ Eventos importantes (cartões, faltas, grandes chances)
          - 🎯 Recomendações específicas para cada time
          - ⚠️ Análise baseada em dados reais extraídos
          
          **Vantagens:**
          - Análise baseada em dados precisos e atualizados
          - Recomendações diretas e justificadas
          - Processamento rápido sem armazenamento intermediário
          - Informações extraídas diretamente da fonte
          
          **Requisitos:** 
          - Playwright funcionando para acesso à página
          - Partida ativa ou recente no SofaScore
          
          **Nota:** Esta análise é baseada em dados reais extraídos da página da partida no momento da consulta.
          """)
async def analyze_match_from_scraping(match_identifier: str):
    """Análise técnica da partida baseada em scrapping de dados em tempo real"""
    try:
        print(f"🤖 Iniciando análise técnica via scrapping para: {match_identifier}")
        
        # Gerar análise a partir dos dados extraídos
        result = await analysis_service.analyze_match_from_scraping(match_identifier)
        
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
            detail=f"Erro interno na análise de dados: {str(e)}"
        )

# Rotas para consultar análises de dados
@app.get("/match/{match_id}/screenshot-analyses",
         response_model=ScreenshotAnalysisListResponse,
         tags=["Análise de Partidas"],
         summary="Listar Análises de Dados de uma Partida",
         description="""
         Recupera todas as análises baseadas em dados realizadas para uma partida específica.
         
         **Retorna:**
         - Lista de análises ordenadas por data (mais recente primeiro)
         - Informações básicas de cada análise
         - Metadados da análise (estatísticas extraídas, eventos)
         - Timestamps de criação
         
         **Parâmetros:**
         - match_id: ID da partida (8 dígitos)
         - limit: Número máximo de análises a retornar (padrão: 10)
         """)
async def get_match_data_analyses(match_id: str, limit: int = 10):
    """Recupera análises de dados de uma partida específica"""
    try:
        database = DatabaseService()
        analyses = await database.get_screenshot_analysis(match_id, limit)
        
        return ScreenshotAnalysisListResponse(
            success=True,
            message=f"Encontradas {len(analyses)} análise(s) de dados para a partida {match_id}",
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
         tags=["Análise de Partidas"],
         summary="Obter Análise de Dados Mais Recente",
         description="""
         Recupera a análise baseada em dados mais recente de uma partida específica.
         
         **Retorna:**
         - Análise completa mais recente
         - Texto da análise técnica
         - Informações da partida
         - Metadados da análise (estatísticas, eventos)
         """)
async def get_latest_data_analysis(match_id: str):
    """Recupera a análise de dados mais recente de uma partida"""
    try:
        database = DatabaseService()
        analysis = await database.get_latest_screenshot_analysis(match_id)
        
        if not analysis:
            raise HTTPException(
                status_code=404,
                detail=f"Nenhuma análise de dados encontrada para a partida {match_id}"
            )
        
        return ScreenshotAnalysisDetailResponse(
            success=True,
            message="Análise de dados mais recente recuperada com sucesso",
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
         tags=["Análise de Partidas"],
         summary="Listar Todas as Análises de Dados",
         description="""
         Recupera todas as análises baseadas em dados realizadas no sistema.
         
         **Retorna:**
         - Lista de todas as análises ordenadas por data
         - Informações básicas de cada análise
         - Tipos de análise (data_scraping_analysis)
         - Paginação com limite configurável
         """)
async def get_all_data_analyses(limit: int = 50):
    """Recupera todas as análises de dados do sistema"""
    try:
        database = DatabaseService()
        analyses = await database.get_all_screenshot_analyses(limit)
        
        return ScreenshotAnalysisListResponse(
            success=True,
            message=f"Encontradas {len(analyses)} análise(s) de dados no sistema",
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
