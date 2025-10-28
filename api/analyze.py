"""API Vercel - Analyser un appel."""
import json
import os
import sys

# Ajouter parent au path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

def handler(request):
    """Handler Vercel Python."""
    try:
        # Get request body
        if hasattr(request, 'body'):
            body = json.loads(request.body) if isinstance(request.body, str) else request.body
        else:
            body = {}
        
        call_id = body.get('call_id', '')
        model = body.get('model', 'gpt-4o-mini')
        
        if not call_id:
            return json.dumps({
                'success': False,
                'error': 'call_id is required'
            }), 400, {'Content-Type': 'application/json'}
        
        # Import and analyze
        from main import PostCallMonitoringSystem
        system = PostCallMonitoringSystem(model_name=model)
        result = system.analyze_call_from_id(call_id)
        
        if result:
            return json.dumps({
                'success': True,
                'call_id': result.call_id,
                'problem_detected': result.problem_detected,
                'problem_type': result.problem_type,
                'tags': result.tags,
                'summary': result.summary,
                'recommendations': result.recommendations
            }), 200, {'Content-Type': 'application/json'}
        else:
            return json.dumps({
                'success': False,
                'error': 'Failed to analyze call'
            }), 400, {'Content-Type': 'application/json'}
            
    except Exception as e:
        return json.dumps({
            'success': False,
            'error': str(e)
        }), 500, {'Content-Type': 'application/json'}
