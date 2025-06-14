"""
Modelos Pydantic para a API de Coleta de Dados do SofaScore
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class MatchDataRequest(BaseModel):
    """Modelo para requisição de dados de partida"""
    match_id: str = Field(..., description="ID da partida no SofaScore")

class MatchDataResponse(BaseModel):
    """Modelo para resposta de dados completos da partida"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    record_id: Optional[str] = None
    timestamp: datetime

class SimplifiedDataResponse(BaseModel):
    """Modelo para resposta de dados simplificados"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    record_id: Optional[str] = None
    timestamp: datetime

class AnalysisResponse(BaseModel):
    """Modelo para resposta com análise do agente técnico"""
    success: bool
    message: str
    match_data: Optional[Dict[str, Any]] = None
    simplified_data: Optional[Dict[str, Any]] = None
    analysis: Optional[str] = None
    record_id: Optional[str] = None
    timestamp: datetime

class ErrorResponse(BaseModel):
    """Modelo para respostas de erro"""
    success: bool = False
    message: str
    error_details: Optional[str] = None
    timestamp: datetime

# Novos modelos para as tabelas adicionais

class FilteredLinksRequest(BaseModel):
    """Modelo para requisição de salvamento de links filtrados"""
    collection_timestamp: str = Field(..., description="Timestamp da coleta")
    source_file: str = Field(..., description="Arquivo fonte dos links")
    pattern_used: str = Field(..., description="Padrão regex usado")
    links_data: List[Dict[str, Any]] = Field(..., description="Lista de links filtrados")

class FilteredLinksResponse(BaseModel):
    """Modelo para resposta de links filtrados"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    record_id: Optional[str] = None
    total_links: Optional[int] = None
    timestamp: datetime

class MatchInfoRequest(BaseModel):
    """Modelo para requisição de informações da partida"""
    match_id: str = Field(..., description="ID da partida")
    url_complete: str = Field(..., description="URL completa da partida")
    url_slug: Optional[str] = Field(None, description="Slug da URL")
    title: Optional[str] = Field(None, description="Título da partida")
    home_team: Optional[str] = Field(None, description="Time da casa")
    away_team: Optional[str] = Field(None, description="Time visitante")
    tournament: Optional[str] = Field(None, description="Torneio/competição")
    match_date: Optional[str] = Field(None, description="Data da partida (ISO format)")
    status: Optional[str] = Field(None, description="Status da partida")

class MatchInfoResponse(BaseModel):
    """Modelo para resposta de informações da partida"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    record_id: Optional[str] = None
    timestamp: datetime

class MatchInfoListResponse(BaseModel):
    """Modelo para resposta de lista de partidas"""
    success: bool
    message: str
    data: Optional[List[Dict[str, Any]]] = None
    total_matches: Optional[int] = None
    timestamp: datetime

class MatchStatusUpdateRequest(BaseModel):
    """Modelo para atualização de status da partida"""
    match_id: str = Field(..., description="ID da partida")
    status: str = Field(..., description="Novo status da partida")

class MatchStatusUpdateResponse(BaseModel):
    """Modelo para resposta de atualização de status"""
    success: bool
    message: str
    match_id: str
    new_status: str
    timestamp: datetime

class DatabaseStatsResponse(BaseModel):
    """Modelo para resposta de estatísticas do banco"""
    success: bool
    message: str
    stats: Optional[Dict[str, Any]] = None
    timestamp: datetime

# Novos modelos para as rotas de links, screenshots e análise

# Modelo para partida detalhada
class DetailedMatch(BaseModel):
    """Modelo para partidas com informações detalhadas extraídas"""
    home_team: str = Field(description="Nome do time da casa")
    away_team: str = Field(description="Nome do time visitante") 
    home_score: str = Field(description="Placar do time da casa")
    away_score: str = Field(description="Placar do time visitante")
    match_time: str = Field(description="Horário da partida ou tempo atual do jogo")
    match_status: str = Field(description="Status da partida: not_started, in_progress, finished, postponed")
    url: str = Field(description="URL da partida no SofaScore")

class LinksCollectionResponse(BaseModel):
    """Modelo para resposta de coleta de links do SofaScore com detalhes das partidas"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class LatestLinksResponse(BaseModel):
    """Modelo para resposta da coleta de links mais recente com detalhes das partidas"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    collection_info: Optional[Dict[str, Any]] = None
    timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ScreenshotRequest(BaseModel):
    """Modelo para requisição de screenshot"""
    match_identifier: str = Field(..., description="Identificador da partida (ID, URL ou slug)")

class ScreenshotResponse(BaseModel):
    """Modelo para resposta de screenshot"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime

class ScreenshotAnalysisRequest(BaseModel):
    """Modelo para requisição de análise de dados de partida"""
    match_identifier: str = Field(..., description="Identificador da partida para extrair dados e analisar")

class ScreenshotAnalysisResponse(BaseModel):
    """Modelo para resposta de análise de dados de partida"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ScreenshotAnalysisData(BaseModel):
    """Modelo para dados de análise baseada em scrapping"""
    match_id: str
    match_identifier: str
    match_url: str
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    analysis_text: str
    analysis_type: str = "data_scraping_analysis"
    analysis_metadata: Optional[Dict[str, Any]] = None

class ScreenshotAnalysisListResponse(BaseModel):
    """Modelo para resposta de lista de análises de dados"""
    success: bool
    message: str
    data: Optional[List[Dict[str, Any]]] = None
    total_analyses: Optional[int] = None
    timestamp: datetime

class ScreenshotAnalysisDetailResponse(BaseModel):
    """Modelo para resposta detalhada de análise de dados"""
    success: bool
    message: str
    analysis_data: Optional[Dict[str, Any]] = None
    match_info: Optional[Dict[str, Any]] = None
    timestamp: datetime 