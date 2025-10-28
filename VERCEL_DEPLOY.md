# 🚀 Déploiement Automatique sur Vercel

## Vue d'ensemble

Cette application est configurée pour se déployer automatiquement sur Vercel à chaque push sur GitHub.

## 🎯 Démarrage Rapide

### 1. Installer Vercel CLI (optionnel)

```bash
npm i -g vercel
```

### 2. Connecter votre repository GitHub à Vercel

1. Allez sur [vercel.com](https://vercel.com)
2. Connectez votre compte GitHub
3. Cliquez sur **"Import Project"**
4. Sélectionnez le repository `louiscbns/post-call-monitoring`
5. Vercel détectera automatiquement la configuration

### 3. Configurer les variables d'environnement

Dans la page de configuration Vercel, ajoutez vos clés API :

```
ROUNDED_API_KEY=votre_clé_rounded_api
OPENAI_API_KEY=votre_clé_openai
ANTHROPIC_API_KEY=votre_clé_anthropic (optionnel)
GOOGLE_API_KEY=votre_clé_google (optionnel)
```

Ou utilisez la CLI :
```bash
vercel env add ROUNDED_API_KEY
vercel env add OPENAI_API_KEY
```

### 4. Déployer

Vercel déploiera automatiquement votre application !

- **Première fois** : Lancez le déploiement depuis Vercel Dashboard
- **Après** : Chaque push sur GitHub déclenchera automatiquement un nouveau déploiement

### 5. Obtenir l'URL

Votre application sera accessible sur :
```
https://post-call-monitoring-[hash].vercel.app
```

## 📁 Structure des fichiers

```
post-call-monitoring/
├── api.py              # API Flask (déployé sur Vercel)
├── vercel.json         # Configuration Vercel
├── static/
│   └── index.html      # Interface web
├── main.py             # Système d'analyse
├── requirements.txt    # Dépendances Python
└── ...
```

## 🔧 Configuration Vercel

Le fichier `vercel.json` configure :

- **API Route** : `/api/*` → Pointe vers `api.py`
- **Static Files** : Les fichiers dans `static/` sont servis
- **Build** : Utilise `@vercel/python` pour l'API Flask

## 🚀 Déploiement manuel avec CLI

Si vous préférez déployer manuellement :

```bash
# Login à Vercel
vercel login

# Déployer
vercel

# Déployer en production
vercel --prod
```

## 🔄 Mise à jour automatique

Une fois configuré, Vercel déploie automatiquement :

1. **Push sur main** → Production (`https://votre-app.vercel.app`)
2. **Pull Request** → Preview URL (pour tester avant merge)

## 📝 API Endpoints

### POST `/api/analyze`
Analyse un appel.

**Request:**
```json
{
  "call_id": "c4739276-0207-4bb4-b3e1-dabe55319c10",
  "model": "gpt-4o-mini"
}
```

**Response:**
```json
{
  "success": true,
  "call_id": "...",
  "problem_detected": true,
  "problem_type": "parsing_error",
  "tags": ["erreur_parsing"],
  "summary": "...",
  "recommendations": [...]
}
```

### GET `/api/health`
Vérifie que l'API fonctionne.

## 🎨 Interface Web

L'interface web (`/static/index.html`) permet de :
- Saisir un Call ID
- Choisir le modèle LLM
- Voir les résultats en temps réel

## 🐛 Dépannage

### Erreur "Module not found"
Assurez-vous que toutes les dépendances sont dans `requirements.txt`

### Erreur 404 sur l'API
Vérifiez que `vercel.json` est correctement configuré

### Variables d'environnement manquantes
Ajoutez toutes les clés API nécessaires dans Vercel Dashboard

## 📚 Ressources

- [Documentation Vercel](https://vercel.com/docs)
- [Documentation Flask on Vercel](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python)
- [Repository GitHub](https://github.com/louiscbns/post-call-monitoring)

