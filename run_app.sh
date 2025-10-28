#!/bin/bash

# Script pour lancer l'application Streamlit
# Usage: ./run_app.sh

echo "🚀 Lancement de l'application Streamlit..."
echo ""

# Vérifier que streamlit est installé
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit n'est pas installé"
    echo "📦 Installation en cours..."
    pip install -r requirements.txt
    echo ""
fi

# Vérifier que le fichier .env existe
if [ ! -f .env ]; then
    echo "⚠️  Le fichier .env n'existe pas"
    echo "📋 Création du fichier .env à partir de env.example..."
    if [ -f env.example ]; then
        cp env.example .env
        echo "✅ Fichier .env créé. Veuillez le modifier avec vos clés API."
    else
        echo "❌ Le fichier env.example n'existe pas"
        exit 1
    fi
    echo ""
fi

# Lancer l'application
echo "🌐 Ouverture de l'application dans le navigateur..."
streamlit run app.py

