# 🚀 Guide de Déploiement

## Option 1 : Streamlit Cloud (Recommandé)

**Streamlit Cloud est gratuit et parfait pour les applications Streamlit.**

### Étapes de déploiement :

1. **Connecter votre repo GitHub à Streamlit Cloud**
   - Allez sur : https://streamlit.io/cloud
   - Cliquez sur "New app"
   - Connectez votre compte GitHub
   - Sélectionnez le repository : `louiscbns/post-call-monitoring`

2. **Configuration**
   - **Branch** : main
   - **Main file path** : `app.py`
   - **Python version** : 3.9+

3. **Variables d'environnement**
   Dans Streamlit Cloud, ajoutez vos secrets :
   ```
   ROUNDED_API_KEY=votre_clé_rounded
   OPENAI_API_KEY=votre_clé_openai
   ANTHROPIC_API_KEY=votre_clé_anthropic (optionnel)
   GOOGLE_API_KEY=votre_clé_google (optionnel)
   ```

4. **Déploiement automatique**
   - Streamlit Cloud déploie automatiquement à chaque push
   - Votre app sera accessible sur : `https://<votre-app>.streamlit.app`

### Avantages :
- ✅ Gratuit
- ✅ Déploiement automatique depuis GitHub
- ✅ Gestion native des secrets
- ✅ HTTPS automatique
- ✅ Pas de configuration serveur

---

## Option 2 : Vercel (API seulement)

Si vous voulez vraiment utiliser Vercel, vous devez convertir l'app en API REST avec Flask ou FastAPI.

### Créer une API Flask

Créez un fichier `api.py` :

```python
from flask import Flask, request, jsonify
from main import PostCallMonitoringSystem
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/api/analyze', methods=['POST'])
def analyze_call():
    data = request.json
    call_id = data.get('call_id')
    model = data.get('model', 'gpt-4o-mini')
    
    try:
        system = PostCallMonitoringSystem(model_name=model)
        result = system.analyze_call_from_id(call_id)
        
        if result:
            return jsonify({
                'success': True,
                'call_id': result.call_id,
                'problem_detected': result.problem_detected,
                'problem_type': result.problem_type,
                'tags': result.tags,
                'summary': result.summary
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Analysis failed'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})
```

### Configuration Vercel

Créez `vercel.json` :

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api.py"
    }
  ],
  "env": {
    "ROUNDED_API_KEY": "@rounded_api_key",
    "OPENAI_API_KEY": "@openai_api_key"
  }
}
```

### Déploiement sur Vercel

```bash
npm i -g vercel
vercel
```

---

## Option 3 : Railway ou Render

Ces plateformes supportent nativement les applications Streamlit.

### Railway

1. Créez un compte sur https://railway.app
2. New Project → Deploy from GitHub
3. Sélectionnez votre repo
4. Ajoutez les variables d'environnement
5. Votre app sera déployée automatiquement

### Render

1. Créez un compte sur https://render.com
2. New → Web Service
3. Connectez GitHub
4. Configuration :
   - Build Command : `pip install -r requirements.txt`
   - Start Command : `streamlit run app.py`
5. Déploiement automatique

---

## Recommandation

**Utilisez Streamlit Cloud** - c'est la solution la plus simple et la plus adaptée pour votre application Streamlit.

Souhaitez-vous que je vous guide à travers le déploiement sur Streamlit Cloud ?

