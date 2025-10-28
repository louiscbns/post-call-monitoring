"""Module de détection initiale d'erreurs."""
from typing import Dict, List, Any
from models import (
    CallAnalysisRequest, 
    InitialAnalysis, 
    ProblemType,
    ConversationTurn,
    ToolResult
)
from llm_clients import LLMClient
import json


class ErrorDetector:
    """Détecte les erreurs dans les appels."""
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.llm = LLMClient(model_name)
        self.model_name = model_name
    
    def detect_errors(self, request: CallAnalysisRequest) -> InitialAnalysis:
        """Détecte les erreurs dans un appel."""
        
        # Contexte pour l'analyse
        context = self._build_context(request)
        
        # Prompt pour la détection
        system_prompt = self._get_system_prompt()
        user_prompt = self._build_detection_prompt(request, context)
        
        # Appel au LLM
        response = self.llm.generate(
            user_prompt, 
            system_prompt,
            temperature=0.2,  # Faible température pour la détection
            max_tokens=500
        )
        
        # Parse la réponse
        analysis = self._parse_detection_response(response, context)
        
        return analysis
    
    def _build_context(self, request: CallAnalysisRequest) -> Dict[str, Any]:
        """Construit le contexte d'analyse."""
        return {
            "call_id": request.call_id,
            "conversation_length": len(request.conversation),
            "tool_calls_count": len(request.tool_results),
            "successful_tools": sum(1 for t in request.tool_results if t.success),
            "failed_tools": sum(1 for t in request.tool_results if not t.success),
            "metadata": request.metadata.dict() if request.metadata else None
        }
    
    def _get_system_prompt(self) -> str:
        """Retourne le prompt système pour la détection."""
        return """Tu es un expert en analyse de conversations clients.

Ta tâche est de détecter les ERREURS et PROBLÈMES dans les appels analysés.

Types d'erreurs à détecter:
- parsing_error: Erreur lors du parsing des données
- api_error: Erreur API (retour vide, timeout, erreur HTTP)
- misunderstanding: Malentendu entre client et agent
- missing_info: Information manquante pour continuer
- technical_error: Erreur technique (timeout, crash, etc.)
- other: Autre type de problème

Réponds UNIQUEMENT avec un JSON valide au format:
{
    "has_error": true/false,
    "error_type": "none" ou "parsing_error" ou "api_error" etc,
    "error_description": "description courte du problème",
    "confidence": 0.0 à 1.0,
    "key_indicators": ["indicateur1", "indicateur2"]
}"""
    
    def _build_detection_prompt(self, request: CallAnalysisRequest, context: Dict) -> str:
        """Construit le prompt utilisateur pour la détection."""
        
        # Format conversation
        conv_text = "CONVERSATION:\n"
        for turn in request.conversation:
            role_emoji = "👤" if turn.role == "user" else "🤖"
            conv_text += f"{role_emoji} [{turn.role}]: {turn.content}\n\n"
        
        # Format tool results
        tools_text = "RÉSULTATS OUTILS:\n"
        for tool_result in request.tool_results:
            status = "✅" if tool_result.success else "❌"
            tools_text += f"{status} {tool_result.tool_name}:\n"
            tools_text += f"  Input: {json.dumps(tool_result.input, indent=2)}\n"
            
            if not tool_result.success:
                tools_text += f"  ❌ Erreur: {tool_result.error_message}\n"
            else:
                tools_text += f"  Output: {json.dumps(tool_result.output, indent=2)}\n"
            tools_text += "\n"
        
        prompt = f"""Analyse cet appel pour détecter des erreurs:

{conv_text}
---
{tools_text}
---
CONTEXTE: {json.dumps(context, indent=2)}

Analyse et réponds avec le JSON."""
        
        return prompt
    
    def _parse_detection_response(self, response: str, context: Dict) -> InitialAnalysis:
        """Parse la réponse du LLM."""
        try:
            # Extraction JSON depuis la réponse
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                # Pas de JSON trouvé
                return InitialAnalysis(
                    has_error=False,
                    error_type=ProblemType.NONE,
                    confidence=0.0,
                    context=context
                )
            
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            
            return InitialAnalysis(
                has_error=data.get("has_error", False),
                error_type=ProblemType(data.get("error_type", "none")),
                error_description=data.get("error_description"),
                confidence=float(data.get("confidence", 0.0)),
                context=context
            )
        
        except Exception as e:
            # En cas d'erreur de parsing, on considère qu'il n'y a pas d'erreur
            return InitialAnalysis(
                has_error=False,
                error_type=ProblemType.NONE,
                confidence=0.0,
                context={**context, "parse_error": str(e)}
            )

