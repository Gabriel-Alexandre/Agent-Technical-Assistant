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