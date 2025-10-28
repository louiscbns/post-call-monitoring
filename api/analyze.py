"""API Vercel - Analyser un appel."""
import json
import os
import sys

def handler(request):
    """Handler pour analyser un appel."""
    
    # Test simple d'abord
    try:
        # Parser le body
        body_data = {}
        if hasattr(request, 'body'):
            try:
                body_data = json.loads(request.body) if isinstance(request.body, str) else request.body
            except:
                pass
        elif hasattr(request, 'get_json'):
            body_data = request.get_json(silent=True) or {}
        
        call_id = body_data.get('call_id', '')
        model = body_data.get('model', 'gpt-4o-mini')
        
        # Si pas de call_id, retourner une erreur
        if not call_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'error': 'call_id is required'})
            }
        
        # Ajouter le parent au path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        # Importer et analyser
        from main import PostCallMonitoringSystem
        
        system = PostCallMonitoringSystem(model_name=model)
        result = system.analyze_call_from_id(call_id)
        
        if result:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': True,
                    'call_id': result.call_id,
                    'problem_detected': result.problem_detected,
                    'problem_type': result.problem_type,
                    'tags': result.tags,
                    'summary': result.summary,
                    'recommendations': result.recommendations
                })
            }
        else:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'error': 'Analysis failed'})
            }
            
    except Exception as e:
        import traceback
        error_detail = str(e)
        tb = traceback.format_exc()
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'success': False,
                'error': error_detail,
                'details': tb[:500]  # Limite les détails
            })
        }
