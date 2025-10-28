# Architecture du Système d'Analyse Post-Appel

## 📐 Vue d'ensemble

Le système utilise une architecture en 2 étapes :

```
┌──────────────────────────────────────────────────┐
│           POSTCALL MONITORING SYSTEM             │
└──────────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼────────┐     ┌─────────▼──────────┐
│ ERROR DETECTOR │     │ DETAILED ANALYZER  │
│  (Étape 1)     │──NO─│   (Étape 2)        │
│                │     │   (Conditionnel)   │
└───────┬────────┘     └──────────┬─────────┘
        │                         │
        └──────────┬──────────────┘
                   │
          ┌────────▼────────┐
          │   LLM CLIENT    │
          │  (Multi-Modèle) │
          └─────────────────┘
```

## 🔄 Flow d'Analyse

### Étape 1 : Détection Initiale (ErrorDetector)

**Objectif** : Détecter si une erreur existe dans l'appel

**Input** :
- Conversation complète (user + assistant)
- Résultats des tools (entrées/sorties)
- Métadonnées de l'appel

**Output** :
```python
InitialAnalysis(
    has_error: bool
    error_type: ProblemType
    error_description: str
    confidence: float
    context: dict
)
```

**Décision** :
- Si `has_error == False` → **FIN** (aucune analyse détaillée)
- Si `has_error == True` → **Étape 2**

### Étape 2 : Analyse Détaillée (DetailedAnalyzer)

**Objectif** : Générer une analyse approfondie avec questions/réponses

**Input** :
- Requête d'analyse complète
- Résultat de l'étape 1 (InitialAnalysis)

**Output** :
```python
DetailedAnalysis(
    problem_type: str
    problem_detected: bool
    steps: List[AnalysisStep]  # Questions structurées
    tags: List[str]            # Tags automatiques
    summary: str               # Résumé concis
    recommendations: List[str] # Actions recommandées
)
```

## 🧩 Composants

### 1. ErrorDetector (`error_detector.py`)

**Responsabilités** :
- Analyser le contexte complet de l'appel
- Détecter les erreurs dans les tools
- Classifier le type de problème
- Calculer la confiance de détection

**Prompt System** :
```
Expert en analyse de conversations clients.
Détecte les erreurs et problèmes dans les appels.
Types: parsing_error, api_error, misunderstanding, etc.
Répond UNIQUEMENT avec JSON valide.
```

### 2. DetailedAnalyzer (`detailed_analyzer.py`)

**Responsabilités** :
- Générer des étapes d'analyse structurées
- Créer des questions multiple choice / open-ended
- Générer des tags automatiques
- Produire un résumé et des recommandations

**Génère Dynamiquement** :
- **Questions** : Adaptées au type d'erreur détecté
- **Tags** : Liste depuis Config.COMMON_TAGS
- **Résumé** : Synthèse en 2-3 phrases
- **Recommandations** : Actions concrètes

### 3. LLMClient (`llm_clients.py`)

**Support Multi-Provider** :
- OpenAI GPT-4o Mini
- Anthropic Claude 3.5 Sonnet
- Google Gemini 2.0 Flash

**API Unifiée** :
```python
client.generate(prompt, system_prompt, **kwargs)
```

### 4. RoundedAPIClient (`rounded_api.py`)

**Fonctionnalités** :
- Récupération d'appels par ID
- Transformation flexible des données
- Gestion multi-format (transcript/conversation/messages)

**Méthodes** :
- `get_call(call_id)` → Données brutes
- `list_calls(limit)` → Liste d'appels
- `transform_call_data(data)` → Standardisation
- `get_call_details(call_id)` → Debug

### 5. PostCallMonitoringSystem (`main.py`)

**Point d'entrée principal** :
```python
system = PostCallMonitoringSystem(model_name="gpt-4o-mini")
result = system.analyze_call_from_id(call_id)
system.print_analysis(result)
```

**Méthodes** :
- `analyze_call_from_id(call_id)` → Récupère et analyse
- `analyze_call(request)` → Analyse une requête
- `print_analysis(analysis)` → Affichage formaté

## 🏷️ Types de Problèmes

| Type | Description | Exemple |
|------|-------------|---------|
| `parsing_error` | Erreur de parsing | JSON invalide |
| `api_error` | Erreur API | Timeout, retour vide |
| `misunderstanding` | Malentendu | Info incorrecte |
| `missing_info` | Info manquante | Données incomplètes |
| `technical_error` | Erreur technique | Crash, timeout |
| `other` | Autre | Non catégorisé |

## 📊 Données Utilisées

### 1. Conversation (OBLIGATOIRE)
```python
List[ConversationTurn(
    role: "user" | "assistant"
    content: str
    timestamp: str
)]
```

### 2. Tool Results (TRÈS IMPORTANT)
```python
List[ToolResult(
    tool_name: str
    input: dict
    output: dict
    success: bool
    error_message: str
)]
```

### 3. Metadata (OPTIONNEL)
```python
CallMetadata(
    call_id: str
    duration: int
    status: str
    triggered_tool: str
    timestamp: str
)
```

## 🔍 Analyse des Erreurs

### Indicateurs Clés

**Erreurs de Tools** :
- `success == False`
- `error_message` non vide
- `output` vide ou invalide

**Malentendus** :
- Répétitions dans la conversation
- Questions du client non résolues
- Changements de sujet fréquents

**Données Manquantes** :
- Tools retournent `{}`
- Champs requis absents
- Validations échouées

## 🎯 Avantages de l'Architecture

1. **Conditionnel** : Analyse détaillée UNIQUEMENT si erreur détectée
2. **Flexible** : Support multi-modèles LLM
3. **Extensible** : Tags personnalisables dans Config
4. **Automatique** : Pas besoin de lire les logs manuellement
5. **Structuré** : Questions générées dynamiquement par le LLM

## 🔧 Personnalisation

### Ajouter des Tags

```python
# config.py
COMMON_TAGS = [
    "votre_tag",
    # ...
]
```

### Changer de Modèle

```python
system = PostCallMonitoringSystem(model_name="claude-3-5-sonnet")
```

### Modifier les Prompts

Éditez les méthodes `_get_system_prompt()` dans :
- `error_detector.py`
- `detailed_analyzer.py`

## 📈 Performance

- **Détection** : ~2-5s par appel
- **Analyse détaillée** : ~5-10s si erreur détectée
- **Total** : ~2-10s selon la complexité

## 🚀 Évolutions Futures

- Dashboard web
- Export CSV/JSON
- Alertes automatiques
- Tendance analysis
- Score qualité par agent
- API REST

