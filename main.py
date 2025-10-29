"""Point d'entrée principal pour l'analyse post-appel."""
import asyncio
from typing import Optional
from models import CallAnalysisRequest, CallMetadata, ConversationTurn, ToolResult, DetailedAnalysis
from detailed_analyzer import DetailedAnalyzer
from rounded_api import RoundedAPIClient
import json


class PostCallMonitoringSystem:
    """Système principal d'analyse post-appel."""
    
    def __init__(self, model_name: str = "gpt-4o"):
        self.model_name = model_name
        self.detailed_analyzer = DetailedAnalyzer(model_name)
        self.rounded_api = RoundedAPIClient()
    
    def analyze_call_from_id(self, call_id: str, logger=None) -> Optional[DetailedAnalysis]:
        """Analyse un appel depuis son ID en utilisant l'API Call Rounded.
        
        Args:
            call_id: ID de l'appel à analyser
            logger: Fonction de logging optionnelle (ex: st.warning)
        """
        try:
            if logger:
                logger(f"Récupération de l'appel {call_id}...")
            
            # Récupère les données depuis Call Rounded
            raw_data = self.rounded_api.get_call(call_id)
            if not raw_data:
                error_msg = f"Impossible de récupérer l'appel {call_id} depuis l'API Call Rounded"
                print(error_msg)
                if logger:
                    logger(f"⚠️ {error_msg}")
                return None
            
            if logger:
                logger("Transformation des données...")
            
            # Transforme les données
            call_data = self.rounded_api.transform_call_data(raw_data)
            
            if logger:
                logger("Construction de la requête d'analyse...")
            
            # Construit la requête d'analyse
            request = self._build_analysis_request(call_data)
            
            if logger:
                logger("Lancement de l'analyse...")
            
            # Analyse l'appel
            return self.analyze_call(request)
        except RuntimeError as e:
            error_msg = f"Erreur critique LLM: {e}"
            print(f"\n❌ {error_msg}")
            if logger:
                logger(f"🚫 {error_msg}")
            return None
        except Exception as e:
            error_msg = f"Erreur inattendue: {e}"
            print(f"\n❌ {error_msg}")
            if logger:
                logger(f"❌ {error_msg}")
            return None
    
    def analyze_call(self, request: CallAnalysisRequest) -> DetailedAnalysis:
        """Analyse un appel avec la requête fournie."""
        try:
            # Analyse directe (inclut l'extraction des statistiques avec failure_reasons et failure_description)
            print("📊 Analyse en cours...")
            detailed = self.detailed_analyzer.analyze(request)
            
            # Log concis du résultat (valeurs exactes)
            if detailed.problem_detected:
                reasons = ", ".join(detailed.statistics.failure_reasons or [])
                print(f"✅ Analyse terminée - Problème détecté: {reasons}")
            else:
                print("✅ Analyse terminée - Aucun problème détecté")
            
            return detailed
        except RuntimeError as e:
            print(f"\n❌ Erreur LLM: {e}")
            raise
        except Exception as e:
            print(f"\n❌ Erreur lors de l'analyse: {e}")
            raise
    
    def _build_analysis_request(self, call_data: dict) -> CallAnalysisRequest:
        """Construit la requête d'analyse depuis les données brutes."""
        # Extrait la conversation depuis le transcript
        conversation = []
        for item in call_data.get("transcript", []):
            if isinstance(item, dict):
                role = item.get("role", "")
                # On ignore les rôles "task_switch" et "tool" qui ne sont pas des tours de conversation
                if role in ["agent", "user", "assistant"]:
                    conversation.append(ConversationTurn(
                        role=role,
                        content=item.get("content", ""),
                        timestamp=item.get("start_time")
                    ))
        
        # Extrait les résultats d'outils
        tool_results = []
        for tool in call_data.get("tools", []):
            if isinstance(tool, dict):
                # Détermine le message d'erreur
                error_message = None
                if not tool.get("success", True):
                    # Si le tool a échoué, extrait le message d'erreur depuis output ou error
                    output = tool.get("output", {})
                    if isinstance(output, dict):
                        error_message = output.get("error") or output.get("message") or tool.get("error")
                    else:
                        error_message = tool.get("error")
                
                tool_results.append(ToolResult(
                    tool_name=tool.get("name", ""),
                    input=tool.get("input", {}),
                    output=tool.get("output", {}),
                    success=tool.get("success", True),
                    error_message=error_message,
                    timestamp=tool.get("timestamp")
                ))
        
        # Construit les métadonnées avec gestion des types
        call_id = call_data.get("call_id") or "unknown"
        
        # Convertit status en string si c'est un int (code HTTP)
        status_value = call_data.get("status")
        if isinstance(status_value, int):
            status_value = str(status_value)
        
        metadata = CallMetadata(
            call_id=call_id,
            duration=call_data.get("duration"),
            status=status_value,
            triggered_tool=call_data.get("metadata", {}).get("tool"),
            timestamp=call_data.get("metadata", {}).get("timestamp")
        )
        
        return CallAnalysisRequest(
            call_id=call_id,
            conversation=conversation,
            tool_results=tool_results,
            metadata=metadata
        )
    
    def print_analysis(self, analysis: DetailedAnalysis):
        """Affiche l'analyse de manière lisible."""
        print("\n" + "="*70)
        print(f"📋 ANALYSE - Call ID: {analysis.call_id}")
        print("="*70)
        
        # Résumé concis
        print(f"📝 {analysis.summary}")
        
        # Statistiques enrichies - format compact avec valeurs exactes
        if analysis.statistics:
            # Motif de l'appel
            if analysis.statistics.call_reason:
                print(f"Motif de l'appel : {analysis.statistics.call_reason}")
            
            # Score de satisfaction
            if analysis.statistics.user_sentiment:
                print(f"Score de Satisfaction : {analysis.statistics.user_sentiment}")
            
            # Erreurs si présentes (format compact avec valeurs exactes)
            if analysis.statistics.failure_reasons and len(analysis.statistics.failure_reasons) > 0:
                reasons_str = ", ".join(analysis.statistics.failure_reasons)
                print(f"❌ Erreurs: {reasons_str}")
                
                if analysis.statistics.failure_description:
                    # Description sur plusieurs lignes si nécessaire
                    desc_lines = analysis.statistics.failure_description.split('\n')
                    if len(desc_lines) == 1:
                        print(f"   └─ {analysis.statistics.failure_description}")
                    else:
                        print("   └─ Description:")
                        for line in desc_lines:
                            if line.strip():
                                print(f"      {line.strip()}")
            
            # Questions de l'appelant
            if analysis.statistics.user_questions:
                print(f"\n❓ Questions de l'appelant:")
                questions_lines = analysis.statistics.user_questions.split('\n')
                for q in questions_lines:
                    if q.strip():
                        print(f"   • {q.strip()}")
            
            # Tags de suivi (valeurs exactes avec underscores)
            if analysis.statistics.call_tags and len(analysis.statistics.call_tags) > 0:
                tags_str = ", ".join(analysis.statistics.call_tags)
                print(f"\n🏷️  Tags: {tags_str}")
        
        print("="*70)


def main():
    """Exemple d'utilisation."""
    print("🚀 Système d'analyse post-appel")
    print("-" * 60)
    
    # Initialise le système
    system = PostCallMonitoringSystem(model_name="gpt-4o")
    
    # Analyse d'un appel réel depuis Call Rounded
    call_id = "c4739276-0207-4bb4-b3e1-dabe55319c10"
    print(f"\n📞 Analyse de l'appel: {call_id}")
    result = system.analyze_call_from_id(call_id)
    if result:
        system.print_analysis(result)
    else:
        print("\n❌ L'analyse a échoué. Veuillez vérifier votre configuration et les logs ci-dessus.")


if __name__ == "__main__":
    main()

