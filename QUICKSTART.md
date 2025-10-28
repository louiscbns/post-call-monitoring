# Guide de Démarrage Rapide 🚀

## Installation

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Configurer les clés API
cp env.example .env
# Éditer .env et ajouter vos clés
```

## Configuration du fichier .env

Créez un fichier `.env` à la racine du projet :

```env
ROUNDED_API_KEY=your_rounded_api_key_here
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
```

## Usage

### Option 1: Analyse d'un appel directement

```bash
python main.py
```

Analyse l'appel `fb96d81d-fef2-4f68-b438-07a9fe97e65e` configuré par défaut.

### Option 2: Utiliser le script de test

```bash
python test_analysis.py
```

Analyse l'appel et sauvegarde le résultat dans un fichier JSON.

### Option 3: Utiliser dans votre code

```python
from main import PostCallMonitoringSystem

# Initialiser le système
system = PostCallMonitoringSystem(model_name="gpt-4o-mini")

# Analyser un appel
call_id = "fb96d81d-fef2-4f68-b438-07a9fe97e65e"
result = system.analyze_call_from_id(call_id)

# Afficher les résultats
system.print_analysis(result)
```

## Changer le call_id

Éditez `main.py` ligne 146 :
```python
call_id = "votre-nouveau-call-id"
```

Ou dans `test_analysis.py` ligne 40 :
```python
call_id = "votre-nouveau-call-id"
```

## Modèles disponibles

- `gpt-4o-mini` (OpenAI) - défaut
- `claude-3-5-sonnet` (Anthropic)
- `gemini-2.0-flash` (Google)

Pour changer de modèle:
```python
system = PostCallMonitoringSystem(model_name="claude-3-5-sonnet")
```

## Debug des données API

Pour voir les données brutes récupérées de l'API Call Rounded :

```python
from rounded_api import RoundedAPIClient

client = RoundedAPIClient()
client.get_call_details("fb96d81d-fef2-4f68-b438-07a9fe97e65e")
```

## Structure des résultats

L'analyse génère :
- ✅ **Détection d'erreurs** : Type et description du problème
- 🏷️ **Tags** : Catégorisation automatique
- 📊 **Étapes d'analyse** : Questions structurées générées par le LLM
- 💡 **Recommandations** : Actions pour éviter le problème
- 📝 **Résumé** : Synthèse en 2-3 phrases

## Format de sortie

L'analyse est affichée dans le terminal et sauvegardée en JSON.

## Troubleshooting

### Erreur "Impossible de récupérer l'appel"
- Vérifiez que votre `ROUNDED_API_KEY` est correcte dans `.env`
- Vérifiez que le `call_id` est valide
- Vérifiez votre connexion internet

### Erreur "Modèle non supporté"
- Vérifiez que vous avez la clé API correspondante dans `.env`
- Vérifiez le nom du modèle (doit correspondre exactement)

### Pas d'erreur détectée
C'est normal ! Le système ne génère une analyse détaillée que si une erreur est détectée dans l'appel.

## Support

Pour toute question ou problème, vérifiez :
1. Les clés API sont correctement configurées
2. Le `call_id` est valide et accessible
3. Les dépendances sont installées (`pip install -r requirements.txt`)

