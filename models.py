"""Modèles de données pour l'analyse d'appels."""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum


class ProblemType(str, Enum):
    """Types de problèmes détectés."""
    NONE = "none"
    PARSING_ERROR = "parsing_error"
    API_ERROR = "api_error"
    MISUNDERSTANDING = "misunderstanding"
    MISSING_INFO = "missing_info"
    TECHNICAL_ERROR = "technical_error"
    OTHER = "other"


class CallMetadata(BaseModel):
    """Métadonnées d'un appel."""
    call_id: str
    duration: Optional[int] = None
    status: Optional[str] = None
    triggered_tool: Optional[str] = None
    timestamp: Optional[str] = None
    agent_id: Optional[str] = None


class ConversationTurn(BaseModel):
    """Un tour de conversation."""
    role: str  # "user" ou "assistant"
    content: str
    timestamp: Optional[str] = None


class ToolResult(BaseModel):
    """Résultat d'un outil."""
    tool_name: str
    input: Dict[str, Any]
    output: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None
    timestamp: Optional[str] = None


class CallAnalysisRequest(BaseModel):
    """Requête pour analyser un appel."""
    call_id: str
    conversation: List[ConversationTurn]
    tool_results: List[ToolResult]
    metadata: Optional[CallMetadata] = None


class Question(BaseModel):
    """Question pour l'analyse détaillée."""
    id: str
    question: str
    type: str  # "multiple_choice" ou "open_ended"
    options: Optional[List[str]] = None  # Pour multiple_choice


class AnalysisStep(BaseModel):
    """Une étape d'analyse."""
    step_number: int
    description: str
    questions: List[Question]
    

class DetailedAnalysis(BaseModel):
    """Analyse détaillée d'un appel."""
    call_id: str
    problem_type: str
    problem_detected: bool
    steps: List[AnalysisStep]
    tags: List[str]
    summary: str
    recommendations: List[str]


class InitialAnalysis(BaseModel):
    """Analyse initiale pour détection d'erreurs."""
    has_error: bool
    error_type: Optional[ProblemType] = None
    error_description: Optional[str] = None
    confidence: float  # Entre 0 et 1
    context: Dict[str, Any]

