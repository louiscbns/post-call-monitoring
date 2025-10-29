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
        {"tag": "patient_non_trouve", "description": "Le patient recherché n'a pas été trouvé dans la base de données"},
        {"tag": "praticien_non_trouve", "description": "Le praticien/chirurgien recherché n'a pas été trouvé"},
        {"tag": "operation_non_trouvee", "description": "L'opération/chirurgie recherchée n'a pas été trouvée"},
        {"tag": "pas_de_disponibilites", "description": "Aucune disponibilité trouvée pour la période demandée"},
        {"tag": "erreur_booking", "description": "Erreur lors de la réservation/booking d'un rendez-vous"},
        {"tag": "erreur_extraction_entite", "description": "Erreur lors de l'extraction d'entités depuis la conversation"},
        {"tag": "erreur_tool", "description": "Erreur lors de l'exécution d'un outil/tool"},
        {"tag": "entity_detection_erreur", "description": "Erreur lors de la détection d'entités (nom, date, etc.)"},
        {"tag": "informations_manquantes", "description": "Informations requises manquantes pour compléter l'action"},
        {"tag": "autres", "description": "Autre type d'erreur non catégorisée"}
    ]
    
    # Motifs d'appel avec description
    CALL_REASONS: list = [
        {"reason": "get_appointment_info", "description": "Demander des informations sur un rendez-vous existant"},
        {"reason": "book_appointment", "description": "Réserver un nouveau rendez-vous"},
        {"reason": "cancel_appointment", "description": "Annuler un rendez-vous"},
        {"reason": "move_appointment", "description": "Déplacer/Modifier un rendez-vous existant"},
        {"reason": "confirm_appointment", "description": "Confirmer un rendez-vous"},
        {"reason": "other_requests", "description": "Autre type de demande non liée au booking"}
    ]
    
    # Sentiments utilisateur avec description
    USER_SENTIMENTS: list = [
        {"sentiment": "positif", "description": "L'appelant exprime des sentiments positifs, satisfaction, enthousiasme"},
        {"sentiment": "neutre", "description": "L'appelant garde un ton neutre, ni positif ni négatif"},
        {"sentiment": "negatif", "description": "L'appelant exprime de la frustration, mécontentement ou insatisfaction"},
        {"sentiment": "frustre", "description": "L'appelant est frustré par la situation ou le service"},
        {"sentiment": "satisfait", "description": "L'appelant est satisfait de l'interaction et du service"},
        {"sentiment": "confus", "description": "L'appelant semble confus, besoin de clarification ou d'explication"}
    ]
    
    # Tags de suivi des informations échangées avec description
    CALL_TAGS: list = [
        {"tag": "nom_du_chirurgien", "description": "Le nom du chirurgien a été mentionné ou demandé"},
        {"tag": "date_de_chirurgie", "description": "La date de la chirurgie a été mentionnée ou discutée"},
        {"tag": "intitule_chirurgie", "description": "L'intitulé/nom de la chirurgie a été mentionné"},
        {"tag": "anticoagulants", "description": "Les anticoagulants ont été mentionnés ou discutés"},
        {"tag": "disponibilites_enoncees", "description": "Des disponibilités ont été énoncées/présentées à l'appelant"},
        {"tag": "patient_trouve", "description": "Le patient a été trouvé avec succès dans la base de données"},
        {"tag": "patient_non_trouve", "description": "Le patient n'a pas été trouvé (erreur ou échec de recherche)"},
        {"tag": "nom", "description": "Le nom du patient a été mentionné, donné ou demandé"},
        {"tag": "prenom", "description": "Le prénom du patient a été mentionné, donné ou demandé"},
        {"tag": "date_de_naissance", "description": "La date de naissance a été mentionnée, donnée ou demandée"},
        {"tag": "email", "description": "L'email a été mentionné, donné ou demandé"},
        {"tag": "adresse", "description": "L'adresse a été mentionnée, donnée ou demandée"},
        {"tag": "rdv_confirme", "description": "Un rendez-vous a été confirmé pendant l'appel"},
        {"tag": "appel_transfere", "description": "L'appel a été transféré à un autre service ou agent"}
    ]
    
    # Structure des questions pour l'extraction - un appel LLM par question
    EXTRACTION_QUESTIONS: list = [
        {
            "name": "call_reason",
            "description": "Identifie le motif principal de l'appel",
            "options": CALL_REASONS,  # Utilise la liste Config
            "response_type": "select",  # Single choice
            "required": True,
            "default_value": "other_requests",
            "field_key": "reason"  # Clé pour extraire la valeur depuis les options dict
        },
        {
            "name": "user_sentiment",
            "description": "Sentiment global de l'appelant durant la conversation",
            "options": USER_SENTIMENTS,
            "response_type": "select",
            "required": False,
            "default_value": None,
            "field_key": "sentiment"
        },
        {
            "name": "failure_reasons",
            "description": "Liste des tags d'erreur si un échec est détecté (tools échoués ou erreurs)",
            "options": ERROR_TAGS,
            "response_type": "multiselect",  # Multiple choice
            "required": False,
            "default_value": None,
            "field_key": "tag",
            "nullable": True  # Peut être null si pas d'échec
        },
        {
            "name": "failure_description",
            "description": "Description textuelle détaillée de l'échec si un échec est détecté",
            "options": None,  # Pas de liste d'options, réponse libre
            "response_type": "text",
            "required": False,
            "default_value": None,
            "nullable": True  # Peut être null si pas d'échec
        },
        {
            "name": "call_tags",
            "description": "Tags indiquant quelles informations ont été échangées/demandées/presentées pendant l'appel",
            "options": CALL_TAGS,
            "response_type": "multiselect",
            "required": True,
            "default_value": [],
            "field_key": "tag",
            "nullable": False  # Doit toujours être une liste (même vide)
        },
        {
            "name": "user_questions",
            "description": "Liste des questions posées UNIQUEMENT par l'appelant (rôle 'user'), IGNORE les questions posées par l'agent (rôle 'assistant'). Une question par ligne.",
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

