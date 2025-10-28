"""Health check endpoint."""
import json

def handler(request):
    """Health check handler."""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'status': 'ok',
            'message': 'API is running'
        })
    }
