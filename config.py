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
    DEFAULT_MODEL: str = "gpt-4.1"
    AVAILABLE_MODELS: dict = {
        "gemini-2.0-flash": "Google",
        "gpt-4.1": "OpenAI",
        "gpt-4.1-mini": "OpenAI"
    }
    
    # Tags d'erreurs avec description - pour génération automatique du prompt
    ERROR_TAGS: list = [
        {"tag": "patient_non_trouve"},
        {"tag": "praticien_non_trouve"},
        {"tag": "operation_non_trouvee"},
        {"tag": "pas_de_disponibilites"},
        {"tag": "erreur_booking"},
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
            "description": "Identifie le motif principal formulé explicitement ou implicitement par l'appelant : la raison initiale et essentielle pour laquelle il a contacté l'accueil. Sélectionne UNE seule valeur la plus représentative, qui caractérise au mieux l'objectif exprimé (même s'il y a plusieurs demandes secondaires). Base-toi uniquement sur ce que l'appelant cherche à réaliser ou demande directement, sans interprétation excessive ni influence de l'agent.",
            "options": CALL_REASONS,  # Utilise la liste Config
            "response_type": "select",  # Single choice
            "required": True,
            "default_value": "other_requests",
            "field_key": "reason"  # Clé pour extraire la valeur depuis les options dict
        },
        {
            "name": "user_sentiment",
            "description": "Analyse le ton, l’attitude générale et le ressenti global de l’appelant tout au long de l’appel. Concentre-toi uniquement sur l’appelant (ignorer l’agent). Déduis cette information à partir du vocabulaire, du niveau de politesse, d’éventuels signes de frustration, de satisfaction ou de confusion, des exclamations, ou des indices laissés dans le discours. Ne tire que des conclusions appuyées par des éléments manifestes dans la conversation.",
            "options": USER_SENTIMENTS,
            "response_type": "select",
            "required": False,
            "default_value": None,
            "field_key": "sentiment"
        },
        {
            "name": "failure_reasons",
            "description": "Liste tous les tags d’erreur applicables en cas de dysfonctionnement ou d’échec survenu durant l’appel (exemples : panne d’un outil, entité recherchée introuvable, information manquante, problème de prise de rendez-vous, etc.). Fournis toutes les causes pertinentes détectées dans le transcript de l’appel ou dans les résultats d’outils éventuels. Retourne une liste possiblement vide. Prends en compte les erreurs même partielles ou multiples.",
            "options": ERROR_TAGS,
            "response_type": "multiselect",  # Multiple choice
            "required": False,
            "default_value": None,
            "field_key": "tag",
            "nullable": True  # Peut être null si pas d'échec
        },
        {
            "name": "failure_description",
            "description": "Rédige une brève description factuelle, précise et synthétique de l’éventuel échec détecté. Décris ce qui s’est produit (quoi, où, pour quelle raison si possible), en mentionnant : l’information ou l’outil concerné, l’étape du processus, et tout symptôme pertinent (exemple : « patient non trouvé lors de la recherche », « échec de l’outil Agenda (timeout) », « information date de naissance manquante »). Sois neutre, objectif et le plus concis possible.",
            "options": None,  # Pas de liste d'options, réponse libre
            "response_type": "text",
            "required": False,
            "default_value": None,
            "nullable": True  # Peut être null si pas d'échec
        },
        {
            "name": "call_tags",
            "description": "Identifie et rassemble tous les tags décrivant les informations concrètement échangées, présentées ou confirmées lors de l'appel : champs administratifs, éléments médicaux (comme un nom de chirurgien, une date d’intervention), disponibilités précisées, etc. Inclure chaque tag mentionné explicitement ou validé sans interprétation. La liste doit toujours être fournie, même si elle est vide.",
            "options": CALL_TAGS,
            "response_type": "multiselect",
            "required": True,
            "default_value": [],
            "field_key": "tag",
            "nullable": False  # Doit toujours être une liste (même vide)
        },
        {
            "name": "user_questions",
            "description": "Dresse une liste exhaustive et synthétique de toutes les questions posées par l'appelant (rôle 'user') portant sur une demande d’information précise, une clarification ou une recherche de confirmation. Exclure toute question issue de l’agent et toute remarque non formulée comme une question authentique. Pour chaque question, restitue une phrase claire qui explicite ce à quoi l’appelant souhaite obtenir une réponse ou une précision.",
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
    BASE_SYSTEM_PROMPT: str = """Tu es un extracteur déterministe d'informations à partir de conversations entre un appelant et un agent vocal.
Ta mission est de produire UNIQUEMENT un objet JSON valide, strictement conforme aux consignes de format et aux valeurs autorisées.

RÈGLES GÉNÉRALES (appliquer à chaque requête) :
1) Format de sortie :
   - Réponds EXCLUSIVEMENT par un unique objet JSON valide.
   - AUCUN texte hors JSON, AUCUN commentaire, AUCUN markdown, AUCUNE explication.
   - Pas de virgule finale, pas de champs supplémentaires non demandés.
2) Valeurs autorisées :
   - Lorsque des options sont fournies, COPIE-COLLE EXACTEMENT les valeurs (sensible à la casse, accents, underscores).
   - Aucune synonymie, aucune reformulation, aucune traduction.
3) Gestion de l'incertitude :
   - Si une valeur n'est pas déductible de manière certaine à partir du transcript et/ou des résultats d'outils, utilise la valeur par défaut fournie ou null selon la consigne.
   - Pour les listes (multiselect), retourne [] s'il n'y a aucune valeur applicable.
4) Source d'information :
   - Base-toi UNIQUEMENT sur le transcript et les résultats d'outils fournis. N'invente pas d'informations.
   - N'infère pas au-delà d'indices clairs et explicites.
5) Spécificités :
   - Les tags et raisons sont des identifiants machine (garde EXACTEMENT la forme fournie, y compris les underscores).
   - Pour le sentiment, analyse exclusivement l'appelant (ignorer l'agent).
6) Cohérence :
   - Respecte strictement le schéma demandé dans l'invite (noms de clés, type attendu).

Ne réponds QU'EN JSON valide, sans aucun texte additionnel.
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
        options = question_config.get("options")
        field_key = question_config.get("field_key")

        # Construire la liste des valeurs exactes si des options sont disponibles
        valid_values_text = ""
        if options and field_key:
            valid_values = [opt[field_key] for opt in options]
            valid_values_text = f"\n\nVALEURS EXACTES AUTORISÉES (utilise EXACTEMENT ces valeurs) :\n{', '.join(valid_values)}\n"

        # Format JSON attendu court et instruction brève
        if response_type == "select":
            json_format = f'"{name}": "valeur"'
            instruction = f"Sélectionne UNE seule valeur EXACTE{(' parmi les valeurs autorisées' if valid_values_text else '')}."
        elif response_type == "multiselect":
            json_format = f'"{name}": ["valeur1", "valeur2"]' + (" | null" if nullable else "")
            instruction = f"Sélectionne toutes les valeurs pertinentes{(' parmi les valeurs autorisées' if valid_values_text else '')} (liste vide [] si aucune). Utilise EXACTEMENT les valeurs fournies."
        elif response_type == "string":
            json_format = f'"{name}": "texte"' + (" | null" if nullable else "")
            instruction = "Fournis un texte explicatif."
        elif response_type == "number":
            json_format = f'"{name}": 123' + (" | null" if nullable else "")
            instruction = "Fournis un nombre."
        elif response_type == "boolean":
            json_format = f'"{name}": true' + (" | null" if nullable else "")
            instruction = "Fournis true ou false."
        elif response_type in ("text", "text_multiline"):  # Support rétrocompatibilité
            json_format = f'"{name}": "texte"' + (" | null" if nullable else "")
            instruction = "Fournis un texte explicatif."
        else:
            json_format = f'"{name}": null'
            instruction = "Retourne au bon format JSON."

        system_prompt = Config.BASE_SYSTEM_PROMPT

        # Règle absolue seulement pour select/multiselect avec options
        absolute_rule = ""
        if response_type in ("select", "multiselect") and valid_values_text:
            absolute_rule = "\nRÈGLE ABSOLUE: Copie-colle EXACTEMENT les valeurs depuis la liste fournie. Pas de variations, pas de reformulation.\n"

        user_prompt = f"""Tâche: Extraire l'attribut: {name}
But: {description}
Consignes: {instruction}{valid_values_text}{absolute_rule}

Rappels obligatoires :
- Réponds EXCLUSIVEMENT par un unique objet JSON valide (aucun texte hors JSON, aucun markdown, aucune explication).
- N'ajoute AUCUNE clé supplémentaire au schéma demandé.
- Si des options sont fournies, COPIE-COLLE EXACTEMENT les valeurs (casse/accents/underscores conservés).
- Si l'information est incertaine, utilise null, [] ou la valeur par défaut selon la consigne.
- Appuie-toi UNIQUEMENT sur le transcript et les résultats d'outils fournis (aucune invention).
- Ne modifie pas les intitulés ni l'ordre des sections suivantes : "Tâche:", "But:", "Consignes:", "Conversation:", "Résultats d'outils:".
- N'insère pas d'autres sections, titres ou séparateurs.

Format attendu (structure) :
{
    {json_format}
}

Conversation:
{conversation_text}

Résultats d'outils:
{tools_text}

{failure_note if failure_note else ""}"""

        return system_prompt, user_prompt

