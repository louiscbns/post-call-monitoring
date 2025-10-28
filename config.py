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

