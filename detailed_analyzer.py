"""Module d'analyse détaillée avec questions/réponses."""
from typing import Dict, List, Any, Optional, Tuple
import json
import re
from models import (
    CallAnalysisRequest,
    DetailedAnalysis,
    AnalysisStep,
    Question,
    CallStatistics
)
from llm_clients import LLMClient
from config import Config


class DetailedAnalyzer:
    """Effectue l'analyse détaillée des appels avec erreurs."""
    
    def __init__(self, model_name: str = "gpt-4o"):
        self.llm = LLMClient(model_name)
        self.model_name = model_name
        self.ERROR_TAGS = Config.get_error_tags_values()
    
    def analyze(self, request: CallAnalysisRequest) -> DetailedAnalysis:
        """Effectue l'analyse détaillée de l'appel."""
        # Ne génère plus les étapes d'analyse ni les recommandations
        steps = []

        # Extraction des statistiques enrichies (inclut failure_reasons et failure_description)
        statistics = self._extract_statistics(request)
        
        # Détermine s'il y a un problème basé sur failure_reasons
        problem_detected = statistics.failure_reasons is not None and len(statistics.failure_reasons) > 0
        
        # Détermine le type de problème depuis failure_reasons (utilise le premier si plusieurs)
        if problem_detected and statistics.failure_reasons:
            problem_type = statistics.failure_reasons[0]  # Utilise le premier failure_reason comme type
        else:
            problem_type = "none"
        
        # Génère les tags depuis failure_reasons ou call_tags
        tags = self._generate_tags_from_statistics(statistics)
        
        # Génère le résumé depuis failure_description ou failure_reasons
        summary = self._generate_summary_from_statistics(statistics, tags)

        # Pas de recommandations
        recommendations = []

        return DetailedAnalysis(
            call_id=request.call_id,
            problem_type=problem_type,
            problem_detected=problem_detected,
            steps=steps,
            tags=tags,
            summary=summary,
            recommendations=recommendations,
            confidence=None,  # Pas de confiance calculée, on utilise les statistiques directement
            statistics=statistics
        )
    
    def _generate_tags_from_statistics(self, statistics: CallStatistics) -> List[str]:
        """Génère les tags appropriés à partir des statistiques."""
        tags = []
        
        # Utilise failure_reasons comme tags principaux
        if statistics.failure_reasons:
            tags.extend(statistics.failure_reasons)
        
        # Si pas d'erreurs, retourne une liste vide
        return tags
    
    def _generate_summary_from_statistics(self, statistics: CallStatistics, tags: List[str]) -> str:
        """Génère le résumé de l'appel à partir des statistiques."""
        
        # Si pas d'erreur, résumé positif
        if not statistics.failure_reasons:
            return "Aucun problème détecté dans cet appel."
        
        # Si on a une description d'échec, l'utiliser
        if statistics.failure_description:
            return statistics.failure_description
        
        # Sinon, générer un résumé à partir des failure_reasons
        if len(statistics.failure_reasons) == 1:
            error_tag = statistics.failure_reasons[0]
            return f"Erreur détectée: {error_tag.replace('_', ' ').title()}"
        else:
            errors_list = ", ".join([r.replace('_', ' ').title() for r in statistics.failure_reasons])
            return f"Plusieurs erreurs détectées: {errors_list}"
    
    def _normalize_tag(self, tag: Any) -> Optional[str]:
        """Normalise un tag pour la comparaison (convertit en minuscules, remplace espaces par underscores)."""
        if not isinstance(tag, str):
            return None
        
        # Normaliser : minuscules, remplacer espaces multiples par un seul underscore
        normalized = tag.lower().strip()
        # Remplacer espaces, tirets, et autres séparateurs par underscores
        normalized = re.sub(r'[\s\-\.]+', '_', normalized)
        # Supprimer les underscores multiples
        normalized = re.sub(r'_+', '_', normalized)
        # Supprimer les underscores en début et fin
        normalized = normalized.strip('_')
        
        return normalized if normalized else None
    
    def _match_tag(self, tag: str, valid_tags: List[str]) -> Optional[str]:
        """Trouve le tag valide correspondant à un tag normalisé."""
        normalized = self._normalize_tag(tag)
        if not normalized:
            return None
        
        # Correspondance exacte après normalisation
        for valid_tag in valid_tags:
            if self._normalize_tag(valid_tag) == normalized:
                return valid_tag
        
        # Correspondance partielle (le tag normalisé contient ou est contenu dans un tag valide)
        for valid_tag in valid_tags:
            valid_normalized = self._normalize_tag(valid_tag)
            if valid_normalized and (normalized in valid_normalized or valid_normalized in normalized):
                # Vérifier que c'est une correspondance significative (pas juste un mot commun)
                if len(normalized) > 3 and len(valid_normalized) > 3:
                    return valid_tag
        
        return None
    
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
        """Valide et normalise une valeur selon la configuration de la question."""
        name = question_config["name"]
        response_type = question_config["response_type"]
        nullable = question_config.get("nullable", False)
        default_value = question_config.get("default_value")
        options = question_config.get("options")
        field_key = question_config.get("field_key")
        
        # Gérer null
        if value is None or (isinstance(value, str) and value.lower() == "null"):
            if nullable:
                return None
            else:
                return default_value if default_value is not None else []
        
        # Validation selon le type
        if response_type == "select":
            # Validation: doit être dans la liste des options
            if options and field_key:
                option_values = [opt[field_key] for opt in options]
                matched = self._match_tag(value, option_values) if isinstance(value, str) else None
                return matched if matched else default_value
            return value
        
        elif response_type == "multiselect":
            # Validation: liste d'options
            if not isinstance(value, list):
                if nullable:
                    return None
                return []
            
            if options and field_key:
                valid_values = []
                option_values = [opt[field_key] for opt in options]
                for item in value:
                    matched = self._match_tag(item, option_values) if isinstance(item, str) else None
                    if matched and matched not in valid_values:
                        valid_values.append(matched)
                
                if not nullable and len(valid_values) == 0:
                    return []
                return valid_values if valid_values else (None if nullable else [])
            return value
        
        elif response_type == "text":
            # Validation: texte non vide
            if isinstance(value, str):
                value = value.strip()
                if len(value) < 5:
                    return None if nullable else default_value
                return value
            return None if nullable else default_value
        
        elif response_type == "text_multiline":
            # Validation: texte multiligne
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
    
