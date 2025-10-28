"""Application Streamlit pour l'analyse post-appel."""
import streamlit as st
from main import PostCallMonitoringSystem
import time
import os
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration de la page
st.set_page_config(
    page_title="Analyse Post-Appel",
    page_icon="📞",
    layout="wide"
)

def main():
    """Application principale."""
    st.title("📞 Analyse Post-Appel")
    st.markdown("---")
    
    # Vérification de la configuration
    if not os.getenv("ROUNDED_API_KEY") or not os.getenv("OPENAI_API_KEY"):
        st.error("⚠️ Configuration incomplète. Veuillez vérifier vos variables d'environnement dans le fichier .env")
        with st.expander("Instructions de configuration"):
            st.code("""
# Copiez env.example vers .env
cp env.example .env

# Éditez .env et ajoutez vos clés API:
ROUNDED_API_KEY=votre_clé_api_rounded
OPENAI_API_KEY=votre_clé_openai
ANTHROPIC_API_KEY=votre_clé_anthropic (optionnel)
GOOGLE_API_KEY=votre_clé_google (optionnel)
            """)
        return
    
    # Sidebar pour la configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Sélection du modèle
        model = st.selectbox(
            "Modèle LLM",
            options=["gpt-4o-mini", "claude-3-5-sonnet", "gemini-2.0-flash"],
            index=0,
            help="Choisissez le modèle à utiliser pour l'analyse"
        )
        
        st.markdown("---")
        st.markdown("### ℹ️ Informations")
        st.info("""
        Cette application analyse les appels Call Rounded pour détecter automatiquement les problèmes et erreurs.
        """)
    
    # Zone de saisie du call_id
    st.header("🔍 Analyser un appel")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        call_id = st.text_input(
            "Call ID",
            placeholder="Ex: c4739276-0207-4bb4-b3e1-dabe55319c10",
            help="Entrez l'ID de l'appel à analyser"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Espacement vertical
        analyze_button = st.button("🚀 Analyser", type="primary", use_container_width=True)
    
    # Bouton pour afficher un exemple
    if st.button("📋 Utiliser un exemple"):
        call_id = "c4739276-0207-4bb4-b3e1-dabe55319c10"
        st.rerun()
    
    st.markdown("---")
    
    # Zone de résultats
    if analyze_button and call_id:
        analyze_call(call_id, model)
    elif analyze_button and not call_id:
        st.warning("⚠️ Veuillez entrer un Call ID")
    
    # Affichage des résultats stockés
    if "last_analysis" in st.session_state and "last_call_id" in st.session_state:
        if st.session_state.last_analysis and st.session_state.last_call_id:
            display_analysis(st.session_state.last_analysis, st.session_state.last_call_id)


def analyze_call(call_id: str, model: str):
    """Analyse un appel."""
    error_container = st.empty()
    
    try:
        # Vérification des variables d'environnement
        if not os.getenv("ROUNDED_API_KEY"):
            error_container.error("❌ ROUNDED_API_KEY non configurée")
            return
        
        if not os.getenv("OPENAI_API_KEY"):
            error_container.error("❌ OPENAI_API_KEY non configurée")
            return
        
        with st.spinner("🔍 Analyse en cours..."):
            # Initialise le système
            system = PostCallMonitoringSystem(model_name=model)
            
            # Affiche la progression
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Récupération des données de l'appel...")
            progress_bar.progress(0.2)
            
            # Analyse l'appel
            time.sleep(0.5)  # Simulation de délai pour l'UI
            result = system.analyze_call_from_id(call_id)
            
            progress_bar.progress(0.8)
            status_text.text("Finalisation de l'analyse...")
            time.sleep(0.3)
            
            if result:
                # Stocke les résultats dans la session
                st.session_state.last_analysis = result
                st.session_state.last_call_id = call_id
                
                progress_bar.progress(1.0)
                status_text.text("✅ Analyse terminée!")
                
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()
                
                st.success("✅ Analyse terminée avec succès!")
                
                # Affiche les résultats
                display_analysis(result, call_id)
                
                st.rerun()
            else:
                progress_bar.empty()
                status_text.empty()
                
                # Message d'erreur plus détaillé
                error_container.error("❌ L'analyse a échoué. Raisons possibles:")
                with st.expander("🔍 Détails de l'erreur"):
                    st.write("**Problèmes possibles:**")
                    st.markdown("""
                    1. **Call ID invalide** - Vérifiez que l'ID de l'appel existe
                    2. **Clés API invalides** - Vérifiez vos variables d'environnement
                    3. **Problème de connexion** - L'API Call Rounded pourrait être inaccessible
                    4. **Limite de taux** - Trop de requêtes à l'API OpenAI
                    """)
                    st.write(f"**Call ID testé:** `{call_id}`")
                    st.write(f"**Modèle utilisé:** `{model}`")
        
    except Exception as e:
        error_container.error(f"❌ Erreur lors de l'analyse: {str(e)}")
        with st.expander("🔍 Détails de l'erreur technique"):
            st.exception(e)
            st.write("**Type d'erreur:**", type(e).__name__)


def display_analysis(analysis, call_id: str):
    """Affiche les résultats de l'analyse."""
    if not analysis:
        st.warning("⚠️ Aucune analyse disponible")
        return
    
    st.header("📊 Résultats de l'analyse")
    
    # Métriques principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if analysis.problem_detected:
            st.metric("⚠️ Status", "Problème détecté", delta=None, delta_color="off")
        else:
            st.metric("✅ Status", "Aucun problème", delta=None)
    
    with col2:
        st.metric("🏷️ Type de problème", analysis.problem_type.replace("_", " ").title())
    
    with col3:
        st.metric("📊 Tags", len(analysis.tags))
    
    st.markdown("---")
    
    # Résumé
    st.subheader("📝 Résumé")
    with st.container():
        st.info(analysis.summary)
    
    # Tags
    if analysis.tags:
        st.subheader("🏷️ Tags")
        tag_cols = st.columns(min(len(analysis.tags), 5))
        for idx, tag in enumerate(analysis.tags):
            with tag_cols[idx % len(tag_cols)]:
                st.markdown(f"- `{tag}`")
    
    # Détails supplémentaires
    if analysis.problem_detected:
        st.markdown("---")
        st.subheader("🔍 Détails")
        
        with st.expander("📋 Informations détaillées"):
            st.write("**ID de l'appel:**")
            st.text(call_id)
            
            data_dict = {
                "call_id": call_id,
                "problem_type": analysis.problem_type,
                "problem_detected": analysis.problem_detected,
                "tags": analysis.tags,
                "summary": analysis.summary
            }
            st.json(data_dict)
    
    # Bouton pour re-analyser ou voir les données brutes
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Analyser un autre appel"):
            st.session_state.last_analysis = None
            st.session_state.last_call_id = None
            st.rerun()
    
    with col2:
        if st.button("📥 Exporter les résultats"):
            export_results(analysis, call_id)


def export_results(analysis, call_id: str):
    """Exporte les résultats au format JSON."""
    import json
    from datetime import datetime
    
    export_data = {
        "call_id": call_id,
        "timestamp": datetime.now().isoformat(),
        "problem_detected": analysis.problem_detected,
        "problem_type": analysis.problem_type,
        "tags": analysis.tags,
        "summary": analysis.summary,
        "recommendations": analysis.recommendations
    }
    
    # Crée le JSON
    json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
    
    # Téléchargement
    st.download_button(
        label="📥 Télécharger JSON",
        data=json_str,
        file_name=f"analysis_{call_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )


if __name__ == "__main__":
    main()

