# 📱 Guide d'utilisation - Application Streamlit

## Installation

1. Assurez-vous que toutes les dépendances sont installées:
```bash
pip install -r requirements.txt
```

2. Configurez vos variables d'environnement dans le fichier `.env`:
```env
ROUNDED_API_KEY=votre_clé_api_rounded
OPENAI_API_KEY=votre_clé_openai
ANTHROPIC_API_KEY=votre_clé_anthropic (optionnel)
GOOGLE_API_KEY=votre_clé_google (optionnel)
```

## Lancement de l'application

Pour lancer l'application Streamlit, exécutez:
```bash
streamlit run app.py
```

L'application s'ouvrira dans votre navigateur à l'adresse: `http://localhost:8501`

## Utilisation

### 1. Entrer un Call ID
Dans le champ "Call ID", entrez l'identifiant unique de l'appel que vous souhaitez analyser.

**Exemple:** `c4739276-0207-4bb4-b3e1-dabe55319c10`

Vous pouvez également cliquer sur le bouton "📋 Utiliser un exemple" pour utiliser un Call ID de démonstration.

### 2. Choisir le modèle LLM
Dans la barre latérale à gauche, sélectionnez le modèle LLM à utiliser pour l'analyse:
- **gpt-4o-mini** (recommandé, rapide et économique)
- **claude-3-5-sonnet** (analyse plus approfondie)
- **gemini-2.0-flash** (raisonnement étape par étape)

### 3. Lancer l'analyse
Cliquez sur le bouton "🚀 Analyser" pour démarrer l'analyse de l'appel.

L'application va:
- Récupérer les données de l'appel depuis l'API Call Rounded
- Analyser la conversation et les résultats des outils
- Détecter les erreurs et problèmes
- Générer un résumé avec des tags et recommandations

### 4. Consulter les résultats
Les résultats sont affichés avec:
- **Status**: Indique si un problème a été détecté
- **Type de problème**: Catégorie du problème (parsing_error, api_error, etc.)
- **Tags**: Liste des tags associés à l'appel
- **Résumé**: Description concise du problème
- **Détails**: Informations complémentaires dans une section extensible

### 5. Exporter les résultats
Vous pouvez exporter les résultats au format JSON en cliquant sur "📥 Exporter les résultats" dans la section détaillée.

## Fonctionnalités

### Détection automatique d'erreurs
L'application détecte automatiquement:
- Erreurs de parsing
- Erreurs API
- Malentendus avec le client
- Informations manquantes
- Erreurs techniques

### Tags disponibles
Les tags suivants sont utilisés pour catégoriser les problèmes:
- `erreur_parsing` - Erreur lors du parsing
- `requete_api_vide` - API retourne vide
- `malentendu_client` - Malentendu avec le client
- `information_manquante` - Info manquante
- `erreur_technique` - Erreur technique
- `timeout` - Timeout
- `donnees_invalides` - Données invalides
- `connexion_echouee` - Connexion échouée
- `validation_echouee` - Validation échouée

### Interface intuitive
- Design moderne et épuré
- Métriques visuelles
- Export JSON des résultats
- Configuration par sidebar

## Exemple d'utilisation

1. Ouvrez l'application: `streamlit run app.py`
2. Entrez un Call ID dans le champ prévu
3. Cliquez sur "🚀 Analyser"
4. Consultez les résultats affichés
5. (Optionnel) Exportez les résultats en JSON

## Dépannage

### Erreur de configuration
Si vous voyez un message d'erreur de configuration:
1. Vérifiez que le fichier `.env` existe
2. Vérifiez que toutes les clés API sont correctement renseignées
3. Redémarrez l'application après modification du `.env`

### Erreur lors de l'analyse
Si l'analyse échoue:
1. Vérifiez que le Call ID est correct
2. Vérifiez que vous avez une connexion internet active
3. Vérifiez les logs dans la console pour plus de détails

### L'application ne se lance pas
1. Vérifiez que streamlit est installé: `pip install streamlit`
2. Vérifiez que toutes les dépendances sont installées: `pip install -r requirements.txt`
3. Vérifiez que vous êtes dans le bon répertoire

## Support

Pour toute question ou problème, consultez:
- `README.md` - Documentation générale du projet
- `FONCTIONNEMENT.md` - Documentation technique détaillée
- `ARCHITECTURE.md` - Architecture du système

