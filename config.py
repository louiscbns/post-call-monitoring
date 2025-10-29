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
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    # Modèles disponibles
    DEFAULT_MODEL: str = "gpt-4o"
    AVAILABLE_MODELS: dict = {
        "gpt-4o": "OpenAI",
        "claude-3-5-sonnet": "Anthropic",
        "gemini-2.0-flash": "Google"
    }
    
    # Tags d'erreurs avec description - pour génération automatique du prompt
    ERROR_TAGS: list = [
        {"tag": "patient_non_trouve"},
        {"tag": "praticien_non_trouve"},
        {"tag": "operation_non_trouvee"},
        {"tag": "pas_de_disponibilites"},
        {"tag": "erreur_booking"},
        {"tag": "erreur_extraction_entite"},
        {"tag": "erreur_tool"},
        {"tag": "entity_detection_erreur"},
        {"tag": "informations_manquantes"},
        {"tag": "autres"}
    ]
    
    # Motifs d'appel avec description
    CALL_REASONS: list = [
        {"reason": "get_appointment_info"},
        {"reason": "book_appointment"},
        {"reason": "cancel_appointment"},
        {"reason": "move_appointment"},
        {"reason": "confirm_appointment"},
        {"reason": "other_requests"}
    ]
    
    # Sentiments utilisateur avec description
    USER_SENTIMENTS: list = [
        {"sentiment": "positif"},
        {"sentiment": "neutre"},
        {"sentiment": "negatif"},
        {"sentiment": "frustre"},
        {"sentiment": "satisfait"},
        {"sentiment": "confus"}
    ]
    
    # Tags de suivi des informations échangées avec description
    CALL_TAGS: list = [
        {"tag": "nom_du_chirurgien"},
        {"tag": "date_de_chirurgie"},
        {"tag": "intitule_chirurgie"},
        {"tag": "anticoagulants"},
        {"tag": "disponibilites_enoncees"},
        {"tag": "patient_trouve"},
        {"tag": "patient_non_trouve"},
        {"tag": "nom"},
        {"tag": "prenom"},
        {"tag": "date_de_naissance"},
        {"tag": "email"},
        {"tag": "adresse"},
        {"tag": "rdv_confirme"},
        {"tag": "appel_transfere"}
    ]
    
    # Structure des questions pour l'extraction - un appel LLM par question
    EXTRACTION_QUESTIONS: list = [
        {
            "name": "call_reason",
            "description": "Motif principal exprimé par l'appelant (le besoin initial qui justifie l'appel). Choisir UNE seule valeur la plus représentative du but de l'appel, en se basant uniquement sur ce que l'appelant demande ou cherche à accomplir.",
            "options": CALL_REASONS,  # Utilise la liste Config
            "response_type": "select",  # Single choice
            "required": True,
            "default_value": "other_requests",
            "field_key": "reason"  # Clé pour extraire la valeur depuis les options dict
        },
        {
            "name": "user_sentiment",
            "description": "Sentiment global de l'appelant (ton/attitude) sur l'ensemble de l'appel. Se concentrer sur l'appelant, pas l'agent. Déduire à partir du vocabulaire, de la politesse, de la frustration, des exclamations et du contexte.",
            "options": USER_SENTIMENTS,
            "response_type": "select",
            "required": False,
            "default_value": None,
            "field_key": "sentiment"
        },
        {
            "name": "failure_reasons",
            "description": "Tous les tags d'erreur applicables si un échec est survenu (panne d'outil, information introuvable, champ manquant, etc.). Retourner une liste (possiblement vide). Inclure chaque cause pertinente détectée dans le transcript ou dans les résultats d'outils.",
            "options": ERROR_TAGS,
            "response_type": "multiselect",  # Multiple choice
            "required": False,
            "default_value": None,
            "field_key": "tag",
            "nullable": True  # Peut être null si pas d'échec
        },
        {
            "name": "failure_description",
            "description": "Brève description factuelle et précise de l'échec s'il y en a un (quoi, où, pourquoi si identifiable). Mentionner l'outil ou l'information en cause, l'étape concernée et le symptôme observé (ex: 'patient non trouvé', 'timeout outil X').",
            "options": None,  # Pas de liste d'options, réponse libre
            "response_type": "text",
            "required": False,
            "default_value": None,
            "nullable": True  # Peut être null si pas d'échec
        },
        {
            "name": "call_tags",
            "description": "Tous les tags décrivant les informations concrètes échangées/presentées pendant l'appel (ex: champs patient, éléments médicaux, disponibilités). Inclure chaque tag objectivement mentionné ou confirmé. Toujours une liste (éventuellement vide).",
            "options": CALL_TAGS,
            "response_type": "multiselect",
            "required": True,
            "default_value": [],
            "field_key": "tag",
            "nullable": False  # Doit toujours être une liste (même vide)
        },
        {
            "name": "user_questions",
            "description": "Liste exhaustive des questions/requests d'information posées UNIQUEMENT par l'appelant (rôle 'user'). Ne pas inclure les questions de l'agent. Restituer une question par ligne, en citant ou reformulant clairement l'intention de l'appelant.",
            "options": None,  # Pas de liste d'options, extraction libre
            "response_type": "text_multiline",  # Texte multiligne
            "required": False,
            "default_value": None,
            "nullable": True
        }
    ]
    
    
    
    
    @staticmethod
    def get_error_tags_values() -> list:
        """Retourne la liste des valeurs de tags d'erreur."""
        return [item["tag"] for item in Config.ERROR_TAGS]
    
    @staticmethod
    def get_call_reasons_values() -> list:
        """Retourne la liste des valeurs de motifs d'appel."""
        return [item["reason"] for item in Config.CALL_REASONS]
    
    @staticmethod
    def get_user_sentiments_values() -> list:
        """Retourne la liste des valeurs de sentiments utilisateur."""
        return [item["sentiment"] for item in Config.USER_SENTIMENTS]
    
    @staticmethod
    def get_call_tags_values() -> list:
        """Retourne la liste des valeurs de tags de suivi."""
        return [item["tag"] for item in Config.CALL_TAGS]
    
    


    # Base prompt global léger, réutilisé pour toutes les extractions
    BASE_SYSTEM_PROMPT: str = """Tu es un expert en analyse de conversations clients.
Tu extrais des statistiques de manière fiable, concise et strictement au format JSON demandé.
Ne réponds qu’en JSON valide, sans texte additionnel.
"""

    @staticmethod
    def generate_minimal_question_prompt(question_config: dict, conversation_text: str, tools_text: str, failure_note: str = "") -> tuple[str, str]:
        """Construit un prompt minimaliste par attribut en réutilisant un base prompt global.

        Retourne (system_prompt, user_prompt)
        """
        name = question_config["name"]
        description = question_config["description"]
        response_type = question_config["response_type"]
        nullable = question_config.get("nullable", False)

        # Format JSON attendu court et instruction brève
        if response_type == "select":
            json_format = f'"{name}": "valeur"'
            instruction = "Sélectionne une seule valeur précise."
        elif response_type == "multiselect":
            json_format = f'"{name}": ["valeur1", "valeur2"]' + (" | null" if nullable else "")
            instruction = "Sélectionne toutes les valeurs pertinentes (liste vide si aucune)."
        elif response_type == "text":
            json_format = f'"{name}": "texte"' + (" | null" if nullable else "")
            instruction = "Fournis un court texte explicatif."
        elif response_type == "text_multiline":
            json_format = f'"{name}": "ligne1\\nligne2"' + (" | null" if nullable else "")
            instruction = "Liste chaque élément sur une nouvelle ligne."
        else:
            json_format = f'"{name}": null'
            instruction = "Retourne au bon format JSON."

        system_prompt = Config.BASE_SYSTEM_PROMPT

        user_prompt = f"""Tâche: Extraire l'attribut: {name}
But: {description}
Consignes: {instruction}

Réponds UNIQUEMENT avec un JSON valide au format:
{{
    {json_format}
}}

Conversation:
{conversation_text}

Résultats d'outils:
{tools_text}

{failure_note if failure_note else ""}"""

        return system_prompt, user_prompt

