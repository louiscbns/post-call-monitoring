# 🚀 Déploiement Automatique sur Vercel

## 📋 Résumé

Votre application est maintenant prête à être déployée automatiquement sur Vercel !

## 🎯 Étapes pour déployer

### 1. Connecter votre GitHub à Vercel

1. Allez sur [vercel.com](https://vercel.com)
2. Sign in avec votre compte GitHub
3. Cliquez sur **"Add New..."** → **"Project"**
4. Importez le repository : `louiscbns/post-call-monitoring`
5. Cliquez sur **"Import"**

### 2. Configurer le projet

Vercel détecte automatiquement la configuration :
- ✅ Framework: Other
- ✅ Root Directory: `/`
- ✅ Build Command: (aucun, géré automatiquement)
- ✅ Output Directory: `static`

### 3. Ajouter les variables d'environnement

Dans la section **"Environment Variables"**, ajoutez :

```bash
ROUNDED_API_KEY=votre_clé_rounded_api
OPENAI_API_KEY=votre_clé_openai
```

**Optionnel** (pour les autres modèles) :
```bash
ANTHROPIC_API_KEY=votre_clé_anthropic
GOOGLE_API_KEY=votre_clé_google
```

### 4. Déployer !

Cliquez sur **"Deploy"** et attendez ~2 minutes.

## 🎉 Votre app sera accessible sur :

```
https://post-call-monitoring-[votre-nom].vercel.app
```

## 📁 Structure du projet

```
post-call-monitoring/
├── api/
│   ├── analyze.py        # Endpoint d'analyse
│   ├── health.py         # Health check
│   └── requirements.txt  # Dépendances Python
├── static/
│   └── index.html        # Interface web
├── vercel.json           # Configuration Vercel
├── main.py               # Système d'analyse
└── ...autres fichiers
```

## 🔄 Déploiement automatique

Une fois configuré :
- ✅ Chaque push sur `main` → Déploiement en production
- ✅ Chaque Pull Request → URL de preview
- ✅ Vercel build automatiquement

## 🧪 Tester l'API

### Health Check
```bash
curl https://votre-app.vercel.app/api/health
```

### Analyser un appel
```bash
curl -X POST https://votre-app.vercel.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "c4739276-0207-4bb4-b3e1-dabe55319c10",
    "model": "gpt-4o-mini"
  }'
```

## 🎨 Interface Web

L'interface web est disponible à :
```
https://votre-app.vercel.app/
```

Permet de :
- ✅ Saisir un Call ID
- ✅ Choisir le modèle LLM
- ✅ Voir les résultats en temps réel
- ✅ Export JSON

## 🐛 Dépannage

### Erreur de build

**Problème** : `Module not found`
**Solution** : Vérifiez que toutes les dépendances sont dans `api/requirements.txt`

**Problème** : `Import error`
**Solution** : Vérifiez que les fichiers dans `api/` importent correctement les modules parent

### Variables d'environnement manquantes

Assurez-vous d'avoir ajouté toutes les clés API nécessaires dans Vercel Dashboard.

### L'API retourne 404

Vérifiez que `vercel.json` contient bien les routes pour `/api/analyze` et `/api/health`.

## 📚 Documentation

- [VERCEL_DEPLOY.md](VERCEL_DEPLOY.md) - Guide détaillé
- [DEPLOYMENT.md](DEPLOYMENT.md) - Options de déploiement
- [README.md](README.md) - Documentation générale

## 🔗 Ressources utiles

- [Repository GitHub](https://github.com/louiscbns/post-call-monitoring)
- [Documentation Vercel](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python)

---

**Bon déploiement ! 🚀**

