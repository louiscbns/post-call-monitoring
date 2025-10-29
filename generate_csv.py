"""Script pour générer un CSV avec les analyses de tous les appels et modèles."""
import csv
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from main import PostCallMonitoringSystem
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Liste des call_ids à analyser
CALL_IDS = [
    "fb96d81d-fef2-4f68-b438-07a9fe97e65e",
    "c4739276-0207-4bb4-b3e1-dabe55319c10",
    "7adeb607-390e-44c2-a974-47c848f35dfe",
    "37ea75da-8101-4005-99f9-96d793f1ca27",
    "9cfca680-334b-42c4-ae51-6f45f94fe436",
    "76dec7d1-7c2c-46e5-a73c-5820dd74e0b9",
    "fa789f5d-8665-46ca-ab36-e26b360642a1",
    "16510542-f4fa-46ae-b16a-6ba15f5a45da",
    "4289531f-7cb6-4c33-b827-bcc33e4ad871",
    "8cd5d571-0507-45db-9481-6200a89d379f"
]

# Liste des modèles à tester
MODELS = [
    "gemini-2.0-flash",
    "gpt-4.1",
    "gpt-4.1-mini"
]

# Verrou pour l'affichage thread-safe
print_lock = Lock()


def format_list_field(value):
    """Formate une liste pour le CSV (sépare par des points-virgules)."""
    if value is None:
        return ""
    if isinstance(value, list):
        return "; ".join(str(v) for v in value)
    return str(value)


def analyze_and_extract(call_id: str, model: str, task_num: int = None, total_tasks: int = None):
    """Analyse un appel avec un modèle et extrait les données."""
    task_info = f"[{task_num}/{total_tasks}] " if task_num and total_tasks else ""
    
    with print_lock:
        print(f"\n{task_info}{'='*70}")
        print(f"{task_info}Analyse: Call ID = {call_id}, Modèle = {model}")
        print(f"{task_info}{'='*70}")
    
    try:
        # Initialise le système avec le modèle
        system = PostCallMonitoringSystem(model_name=model)
        
        # Analyse l'appel
        result = system.analyze_call_from_id(call_id)
        
        if not result:
            with print_lock:
                print(f"{task_info}❌ Échec de l'analyse pour {call_id} avec {model}")
            return {
                "call_id": call_id,
                "model_used": model,
                "call_reason": "ERROR",
                "user_sentiment": "ERROR",
                "failure_reasons": "ERROR",
                "failure_description": "Erreur lors de l'analyse",
                "user_questions": "ERROR",
                "call_tags": "ERROR"
            }
        
        # Extrait les statistiques
        stats = result.statistics
        
        # Prépare les données pour le CSV
        data = {
            "call_id": call_id,
            "model_used": model,
            "call_reason": stats.call_reason if stats.call_reason else "",
            "user_sentiment": stats.user_sentiment if stats.user_sentiment else "",
            "failure_reasons": format_list_field(stats.failure_reasons),
            "failure_description": stats.failure_description if stats.failure_description else "",
            "user_questions": stats.user_questions if stats.user_questions else "",
            "call_tags": format_list_field(stats.call_tags)
        }
        
        with print_lock:
            print(f"{task_info}✅ Analyse réussie: {call_id} avec {model}")
        return data
        
    except Exception as e:
        with print_lock:
            print(f"{task_info}❌ Erreur pour {call_id} avec {model}: {e}")
        return {
            "call_id": call_id,
            "model_used": model,
            "call_reason": "ERROR",
            "user_sentiment": "ERROR",
            "failure_reasons": "ERROR",
            "failure_description": f"Exception: {str(e)}",
            "user_questions": "ERROR",
            "call_tags": "ERROR"
        }


