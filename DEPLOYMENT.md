# 🚀 Guide de déploiement

## ⚠️ Pourquoi pas Vercel ?

Vercel est conçu pour des applications statiques et des fonctions serverless (serverless functions). Streamlit nécessite un serveur Python actif, ce qui n'est pas compatible avec le modèle serverless de Vercel.

## ✅ Solutions recommandées

### 1. Streamlit Cloud (Recommandé - Gratuit) ⭐

Streamlit Cloud est la solution la plus simple pour déployer des applications Streamlit.

#### Avantages
- ✅ Gratuit
- ✅ Déploiement en 1 clic
- ✅ Mises à jour automatiques à chaque push
- ✅ SSL automatique
- ✅ Pas de configuration requise

#### Étapes de déploiement

1. **Connecter votre repository GitHub**
   - Allez sur [share.streamlit.io](https://share.streamlit.io)
   - Connectez-vous avec votre compte GitHub
   - Cliquez sur "New app"

2. **Configurer l'application**
   - Repository : `louiscbns/post-call-monitoring`
   - Branch : `main`
   - Main file path : `app.py`

3. **Ajouter les secrets**
   - Dans les paramètres de l'app, ajoutez vos clés API comme secrets :
     - `ROUNDED_API_KEY`
     - `OPENAI_API_KEY`
     - `ANTHROPIC_API_KEY` (optionnel)
     - `GOOGLE_API_KEY` (optionnel)

4. **Déployer**
   - Cliquez sur "Deploy"
   - Streamlit Cloud déploie automatiquement votre app
   - L'URL sera : `https://post-call-monitoring-xxx.streamlit.app`

#### Mises à jour automatiques
À chaque push sur GitHub, l'application se met à jour automatiquement !

---

### 2. Render (Alternative)

Render est une plateforme cloud qui supporte les applications Streamlit.

#### Configuration nécessaire

1. **Créer un fichier `render.yaml`** :

```yaml
services:
  - type: web
    name: post-call-monitoring
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
    envVars:
      - key: ROUNDED_API_KEY
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: GOOGLE_API_KEY
        sync: false
```

2. **Déployer sur Render**
   - Connectez votre repo GitHub
   - Render détecte automatiquement le fichier `render.yaml`
   - Ajoutez vos variables d'environnement

---

### 3. Railway (Alternative)

Railway offre un déploiement simple avec support Python.

#### Étapes
1. Créez un compte sur [Railway.app](https://railway.app)
2. Nouveau projet → "Deploy from GitHub repo"
3. Sélectionnez votre repository
4. Ajoutez vos variables d'environnement
5. Railway déploie automatiquement

---

### 4. Heroku (Payant)

Pour déployer sur Heroku :

1. **Installer Heroku CLI**

2. **Créer les fichiers nécessaires**

```bash
# Procfile
echo "web: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile

# runtime.txt
echo "python-3.11.0" > runtime.txt
```

3. **Déployer**

```bash
heroku create votre-app-nom
git push heroku main
heroku config:set ROUNDED_API_KEY=votre_clé
heroku config:set OPENAI_API_KEY=votre_clé
```

---

## 🔐 Sécurité des clés API

### Sur Streamlit Cloud
1. Allez dans les paramètres de votre app
2. Cliquez sur "Secrets"
3. Ajoutez vos clés :
```toml
ROUNDED_API_KEY="votre_clé"
OPENAI_API_KEY="votre_clé"
```

### Sur les autres plateformes
Ajoutez les variables d'environnement dans les paramètres du déploiement.

---

## 📝 Résumé des options

| Plateforme | Coût | Complexité | Recommandation |
|------------|------|------------|----------------|
| **Streamlit Cloud** | Gratuit | ⭐ Facile | ⭐⭐⭐⭐⭐ |
| Render | Gratuit (limité) | ⭐⭐ Moyen | ⭐⭐⭐⭐ |
| Railway | $$ | ⭐⭐ Moyen | ⭐⭐⭐ |
| Heroku | $$ | ⭐⭐⭐ Difficile | ⭐⭐ |

---

## 🎯 Recommandation finale

Pour déployer rapidement votre application, utilisez **Streamlit Cloud** :
1. Gratuit
2. Le plus simple
3. Optimisé pour Streamlit
4. Déploiement automatique

**URL** : https://share.streamlit.io

---

## 📞 Support

Pour toute question sur le déploiement, consultez :
- Documentation Streamlit Cloud : https://docs.streamlit.io/streamlit-community-cloud
- Documentation Render : https://render.com/docs
- Documentation Railway : https://docs.railway.app

