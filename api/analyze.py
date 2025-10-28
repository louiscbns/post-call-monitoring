"""API Vercel pour analyser un appel."""
import json
import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import des modules locaux
from main import PostCallMonitoringSystem

def handler(request):
    """Handler principal pour l'analyse."""
    try:
        # Parse le body de la requête
        body = json.loads(request.get('body', '{}')) if isinstance(request.get('body'), str) else request.get('body', {})
        
        call_id = body.get('call_id')
        model = body.get('model', 'gpt-4o-mini')
        
        if not call_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'call_id is required'
                })
            }
        
        # Analyser l'appel
        system = PostCallMonitoringSystem(model_name=model)
        result = system.analyze_call_from_id(call_id)
        
        if result:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
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
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Failed to analyze call. Please check the call_id and your configuration.'
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }

