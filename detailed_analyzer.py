"""Module d'analyse détaillée avec questions/réponses."""
from typing import Dict, List, Any, Optional, Tuple
from models import (
    CallAnalysisRequest,
    DetailedAnalysis,
    AnalysisStep,
    Question,
    InitialAnalysis,
    CallStatistics
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
        
        # Extraction des statistiques enrichies (intégré directement ici)
        statistics = self._extract_statistics(request)

        return DetailedAnalysis(
            call_id=request.call_id,
            problem_type=initial_analysis.error_type.value,
            problem_detected=initial_analysis.has_error,
            steps=steps,
            tags=tags,
            summary=summary,
            recommendations=recommendations,
            confidence=initial_analysis.confidence,
            statistics=statistics
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
    
    def _extract_statistics(self, request: CallAnalysisRequest) -> CallStatistics:
        """Extrait toutes les statistiques de l'appel en un seul appel LLM (utilise les prompts de Config)."""
        
        # Générer le prompt système dynamiquement depuis Config (utilise les listes)
        system_prompt = Config.get_statistics_system_prompt()
        
        conversation_text = self._build_conversation_text(request)
        tools_text = self._build_tools_text(request)
        
        # Vérifier s'il y a des échecs pour guider le LLM
        has_failure = (
            any(not tool.success for tool in request.tool_results) or
            any("erreur" in turn.content.lower() or "échec" in turn.content.lower() 
                for turn in request.conversation)
        )
        
        failure_note = "⚠️ ATTENTION: Un ou plusieurs outils ont échoué. Identifie les raisons d'échec." if has_failure else "✅ Aucun échec détecté. failure_reasons et failure_description doivent être null."
        
        # Utiliser le template de prompt depuis Config
        user_prompt = Config.STATISTICS_USER_PROMPT_TEMPLATE.format(
            conversation_text=conversation_text,
            tools_text=tools_text,
            failure_note=failure_note
        )
        
        response = self.llm.generate(user_prompt, system_prompt, temperature=0.2, max_tokens=500)
        
        # Parse la réponse JSON
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                data = json.loads(response[json_start:json_end])
                
                # Extraire et valider les données depuis Config
                call_reason = data.get("call_reason")
                if call_reason not in Config.CALL_REASONS:
                    call_reason = "other_requests"
                
                user_questions = data.get("user_questions")
                if user_questions and user_questions.lower() == "null":
                    user_questions = None
                elif user_questions and len(user_questions.strip()) < 5:
                    user_questions = None
                
                user_sentiment = data.get("user_sentiment")
                if user_sentiment not in Config.USER_SENTIMENTS:
                    user_sentiment = self._infer_sentiment_from_context(request)
                
                failure_reasons = data.get("failure_reasons")
                if failure_reasons and failure_reasons != "null":
                    if isinstance(failure_reasons, list):
                        valid_reasons = [r for r in failure_reasons if r in Config.FAILURE_REASONS]
                        failure_reasons = valid_reasons if valid_reasons else None
                    else:
                        failure_reasons = None
                else:
                    failure_reasons = None
                
                failure_description = data.get("failure_description")
                if failure_description and failure_description.lower() == "null":
                    failure_description = None
                elif failure_description and len(failure_description.strip()) < 5:
                    failure_description = None
                
                return CallStatistics(
                    call_reason=call_reason,
                    user_questions=user_questions,
                    user_sentiment=user_sentiment,
                    failure_reasons=failure_reasons,
                    failure_description=failure_description
                )
        except Exception as e:
            print(f"Erreur lors du parsing JSON: {e}")
            print(f"Réponse LLM: {response[:200]}")
        
        # Fallback: extraction basique si le parsing échoue
        return self._extract_statistics_fallback(request)
    
    def _extract_statistics_fallback(self, request: CallAnalysisRequest) -> CallStatistics:
        """Méthode de fallback si le parsing JSON échoue."""
        user_messages = " ".join([turn.content.lower() for turn in request.conversation if turn.role == "user"])
        
        # Détection basique du motif
        call_reason = "other_requests"
        if any(word in user_messages for word in ["réserver", "prendre rendez-vous", "disponible", "créneau"]):
            call_reason = "book_appointment"
        elif any(word in user_messages for word in ["annuler", "annulation"]):
            call_reason = "cancel_appointment"
        elif any(word in user_messages for word in ["déplacer", "modifier", "changer"]):
            call_reason = "move_appointment"
        elif any(word in user_messages for word in ["confirmer", "confirmation"]):
            call_reason = "confirm_appointment"
        elif any(word in user_messages for word in ["horaire", "disponibilité", "info", "information"]):
            call_reason = "get_appointment_info"
        
        user_sentiment = self._infer_sentiment_from_context(request)
        
        failure_reasons = None
        failure_description = None
        if any(not tool.success for tool in request.tool_results):
            failure_reasons = ["erreur_api"]
            failure_description = "Un ou plusieurs outils ont échoué"
        
        return CallStatistics(
            call_reason=call_reason,
            user_questions=None,
            user_sentiment=user_sentiment,
            failure_reasons=failure_reasons,
            failure_description=failure_description
        )
    
    def _build_conversation_text(self, request: CallAnalysisRequest) -> str:
        """Construit le texte de la conversation pour les prompts."""
        text = "CONVERSATION:\n"
        for turn in request.conversation:
            role_emoji = "👤" if turn.role == "user" else "🤖"
            text += f"{role_emoji} [{turn.role}]: {turn.content}\n\n"
        return text
    
    def _build_tools_text(self, request: CallAnalysisRequest) -> str:
        """Construit le texte des résultats d'outils."""
        if not request.tool_results:
            return ""
        
        text = "RÉSULTATS OUTILS:\n"
        for tool in request.tool_results:
            status = "✅" if tool.success else "❌"
            text += f"{status} {tool.tool_name}:\n"
            if not tool.success and tool.error_message:
                text += f"  ❌ Erreur: {tool.error_message}\n"
        return text
    
    def _infer_sentiment_from_context(self, request: CallAnalysisRequest) -> str:
        """Infère le sentiment depuis le contexte si le LLM n'a pas répondu correctement."""
        user_messages = " ".join([turn.content.lower() for turn in request.conversation if turn.role == "user"])
        
        positive_words = ["merci", "parfait", "super", "excellent", "satisfait"]
        negative_words = ["problème", "erreur", "déçu", "insatisfait", "colère"]
        confused_words = ["comprend", "comment", "explique", "confus"]
        
        if any(word in user_messages for word in positive_words):
            return "positif"
        elif any(word in user_messages for word in negative_words):
            return "negatif"
        elif any(word in user_messages for word in confused_words):
            return "confus"
        else:
            return "neutre"
    

