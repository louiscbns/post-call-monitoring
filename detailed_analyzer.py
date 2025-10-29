"""Module d'analyse détaillée avec questions/réponses."""
from typing import List, Any
import json
from models import (
    CallAnalysisRequest,
    DetailedAnalysis,
    CallStatistics
)
from llm_clients import LLMClient
from config import Config


class DetailedAnalyzer:
    """Effectue l'analyse détaillée des appels avec erreurs."""
    
    def __init__(self, model_name: str = "gpt-4o"):
        self.llm = LLMClient(model_name)
        self.model_name = model_name
    
    def analyze(self, request: CallAnalysisRequest) -> DetailedAnalysis:
        """Effectue l'analyse détaillée de l'appel."""
        statistics = self._extract_statistics(request)
        
        problem_detected = bool(statistics.failure_reasons)
        problem_type = statistics.failure_reasons[0] if problem_detected else "none"
        tags = self._generate_tags_from_statistics(statistics)
        summary = self._generate_summary_from_statistics(statistics)

        return DetailedAnalysis(
            call_id=request.call_id,
            problem_type=problem_type,
            problem_detected=problem_detected,
            steps=[],
            tags=tags,
            summary=summary,
            recommendations=[],
            confidence=None,
            statistics=statistics
        )
    
    def _generate_tags_from_statistics(self, statistics: CallStatistics) -> List[str]:
        """Génère les tags à partir des failure_reasons."""
        return statistics.failure_reasons or []
    
    def _generate_summary_from_statistics(self, statistics: CallStatistics) -> str:
        """Génère le résumé de l'appel à partir des statistiques."""
        if not statistics.failure_reasons:
            return "Aucun problème détecté dans cet appel."
        
        if statistics.failure_description:
            return statistics.failure_description
        
        # Générer un résumé à partir des failure_reasons
        if len(statistics.failure_reasons) == 1:
            return f"Erreur détectée: {statistics.failure_reasons[0].replace('_', ' ').title()}"
        else:
            errors_list = ", ".join([r.replace('_', ' ').title() for r in statistics.failure_reasons])
            return f"Plusieurs erreurs détectées: {errors_list}"
    
    def _extract_single_question(self, question_config: dict, conversation_text: str, tools_text: str, failure_note: str = "") -> Any:
        """Extrait une seule question avec un appel LLM dédié."""
        name = question_config["name"]
        
        # Générer les prompts minimalistes (base prompt global + contexte spécifique à l'attribut)
        system_prompt, user_prompt = Config.generate_minimal_question_prompt(
            question_config, conversation_text, tools_text, failure_note
        )
        
        # Appel LLM
        response = self.llm.generate(user_prompt, system_prompt, temperature=0.2, max_tokens=600)
        
        # Parser la réponse JSON
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                data = json.loads(response[json_start:json_end])
                value = data.get(name)
                return self._validate_and_normalize_value(value, question_config)
            else:
                return question_config.get("default_value")
        except Exception as e:
            print(f"Erreur lors de l'extraction de {name}: {e}")
            print(f"Réponse LLM: {response[:200]}")
            return question_config.get("default_value")
    
    def _validate_and_normalize_value(self, value: Any, question_config: dict) -> Any:
        """Valide une valeur selon la configuration de la question (vérifie le format et les options)."""
        response_type = question_config["response_type"]
        nullable = question_config.get("nullable", False)
        default_value = question_config.get("default_value")
        options = question_config.get("options")
        field_key = question_config.get("field_key")
        
        # Gérer null
        if value is None or (isinstance(value, str) and value.lower() == "null"):
            return None if nullable else (default_value if default_value is not None else [])
        
        # Validation selon le type
        if response_type == "select":
            # Vérifier que la valeur est exactement dans les options
            if options and field_key:
                option_values = [opt[field_key] for opt in options]
                if isinstance(value, str) and value in option_values:
                    return value
                return default_value
            return value
        
        elif response_type == "multiselect":
            # Vérifier que c'est une liste et que toutes les valeurs sont dans les options
            if not isinstance(value, list):
                return None if nullable else []
            
            if options and field_key:
                option_values = [opt[field_key] for opt in options]
                valid_values = [item for item in value if isinstance(item, str) and item in option_values]
                
                if not nullable and len(valid_values) == 0:
                    return []
                return valid_values if valid_values else (None if nullable else [])
            return value
        
        elif response_type == "string":
            # Validation: string non vide
            if isinstance(value, str):
                value = value.strip()
                if len(value) == 0:
                    return None if nullable else default_value
                return value
            return None if nullable else default_value
        
        elif response_type == "number":
            # Validation: nombre
            if isinstance(value, (int, float)):
                return value
            if isinstance(value, str):
                try:
                    # Essayer de convertir en float pour supporter les décimales
                    return float(value) if '.' in value else int(value)
                except ValueError:
                    return None if nullable else default_value
            return None if nullable else default_value
        
        elif response_type == "boolean":
            # Validation: boolean
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                lower_val = value.lower().strip()
                if lower_val in ("true", "1", "yes", "oui"):
                    return True
                elif lower_val in ("false", "0", "no", "non"):
                    return False
            return None if nullable else default_value
        
        elif response_type in ("text", "text_multiline"):  # Support rétrocompatibilité
            # Validation: texte non vide
            if isinstance(value, str):
                value = value.strip()
                if len(value) < 5:
                    return None if nullable else default_value
                return value
            return None if nullable else default_value
        
        return value
    
    def _extract_statistics(self, request: CallAnalysisRequest) -> CallStatistics:
        """Extrait toutes les statistiques de l'appel - un appel LLM par question."""
        
        conversation_text = self._build_conversation_text(request)
        tools_text = self._build_tools_text(request)
        
        # Vérifier s'il y a des échecs pour guider le LLM
        has_failure = (
            any(not tool.success for tool in request.tool_results) or
            any("erreur" in turn.content.lower() or "échec" in turn.content.lower() 
                for turn in request.conversation)
        )
        
        failure_note = "⚠️ ATTENTION: Un ou plusieurs outils ont échoué. Identifie les raisons d'échec." if has_failure else "✅ Aucun échec détecté. failure_reasons et failure_description doivent être null."
        
        # Initialiser les résultats avec les valeurs par défaut
        results = {}
        
        # Extraire chaque question individuellement
        print("  Extractions:", end=" ", flush=True)
        for idx, question_config in enumerate(Config.EXTRACTION_QUESTIONS):
            question_name = question_config["name"]
            if idx > 0:
                print(",", end=" ", flush=True)
            print(f"{question_name}", end="", flush=True)
            
            value = self._extract_single_question(
                question_config, 
                conversation_text, 
                tools_text, 
                failure_note if question_name in ["failure_reasons", "failure_description"] else ""
            )
            
            results[question_name] = value
        
        print()  # Nouvelle ligne après les extractions
        
        # Construire CallStatistics avec les résultats
        return CallStatistics(
            call_reason=results.get("call_reason"),
            user_questions=results.get("user_questions"),
            user_sentiment=results.get("user_sentiment"),
            failure_reasons=results.get("failure_reasons"),
            failure_description=results.get("failure_description"),
            call_tags=results.get("call_tags", [])
        )
    
    def _build_conversation_text(self, request: CallAnalysisRequest) -> str:
        """Construit le texte de la conversation pour les prompts."""
        text = "TRANSCRIPT DE LA CONVERSATION:\n"
        text += "=" * 60 + "\n"
        for idx, turn in enumerate(request.conversation, 1):
            # Identifie clairement l'appelant vs l'agent
            if turn.role == "user":
                role_label = "APPELANT"
                role_emoji = "👤"
            elif turn.role in ["assistant", "agent"]:
                role_label = "AGENT"
                role_emoji = "🤖"
            else:
                role_label = turn.role.upper()
                role_emoji = "💬"
            
            text += f"\n[{idx}] {role_emoji} {role_label} [{turn.role}]:\n{turn.content}\n"
            text += "-" * 60 + "\n"
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
    
