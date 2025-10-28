"""Script de test pour l'analyse d'appels."""
from main import PostCallMonitoringSystem
import json


def test_with_call_id(call_id: str):
    """Teste l'analyse avec un call_id spécifique."""
    print(f"\n{'='*70}")
    print(f"🧪 TEST D'ANALYSE POUR L'APPEL: {call_id}")
    print(f"{'='*70}\n")
    
    try:
        # Initialise le système
        system = PostCallMonitoringSystem(model_name="gpt-4o-mini")
        
        # Analyse l'appel
        result = system.analyze_call_from_id(call_id)
        
        if result:
            # Affiche l'analyse
            system.print_analysis(result)
            
            # Sauvegarde dans un fichier JSON
            output_file = f"analysis_{call_id[:8]}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result.dict(), f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Analyse sauvegardée dans: {output_file}")
        else:
            print("❌ Impossible d'analyser cet appel")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Test avec le call_id fourni
    call_id = "fb96d81d-fef2-4f68-b438-07a9fe97e65e"
    test_with_call_id(call_id)
    
    # Vous pouvez tester avec d'autres call_ids:
    # test_with_call_id("autre-call-id")

