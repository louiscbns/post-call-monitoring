"""Script pour analyser plusieurs appels en batch."""
from main import PostCallMonitoringSystem
import json
from typing import List
from datetime import datetime


def batch_analyze(call_ids: List[str], model_name: str = "gpt-4o-mini"):
    """Analyse plusieurs appels en batch."""
    system = PostCallMonitoringSystem(model_name=model_name)
    
    results = []
    
    print(f"\n{'='*70}")
    print(f"📊 ANALYSE EN BATCH - {len(call_ids)} APPELS")
    print(f"{'='*70}\n")
    
    for idx, call_id in enumerate(call_ids, 1):
        print(f"\n[{idx}/{len(call_ids)}] Analyse de l'appel: {call_id}")
        print("-" * 70)
        
        try:
            result = system.analyze_call_from_id(call_id)
            
            if result:
                results.append({
                    "call_id": call_id,
                    "analysis": result.dict(),
                    "timestamp": datetime.now().isoformat()
                })
                
                # Affiche un résumé rapide
                print(f"✅ Problème détecté: {result.problem_detected}")
                print(f"🏷️  Tags: {', '.join(result.tags)}")
                print(f"📝 Résumé: {result.summary[:100]}...")
            else:
                print(f"⚠️  Impossible d'analyser cet appel")
                results.append({
                    "call_id": call_id,
                    "error": "Unable to analyze",
                    "timestamp": datetime.now().isoformat()
                })
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            results.append({
                "call_id": call_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    # Sauvegarde des résultats
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"batch_analysis_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*70}")
    print(f"✅ Analyse terminée - {len(results)} résultats sauvegardés dans: {output_file}")
    print(f"{'='*70}")
    
    # Statistiques
    with_errors = sum(1 for r in results if r.get("analysis", {}).get("problem_detected"))
    without_errors = len(results) - with_errors
    
    print(f"\n📊 STATISTIQUES:")
    print(f"   ✅ Appels sans problème: {without_errors}")
    print(f"   ⚠️  Appels avec problème: {with_errors}")
    print(f"   📈 Taux de problèmes: {with_errors/len(results)*100:.1f}%")
    
    return results


if __name__ == "__main__":
    # Exemple: Liste d'appels à analyser
    call_ids = [
        "fb96d81d-fef2-4f68-b438-07a9fe97e65e",
        # Ajoutez d'autres call_ids ici
        # "autre-call-id-1",
        # "autre-call-id-2",
    ]
    
    # Analyse en batch
    batch_analyze(call_ids, model_name="gpt-4o-mini")

