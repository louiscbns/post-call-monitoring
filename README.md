# Système d'Analyse Post-Appel 🔍

Système intelligent pour identifier automatiquement les problèmes des agents sans avoir besoin de lire les logs manuellement.

## 🎯 Fonctionnalités

### 1. **Détection Automatique d'Erreurs**
- Analyse contextuelle des conversations
- Détection des erreurs dans les résultats des outils (tools)
- Classification automatique des types de problèmes

### 2. **Analyse Détaillée Conditionnelle**
- Si une erreur est détectée → déclenchement d'un flow d'analyse approfondie
- Génération dynamique de questions structurées
- Tags automatiques pour catégoriser les problèmes

### 3. **Support Multi-Modèles**
- **GPT-4o Mini** (OpenAI)
- **Claude 3.5 Sonnet** (Anthropic)  
- **Gemini 2.0 Flash** (Google)

### 4. **Intégration API Call Rounded**
- Récupération automatique des appels
- Transformation des données pour analyse

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│         PostCallMonitoringSystem            │
└─────────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼────┐          ┌──────▼───────┐
    │ Error   │          │  Detailed    │
    │Detector │          │  Analyzer    │
    └────┬────┘          └──────┬───────┘
         │                      │
         │              ┌───────▼──────┐
         │              │    LLM       │
         │              │   Client     │
         │              └───────┬──────┘
         │                      │
         └──────────────────────┘
                  │
         ┌────────▼────────┐
         │  Call Rounded   │
         │      API        │
         └─────────────────┘
```

## 📋 Structure du Projet

```
post-call-monitoring/
├── main.py                 # Point d'entrée principal
├── models.py               # Modèles de données (Pydantic)
├── error_detector.py       # Détection initiale d'erreurs
├── detailed_analyzer.py    # Analyse détaillée avec questions
├── llm_clients.py          # Clients multi-modèles
├── rounded_api.py          # Client API Call Rounded
├── config.py              # Configuration
├── requirements.txt        # Dépendances
├── .env.example           # Exemple de configuration
└── README.md              # Documentation
```

## 🚀 Installation

```bash
# Cloner ou télécharger le projet
cd post-call-monitoring

# Installer les dépendances
pip install -r requirements.txt

# Configurer les clés API
cp .env.example .env
# Éditer .env et ajouter vos clés API
```

## 🔑 Configuration API

Éditez le fichier `.env`:

```env
ROUNDED_API_KEY=your_rounded_api_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
```

## 💻 Utilisation

### Analyse d'un appel

```python
from main import PostCallMonitoringSystem

# Initialise le système
system = PostCallMonitoringSystem(model_name="gpt-4o-mini")

# Analyse depuis un call_id
result = system.analyze_call_from_id("your_call_id")

# Affiche les résultats
system.print_analysis(result)
```

### Exemple de sortie

```
🔍 Détection initiale d'erreurs...
Erreur détectée: True
Type: parsing_error
Confiance: 0.85

📊 Analyse détaillée en cours...

============================================================
📋 ANALYSE DÉTAILLÉE DE L'APPEL
============================================================

🆔 Call ID: call_123
⚠️  Problème détecté: True
🏷️  Type: parsing_error
🏷️  Tags: erreur_parsing, donnees_invalides

📝 Résumé:
   L'appel a échoué à cause d'une erreur de parsing des données
   retournées par l'API. Les données étaient en format inattendu.

🔬 Étapes d'analyse:
   
   Étape 1: Identifier le type d'erreur de parsing
      • Quel format de données était attendu?
      • Quel format a été reçu?
      • À quel moment l'erreur s'est-elle produite?

   Étape 2: Analyser la cause racine
      • Le parsing a-t-il échoué sur une requête spécifique?
      • Les données étaient-elles vides?
        - Oui
        - Non
        - Partiellement

💡 Recommandations:
   1. Ajouter une validation des données avant parsing
   2. Gérer les cas de retour vide de l'API
   3. Logger plus d'infos pour debug

============================================================
```

## 🔄 Flow d'Analyse

### Étape 1: Détection Initiale
- Le système analyse le contexte complet (conversation + tools)
- Détecte si une erreur existe
- **Si aucune erreur** → fin de l'analyse
- **Si erreur détectée** → passage à l'étape 2

### Étape 2: Analyse Détaillée
- Génération dynamique de questions structurées
- Classification avec tags appropriés
- Résumé concis
- Recommandations actionnables

## 🏷️ Tags Disponibles

- `erreur_parsing` - Erreur lors du parsing
- `requete_api_vide` - API retourne vide
- `malentendu_client` - Malentendu avec le client
- `information_manquante` - Info manquante
- `double_appel` - Double appel
- `erreur_technique` - Erreur technique
- `timeout` - Timeout
- `donnees_invalides` - Données invalides
- `connexion_echouee` - Connexion échouée
- `validation_echouee` - Validation échouée

## 🧠 Modèles Reasoning

Les modèles "reasoning" comme Gemini 2.0 permettent une analyse plus approfondie grâce à leur capacité de raisonnement étape par étape.

### Exemple d'utilisation avec Gemini

```python
system = PostCallMonitoringSystem(model_name="gemini-2.0-flash")
```

## 📊 Types de Problèmes Détectés

| Type | Description | Exemple |
|------|-------------|---------|
| `parsing_error` | Erreur de parsing | Données JSON invalides |
| `api_error` | Erreur API | Retour vide, timeout |
| `misunderstanding` | Malentendu | Client confus, info incorrecte |
| `missing_info` | Info manquante | Données incomplètes |
| `technical_error` | Erreur technique | Crash, timeout |
| `other` | Autre | Problème non catégorisé |

## 🔧 Personnalisation

### Ajouter des tags personnalisés

Éditez `config.py`:

```python
COMMON_TAGS = [
    "votre_tag_1",
    "votre_tag_2",
    # ...
]
```

### Modifier les modèles

```python
# Utiliser Claude
system = PostCallMonitoringSystem(model_name="claude-3-5-sonnet")

# Utiliser Gemini
system = PostCallMonitoringSystem(model_name="gemini-2.0-flash")
```

## 📝 Exemple de Données

```python
from models import CallAnalysisRequest, ConversationTurn, ToolResult

request = CallAnalysisRequest(
    call_id="call_123",
    conversation=[
        ConversationTurn(
            role="user", 
            content="Je veux réserver une table"
        ),
        ConversationTurn(
            role="assistant",
            content="Quel restaurant préférez-vous?"
        )
    ],
    tool_results=[
        ToolResult(
            tool_name="search_restaurant",
            input={"query": "restaurant paris"},
            output={},
            success=False,
            error_message="No results found"
        )
    ]
)
```

## 🚧 Roadmap

- [ ] Dashboard web pour visualisation
- [ ] Export CSV/JSON des analyses
- [ ] Alertes automatiques
- [ ] Analyse de tendances
- [ ] Score de qualité par agent
- [ ] API REST pour intégration

## 📄 Licence

MIT

## 👥 Auteur

Système développé pour l'analyse post-appel automatisée.

