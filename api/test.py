"""Test endpoint pour vérifier que Vercel fonctionne."""
import json

def handler(request):
    """Test simple."""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'message': 'Test OK', 'python': 'working'})
    }

