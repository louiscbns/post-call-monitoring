"""Health check."""
import json

def handler(request):
    """Health check endpoint."""
    return json.dumps({
        'status': 'ok',
        'message': 'API running'
    }), 200, {'Content-Type': 'application/json'}
