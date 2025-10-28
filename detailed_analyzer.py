"""Module d'analyse détaillée avec questions/réponses."""
from typing import Dict, List, Any
from models import (
    CallAnalysisRequest,
    DetailedAnalysis,
    AnalysisStep,
    Question,
    InitialAnalysis
)
from llm_clients import LLMClient
from config import Config
import json


class DetailedAnalyzer:
    """Effectue l'analyse détaillée des appels avec erreurs."""
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.llm = LLMClient(model_name)
        self.model_name = model_name
        self.common_tags = Config.COMMON_TAGS
    
    def analyze(self, request: CallAnalysisRequest, initial_analysis: InitialAnalysis) -> DetailedAnalysis:
        """Effectue l'analyse détaillée de l'appel."""
        # Ne génère plus les étapes d'analyse ni les recommandations
        steps = []

        # Génère uniquement les tags et le résumé
        tags = self._generate_tags(request, initial_analysis)
        summary = self._generate_summary(request, initial_analysis, tags)

        # Pas de recommandations
        recommendations = []

        return DetailedAnalysis(
            call_id=request.call_id,
            problem_type=initial_analysis.error_type.value,
            problem_detected=initial_analysis.has_error,
            steps=steps,
            tags=tags,
            summary=summary,
            recommendations=recommendations
        )
    
    def _generate_tags(self, request: CallAnalysisRequest, initial: InitialAnalysis) -> List[str]:
        """Génère les tags appropriés pour l'appel."""
        
        # Assignation simple des tags en fonction du type d'erreur
        tag_mapping = {
            "parsing_error": ["erreur_parsing"],
            "api_error": ["erreur_technique"],
            "misunderstanding": ["malentendu_client"],
            "missing_info": ["information_manquante"],
            "technical_error": ["erreur_technique"],
            "other": []
        }
        
        # Obtient les tags de base du type
        tags = tag_mapping.get(initial.error_type.value, [])
        
        # Ajoute des tags additionnels si des outils ont échoué
        if any(not t.success for t in request.tool_results):
            if "erreur_technique" not in tags:
                tags.append("erreur_technique")
        
        return tags
    
    def _generate_summary(self, request: CallAnalysisRequest, initial: InitialAnalysis, tags: List[str]) -> str:
        """Génère le résumé de l'appel."""
        
        system_prompt = """Tu génères un résumé concis de l'erreur détectée dans l'appel."""
        
        user_prompt = f"""Résume l'erreur en une phrase claire et concise:

Type d'erreur: {initial.error_type.value}
Description: {initial.error_description}

Résume simplement ce qui s'est passé."""
        
        response = self.llm.generate(user_prompt, system_prompt, temperature=0.3, max_tokens=100)
        return response.strip()
    

