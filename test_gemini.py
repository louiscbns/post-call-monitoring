"""Script de test pour l'API Google Gemini (REST direct)."""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"


def call_gemini_api(api_key: str, model: str, prompt: str, temperature: float = 0.1, max_tokens: int = 10) -> str:
    """Appelle l'API Gemini via REST."""
    url = f"{GEMINI_API_BASE}/models/{model}:generateContent"
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens
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
    
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    
    # Debug: afficher la réponse complète si problème
    if "candidates" not in data or not data["candidates"]:
        print(f"DEBUG - Réponse complète: {data}")
        raise ValueError("Aucune réponse dans les candidates")
    
    candidate = data["candidates"][0]
    
    # Vérifier le finishReason (MAX_TOKENS est acceptable si on a du contenu)
    finish_reason = candidate.get("finishReason", "UNKNOWN")
    if finish_reason not in ["STOP", "MAX_TOKENS"]:
        print(f"⚠️  ATTENTION - finishReason: {finish_reason}")
        if finish_reason in ["SAFETY", "RECITATION"]:
            print(f"DEBUG - Candidate complet: {candidate}")
            raise ValueError(f"Génération bloquée ou incomplète (finishReason: {finish_reason})")
    
    # Debug: vérifier la structure
    if "content" not in candidate:
        print(f"DEBUG - Candidate: {candidate}")
        raise ValueError("Pas de 'content' dans le candidate")
    
    content = candidate["content"]
    
    # Vérifier si parts existe
    if "parts" not in content or not content.get("parts"):
        print(f"DEBUG - Content complet: {content}")
        print(f"DEBUG - Candidate complet: {candidate}")
        print(f"DEBUG - Réponse complète: {data}")
        raise ValueError("Pas de 'parts' dans le content - peut-être bloqué par safety filters ou limite de tokens trop basse")
    
    parts = content["parts"]
    if not parts or len(parts) == 0:
        print(f"DEBUG - Parts: {parts}")
        raise ValueError("Liste 'parts' vide")
    
    if not isinstance(parts[0], dict) or "text" not in parts[0]:
        print(f"DEBUG - First part: {parts[0]}")
        raise ValueError("Format de 'parts[0]' inattendu")
    
    text = parts[0]["text"].strip()
    if not text:
        raise ValueError("Texte vide dans la réponse")
    
    return text


def test_gemini():
    """Test simple de l'API Gemini via REST."""
    print("🧪 Test de l'API Google Gemini (REST)\n")
    
    # Récupérer la clé API
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY non trouvée dans les variables d'environnement")
        return False
    
    api_key = api_key.strip()
    print(f"🔑 Clé API : {api_key[:10]}...{api_key[-4:]}\n")
    
    try:
        # Test avec gemini-2.5-flash (comme dans votre curl)
        model = "gemini-2.5-flash"
        prompt = "Réponds uniquement avec le mot 'OK'."
        
        print(f"🤖 Modèle : {model}")
        print(f"📝 Prompt : {prompt}")
        print("📤 Envoi de la requête...\n")
        
        # Augmenter la limite de tokens pour avoir assez d'espace
        text = call_gemini_api(api_key, model, prompt, temperature=0.1, max_tokens=500)
        
        print(f"✅ Réponse reçue : {text}\n")
        return True
            
    except Exception as e:
        print(f"❌ Erreur : {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🔍 TEST API GOOGLE GEMINI (REST)")
    print("=" * 60)
    print()
    
    success = test_gemini()
    
    print("=" * 60)
    if success:
        print("✅ Test réussi !")
    else:
        print("❌ Test échoué")
        sys.exit(1)
    print("=" * 60)
