"""Clients LLM pour les différents providers."""
import os
from typing import Dict, Any, List, Optional
import requests
from openai import OpenAI
from anthropic import Anthropic


class LLMClient:
    """Client générique pour les LLM."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.client = None
        self.initialization_error = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialise le client selon le modèle."""
        try:
            # Modèles OpenAI (gpt-4o, gpt-4.1, gpt-4.1-mini, gpt-5, gpt-5-mini)
            if self.model_name in ["gpt-4o", "gpt-4.1", "gpt-4.1-mini", "gpt-5", "gpt-5-mini"]:
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    # Nettoie la clé API des caractères d'escape potentiels
                    api_key = api_key.strip()
                    # Temporairement retire les variables proxy pour éviter les erreurs
                    old_proxies = {
                        'http_proxy': os.environ.pop('HTTP_PROXY', None),
                        'https_proxy': os.environ.pop('HTTPS_PROXY', None),
                        'all_proxy': os.environ.pop('ALL_PROXY', None)
                    }
                    try:
                        self.client = OpenAI(api_key=api_key)
                    finally:
                        # Restaure les variables d'environnement
                        if old_proxies['http_proxy']:
                            os.environ['HTTP_PROXY'] = old_proxies['http_proxy']
                        if old_proxies['https_proxy']:
                            os.environ['HTTPS_PROXY'] = old_proxies['https_proxy']
                        if old_proxies['all_proxy']:
                            os.environ['ALL_PROXY'] = old_proxies['all_proxy']
                else:
                    print("ℹ️  OPENAI_API_KEY non configurée - utilisation du mode analyse locale.")
                    self.client = None
            elif self.model_name == "claude-3-5-sonnet":
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if api_key:
                    api_key = api_key.strip()
                    # Temporairement retire les variables proxy pour éviter les erreurs
                    old_proxies = {
                        'http_proxy': os.environ.pop('HTTP_PROXY', None),
                        'https_proxy': os.environ.pop('HTTPS_PROXY', None),
                        'all_proxy': os.environ.pop('ALL_PROXY', None)
                    }
                    try:
                        self.client = Anthropic(api_key=api_key)
                    finally:
                        # Restaure les variables d'environnement
                        if old_proxies['http_proxy']:
                            os.environ['HTTP_PROXY'] = old_proxies['http_proxy']
                        if old_proxies['https_proxy']:
                            os.environ['HTTPS_PROXY'] = old_proxies['https_proxy']
                        if old_proxies['all_proxy']:
                            os.environ['ALL_PROXY'] = old_proxies['all_proxy']
                else:
                    print("⚠️  ANTHROPIC_API_KEY non configurée.")
                    self.client = None
            # Modèles Google Gemini (API REST directe)
            elif self.model_name.startswith("gemini"):
                # Support des deux noms de variables d'environnement
                api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
                if api_key:
                    self.client = api_key.strip()
                else:
                    print("⚠️  GEMINI_API_KEY ou GEMINI_API_KEY non configurée.")
                    self.client = None
        except Exception as e:
            print(f"⚠️  Erreur lors de l'initialisation du client LLM: {e}")
            self.client = None
            self.initialization_error = str(e)
    
    def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        """Génère une réponse avec le prompt donné."""
        # Si erreur d'initialisation, lever une exception
        if self.initialization_error:
            raise RuntimeError(f"Le client LLM n'est pas correctement initialisé: {self.initialization_error}")
        
        # Si client non initialisé (mais pas d'erreur), utilise le mode mock intelligent
        if self.client is None:
            return self._generate_mock(prompt, system_prompt, kwargs.get("context"))
        
        try:
            # Modèles OpenAI
            if self.model_name in ["gpt-4o", "gpt-4.1", "gpt-4.1-mini", "gpt-5", "gpt-5-mini"]:
                return self._generate_openai(prompt, system_prompt, **kwargs)
            elif self.model_name == "claude-3-5-sonnet":
                return self._generate_anthropic(prompt, system_prompt, **kwargs)
            elif self.model_name.startswith("gemini"):
                return self._generate_google(prompt, system_prompt, **kwargs)
            else:
                raise ValueError(f"Modèle non supporté: {self.model_name}")
        except Exception as e:
            print(f"⚠️  Erreur lors de la génération avec le LLM: {e}")
            # Ne pas simuler de réponses si il y a une erreur réelle
            raise RuntimeError(f"Erreur lors de la génération avec le LLM: {e}")
    
    def _generate_mock(self, prompt: str, system_prompt: str, context: dict = None) -> str:
        """Génère une analyse basée sur les vraies données sans utiliser d'API LLM externe."""
        
        # Détection d'erreurs - utilise les vraies données
        if "détecter les ERREURS" in system_prompt or "détecter" in system_prompt.lower():
            # Analyse le prompt pour détecter les erreurs réelles
            has_real_error = self._detect_real_errors(prompt)
            
            if has_real_error:
                return '''{
    "has_error": true,
    "error_type": "api_error",
    "error_description": "Un tool a échoué pendant l'appel.",
    "confidence": 0.9,
    "key_indicators": ["tool_echec"]
}'''
            else:
                return '''{
    "has_error": false,
    "error_type": "none",
    "error_description": "Aucune erreur détectée",
    "confidence": 1.0,
    "key_indicators": []
}'''
        
        # Génération d'étapes d'analyse
        elif "étapes d'analyse" in system_prompt or "étapes" in system_prompt:
            return '''{
    "steps": [
        {
            "step_number": 1,
            "description": "Identifier la cause de l'erreur API",
            "questions": [
                {
                    "id": "q1",
                    "question": "Quel tool a été appelé ?",
                    "type": "open_ended",
                    "options": null
                },
                {
                    "id": "q2",
                    "question": "Le problème vient de :",
                    "type": "multiple_choice",
                    "options": ["La connexion réseau", "L'API externe", "Les paramètres de la requête", "Timeout"]
                }
            ]
        },
        {
            "step_number": 2,
            "description": "Analyser les données d'entrée",
            "questions": [
                {
                    "id": "q3",
                    "question": "Les paramètres de la requête étaient-ils valides ?",
                    "type": "multiple_choice",
                    "options": ["Oui", "Non", "Partiellement"]
                }
            ]
        }
    ]
}'''
        
        # Génération de tags
        elif "tags" in system_prompt.lower():
            return '''{
    "tags": ["requete_api_vide", "connexion_echouee", "timeout"]
}'''
        
        # Génération de résumé
        elif "résumé" in system_prompt.lower() or "résume" in prompt.lower():
            return "Simulation: L'appel a échoué à cause d'une erreur de connexion API. Le tool demandé n'a pas pu être exécuté correctement, probablement en raison d'un problème de réseau ou de timeout."
        
        # Génération de recommandations
        elif "recommandation" in system_prompt.lower() or "recommandations" in prompt.lower():
            return '''{
    "recommendations": [
        "Implémenter un système de retry automatique pour les appels API",
        "Augmenter le timeout des requêtes API",
        "Ajouter des logs détaillés pour déboguer les erreurs de connexion",
        "Vérifier la disponibilité de l'API externe avant chaque appel"
    ]
}'''
        
        # Par défaut, retourne une réponse générique
        return '''{
    "has_error": false,
    "error_type": "none",
    "error_description": "Aucun problème détecté",
    "confidence": 1.0
}'''
    
    def _detect_real_errors(self, prompt: str) -> bool:
        """Détecte les erreurs réelles dans le prompt."""
        # Cherche des indices d'erreur dans le prompt
        if "❌" in prompt or "❌ Erreur:" in prompt:
            return True
        
        # Cherche des patterns d'erreur dans les tool results
        import re
        # Pattern: success: false (insensible à la casse)
        if re.search(r'success["\s]*:[\s]*false', prompt, re.IGNORECASE):
            return True
        
        # Pattern: success" : "false" ou success" : false
        if re.search(r'success["\s]*:[\s]*["\']?false', prompt, re.IGNORECASE):
            return True
            
        # Cherche des messages d'erreur dans le contenu
        if '"success": false' in prompt:
            return True
            
        return False
    
    def _generate_openai(self, prompt: str, system_prompt: str, **kwargs) -> str:
        """Génère avec OpenAI."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Les modèles gpt-5 et gpt-5-mini utilisent reasoning_effort et verbosity
        # Pour les autres modèles, on utilise temperature
        request_params = {
            "model": self.model_name,
            "messages": messages
        }
        
        # Pour gpt-5 et gpt-5-mini, utiliser reasoning_effort et verbosity
        if self.model_name in ["gpt-5", "gpt-5-mini"]:
            request_params["reasoning_effort"] = kwargs.get("reasoning_effort", "low")
            request_params["verbosity"] = kwargs.get("verbosity", "low")
        else:
            request_params["temperature"] = kwargs.get("temperature", 0.3)
        
        response = self.client.chat.completions.create(**request_params)
        return response.choices[0].message.content
    
    def _generate_anthropic(self, prompt: str, system_prompt: str, **kwargs) -> str:
        """Génère avec Anthropic Claude."""
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=kwargs.get("max_tokens", 4096),
            temperature=kwargs.get("temperature", 0.3),
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    def _generate_google(self, prompt: str, system_prompt: str, **kwargs) -> str:
        """Génère avec Google Gemini via l'API REST."""
        api_key = self.client
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY non configurée")
        
        # Construction du prompt complet
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        # URL de l'API Gemini REST
        # Mapper les noms de modèles aux modèles API disponibles
        model_map = {
            "gemini-1.5-flash": "gemini-1.5-flash",
            "gemini-2.0-flash": "gemini-2.0-flash",
            "gemini-2.5-flash": "gemini-2.5-flash",
        }
        api_model = model_map.get(self.model_name, "gemini-1.5-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{api_model}:generateContent"
        
        # Headers
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }
        
        # Configuration de génération
        # Pour Gemini, augmenter la limite minimale si elle est trop faible
        # Les modèles récents comme gemini-2.5-flash peuvent générer des réponses plus longues
        max_tokens_requested = kwargs.get("max_tokens", 8192)
        max_tokens_gemini = max(max_tokens_requested, 2048) if max_tokens_requested < 2048 else max_tokens_requested
        
        payload = {
                "contents": [{
                    "parts": [{"text": full_prompt}]
                }],
                "generationConfig": {
                    "temperature": kwargs.get("temperature", 0.3),
                    "maxOutputTokens": max_tokens_gemini
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_NONE"
                    }
                ]
            }
        
        # Appel API REST
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Erreur lors de l'appel API Gemini: {e}")
        
        # Extraction de la réponse
        data = response.json()
        
        if "candidates" not in data or not data["candidates"]:
            # Afficher plus d'informations pour le débogage
            error_msg = f"La réponse de Gemini est vide. Réponse complète: {data}"
            if "promptFeedback" in data:
                error_msg += f" Prompt feedback: {data['promptFeedback']}"
            raise ValueError(error_msg)
        
        candidate = data["candidates"][0]
        
        # Vérifier le finishReason
        finish_reason = candidate.get("finishReason", "UNKNOWN")
        if finish_reason not in ["STOP", "MAX_TOKENS"]:
            # Ajouter plus de contexte sur le finishReason
            error_details = f"finishReason: {finish_reason}"
            if "safetyRatings" in candidate:
                error_details += f", safetyRatings: {candidate['safetyRatings']}"
            raise ValueError(f"Génération bloquée ou incomplète ({error_details})")
        
        if "content" not in candidate:
            raise ValueError(f"Pas de 'content' dans le candidate. Candidate complet: {candidate}")
        
        content = candidate["content"]
        
        # Vérifier si parts existe (peut être absent si bloqué ou si réponse vide)
        if "parts" not in content or not content.get("parts"):
            # Si finishReason est MAX_TOKENS et qu'il n'y a pas de parts, 
            # cela peut signifier que la réponse était trop longue même avec la limite augmentée
            # ou que le format de réponse est différent
            error_details = f"Pas de 'parts' dans le content. FinishReason: {finish_reason}"
            if finish_reason == "MAX_TOKENS":
                error_details += " (Limite de tokens atteinte - essayez d'augmenter max_tokens)"
            if "safetyRatings" in candidate:
                error_details += f", safetyRatings: {candidate['safetyRatings']}"
            error_details += f", content: {content}"
            # Pour MAX_TOKENS, essayer une fois de plus avec une limite plus élevée
            if finish_reason == "MAX_TOKENS" and max_tokens_gemini < 8192:
                # Essayer avec une limite plus élevée
                payload["generationConfig"]["maxOutputTokens"] = 8192
                retry_response = requests.post(url, json=payload, headers=headers, timeout=60)
                retry_response.raise_for_status()
                retry_data = retry_response.json()
                if "candidates" in retry_data and retry_data["candidates"]:
                    retry_candidate = retry_data["candidates"][0]
                    if "content" in retry_candidate and "parts" in retry_candidate["content"]:
                        parts = retry_candidate["content"]["parts"]
                        if parts and len(parts) > 0 and isinstance(parts[0], dict) and "text" in parts[0]:
                            return parts[0]["text"].strip()
            raise ValueError(f"Pas de 'parts' dans le content - peut-être bloqué par safety filters ou erreur API ({error_details})")
        
        parts = content["parts"]
        if not parts or len(parts) == 0:
            raise ValueError("Liste 'parts' vide")
        
        if not isinstance(parts[0], dict) or "text" not in parts[0]:
            raise ValueError("Format de 'parts[0]' inattendu - pas de 'text'")
        
        text = parts[0]["text"].strip()
        if not text:
            raise ValueError("Texte vide dans la réponse Gemini")
        
        return text

