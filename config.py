"""Configuration pour le système d'analyse post-appel."""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration de l'application."""
    
    # API Call Rounded
    ROUNDED_API_KEY: str = os.getenv("ROUNDED_API_KEY", "")
    ROUNDED_API_URL: str = "https://api.callrounded.com/v1/calls"
    
    # Modèles LLM
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    
    # Modèles disponibles
    DEFAULT_MODEL: str = "gpt-4o-mini"
    AVAILABLE_MODELS: dict = {
        "gpt-4o-mini": "OpenAI",
        "claude-3-5-sonnet": "Anthropic",
        "gemini-2.0-flash": "Google"
    }
    
    # Tags de problèmes communs
    COMMON_TAGS: list = [
        "erreur_parsing",
        "requete_api_vide",
        "malentendu_client",
        "information_manquante",
        "double_appel",
        "erreur_technique",
        "timeout",
        "donnees_invalides",
        "connexion_echouee",
        "validation_echouee"
    ]
    
    # Options pour les statistiques
    CALL_REASONS: list = [
        "get_appointment_info",
        "book_appointment",
        "cancel_appointment",
        "move_appointment",
        "confirm_appointment",
        "other_requests"
    ]
    
    USER_SENTIMENTS: list = [
        "positif",
        "neutre",
        "negatif",
        "frustre",
        "satisfait",
        "confus"
    ]
    
    FAILURE_REASONS: list = [
        "timeout",
        "erreur_api",
        "donnees_manquantes",
        "malentendu",
        "probleme_technique",
        "refus_client",
        "limite_systeme",
        "autre"
    ]
    
    # Questions personnalisables pour la base de connaissances
    # Vous pouvez ajouter des questions types ici pour guider l'extraction
    CUSTOM_QUESTIONS_PATTERNS: list = [
        # Exemples de patterns à détecter
        "Quels sont les",
        "Combien coûte",
        "Comment puis-je",
        "Est-ce que",
        "Quand peut-on",
    ]
    
    # Template du prompt système pour l'extraction de statistiques (utilise les listes Config)
    STATISTICS_SYSTEM_PROMPT_TEMPLATE: str = """Tu es un expert en analyse de conversations clients.
Ta tâche est d'extraire toutes les statistiques d'un appel en analysant la conversation et les résultats des outils.

Réponds UNIQUEMENT avec un JSON valide au format suivant:
{{
    "call_reason": {call_reasons_options},
    "user_questions": "Liste des questions posées par l'appelant pour la base de connaissances, une question par ligne. null si aucune question pertinente.",
    "user_sentiment": {user_sentiments_options},
    "failure_reasons": {failure_reasons_options} | null,
    "failure_description": "Description textuelle détaillée de l'échec" | null
}}

RÈGLES IMPORTANTES:
- call_reason: Identifie le motif principal de l'appel. Options disponibles:
{call_reasons_list}

- user_questions: Extrais les questions intéressantes pour une base de connaissances. Liste-les une par ligne. null si aucune.

- user_sentiment: Sentiment global de l'appelant durant la conversation. Options disponibles:
{user_sentiments_list}

- failure_reasons: Liste des raisons d'échec si un échec est détecté (tools échoués ou erreurs). null si pas d'échec.
  Options disponibles: {failure_reasons_list}

- failure_description: Description détaillée de l'échec. null si pas d'échec."""
    
    @staticmethod
    def get_statistics_system_prompt() -> str:
        """Génère le prompt système dynamiquement à partir des listes Config."""
        # Formater les options pour le JSON schema
        call_reasons_options = ' | '.join([f'"{r}"' for r in Config.CALL_REASONS])
        user_sentiments_options = ' | '.join([f'"{s}"' for s in Config.USER_SENTIMENTS])
        failure_reasons_options = '["' + '", "'.join(Config.FAILURE_REASONS) + '", ...]'
        
        # Créer les listes formatées pour les règles
        call_reasons_list = '\n'.join([f'  * {reason}' for reason in Config.CALL_REASONS])
        user_sentiments_list = '\n'.join([f'  * {sentiment}' for sentiment in Config.USER_SENTIMENTS])
        failure_reasons_list = ', '.join([f'"{r}"' for r in Config.FAILURE_REASONS])
        
        return Config.STATISTICS_SYSTEM_PROMPT_TEMPLATE.format(
            call_reasons_options=call_reasons_options,
            user_sentiments_options=user_sentiments_options,
            failure_reasons_options=failure_reasons_options,
            call_reasons_list=call_reasons_list,
            user_sentiments_list=user_sentiments_list,
            failure_reasons_list=failure_reasons_list
        )
    
    # Template du prompt utilisateur pour l'extraction de statistiques (modifiable)
    STATISTICS_USER_PROMPT_TEMPLATE: str = """Analyse cette conversation et extrait toutes les statistiques:

{conversation_text}

{tools_text}

Extrais:
1. Le motif principal de l'appel (call_reason)
2. Les questions posées par l'appelant pour la base de connaissances (user_questions)
3. Le sentiment de l'appelant (user_sentiment)
4. Les raisons d'échec si un échec est détecté (failure_reasons) - null sinon
5. La description de l'échec si applicable (failure_description) - null sinon

{failure_note}

Réponds avec UNIQUEMENT le JSON valide, sans texte supplémentaire."""

