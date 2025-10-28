"""API Vercel - Analyser un appel."""
import json
import sys
import os
import traceback

# Ajouter parent au path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import au niveau module (plus fiable)
try:
    from main import PostCallMonitoringSystem
except ImportError as e:
    print(f"Import error: {e}")
    PostCallMonitoringSystem = None

def handler(request):
    """Handler Vercel Python - Format: retourne un dict."""
    try:
        print("=== API Analyze Called ===")
        
        # Parse body
        try:
            if hasattr(request, 'body'):
                if isinstance(request.body, str):
                    body = json.loads(request.body)
                else:
                    body = request.body
            elif hasattr(request, 'json'):
                body = request.json
            else:
                body = {}
            print(f"Body: {body}")
        except Exception as e:
            print(f"Parse error: {e}")
            body = {}
        
        call_id = body.get('call_id') or body.get('callId', '')
        model = body.get('model', 'gpt-4o-mini')
        
        print(f"Call ID: {call_id}, Model: {model}")
        
        if not call_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'call_id is required'
                })
            }
        
        if PostCallMonitoringSystem is None:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'PostCallMonitoringSystem not loaded'
                })
            }
        
        # Analyser
        print("Starting analysis...")
        system = PostCallMonitoringSystem(model_name=model)
        print("System created")
        result = system.analyze_call_from_id(call_id)
        print(f"Result: {result}")
        
        if result:
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
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
                    'error': 'Failed to analyze call'
                })
            }
            
    except Exception as e:
        print(f"Exception: {e}")
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            })
        }