def generate_csv(max_workers: int = None):
    """Génère le fichier CSV avec toutes les analyses en parallèle."""
    print("🚀 Génération du CSV d'analyse (mode parallèle)")
    print(f"📞 Call IDs: {len(CALL_IDS)}")
    print(f"🤖 Modèles: {len(MODELS)}")
    total_tasks = len(CALL_IDS) * len(MODELS)
    print(f"📊 Total d'analyses: {total_tasks}")
    
    # Détermine le nombre de workers (par défaut: nombre de modèles × nombre de call_ids, max 20)
    if max_workers is None:
        max_workers = min(total_tasks, 20)
    print(f"🔄 Workers parallèles: {max_workers}\n")
    
    # Crée le nom du fichier avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analysis_results_{timestamp}.csv"
    
    # Colonnes du CSV
    fieldnames = [
        "call_id",
        "model_used",
        "call_reason",
        "user_sentiment",
        "failure_reasons",
        "failure_description",
        "user_questions",
        "call_tags"
    ]
    
    # Crée toutes les combinaisons call_id × model (avec déduplication)
    tasks_dict = {}  # Utilise un dict pour dédupliquer automatiquement
    task_num = 0
    
    # Dédupliquer les call_ids et modèles
    unique_call_ids = list(dict.fromkeys(CALL_IDS))  # Préserve l'ordre
    unique_models = list(dict.fromkeys(MODELS))  # Préserve l'ordre
    
    for call_id in unique_call_ids:
        for model in unique_models:
            task_key = (call_id, model)
            if task_key not in tasks_dict:
                task_num += 1
                tasks_dict[task_key] = (call_id, model, task_num)
    
    tasks = list(tasks_dict.values())
    actual_total = len(tasks)
    
    # Ajuster le total si différent à cause de la déduplication
    if actual_total != total_tasks:
        print(f"⚠️  Déduplication détectée: {total_tasks} combinaisons → {actual_total} uniques")
        total_tasks = actual_total
    
    # Afficher les combinaisons qui seront traitées
    print(f"\n📋 Combinaisons à traiter ({actual_total}):")
    for call_id, model, num in tasks:
        print(f"   {num}. {call_id[:8]}... × {model}")
    print()
    
    # Traitement en parallèle
    results = []
    seen_keys = set()  # Pour détecter les doublons dans les résultats
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Soumet toutes les tâches (garanties uniques)
        future_to_task = {
            executor.submit(analyze_and_extract, call_id, model, task_num, total_tasks): (call_id, model)
            for call_id, model, task_num in tasks
        }
        
        # Traite les résultats au fur et à mesure
        completed = 0
        for future in as_completed(future_to_task):
            completed += 1
            call_id, model = future_to_task[future]
            try:
                data = future.result()
                
                # Vérifier les doublons
                result_key = (data["call_id"], data["model_used"])
                if result_key in seen_keys:
                    with print_lock:
                        print(f"⚠️  [{completed}/{total_tasks}] DOUBLON DÉTECTÉ: {call_id} - {model} (ignoré)")
                else:
                    seen_keys.add(result_key)
                    results.append(data)
                    with print_lock:
                        print(f"📝 [{completed}/{total_tasks}] Résultat reçu: {call_id} - {model}")
            except Exception as e:
                with print_lock:
                    print(f"❌ [{completed}/{total_tasks}] Exception pour {call_id} - {model}: {e}")
                results.append({
                    "call_id": call_id,
                    "model_used": model,
                    "call_reason": "ERROR",
                    "user_sentiment": "ERROR",
                    "failure_reasons": "ERROR",
                    "failure_description": f"Exception: {str(e)}",
                    "user_questions": "ERROR",
                    "call_tags": "ERROR"
                })
    
    # Écrit tous les résultats dans le CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')
        writer.writeheader()
        
        # Trie les résultats par call_id puis par model pour un ordre cohérent
        results_sorted = sorted(results, key=lambda x: (x["call_id"], x["model_used"]))
        
        # Vérification finale des doublons avant écriture
        final_seen = set()
        unique_results = []
        duplicates_count = 0
        
        for data in results_sorted:
            result_key = (data["call_id"], data["model_used"])
            if result_key not in final_seen:
                final_seen.add(result_key)
                unique_results.append(data)
            else:
                duplicates_count += 1
                print(f"⚠️  Doublon final détecté et ignoré: {data['call_id']} - {data['model_used']}")
        
        for data in unique_results:
            writer.writerow(data)
        
    print(f"\n{'='*70}")
    print(f"✅ CSV généré avec succès: {filename}")
    print(f"📊 {len(unique_results)} résultats uniques écrits")
    if duplicates_count > 0:
        print(f"⚠️  {duplicates_count} doublons détectés et ignorés")
    print(f"{'='*70}")
    return filename


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Génère un CSV avec les analyses de tous les appels et modèles")
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Nombre de workers parallèles (défaut: min(total_tasks, 20))"
    )
    
    args = parser.parse_args()
    
    try:
        filename = generate_csv(max_workers=args.workers)
        print(f"\n📁 Fichier créé: {filename}")
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interruption par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

