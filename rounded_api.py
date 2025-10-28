"""Client API pour Call Rounded."""
import requests
import json
from typing import Optional, Dict, Any
from config import Config


class RoundedAPIClient:
    """Client pour l'API Call Rounded."""
    
    def __init__(self):
        self.api_key = Config.ROUNDED_API_KEY
        self.base_url = Config.ROUNDED_API_URL
    
    def get_call(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les détails d'un appel."""
        url = f"{self.base_url}/{call_id}"
        headers = {"X-Api-Key": self.api_key}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Erreur lors de la récupération de l'appel {call_id}: {e}")
            return None
    
    def list_calls(self, limit: int = 10) -> Optional[list]:
        """Liste les appels récents."""
        url = f"{self.base_url}"
        headers = {"X-Api-Key": self.api_key}
        params = {"limit": limit}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Erreur lors de la récupération de la liste d'appels: {e}")
            return None
    
    def transform_call_data(self, raw_call_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transforme les données brutes en format standard."""
        
        # L'API Call Rounded retourne {"data": {...}, "status": ...}
        # Si c'est ce format, on extrait "data"
        if "data" in raw_call_data:
            call_data = raw_call_data["data"]
        else:
            call_data = raw_call_data
        
        # Extraction du call_id (plusieurs formats possibles)
        call_id = call_data.get("id") or call_data.get("call_id") or call_data.get("callId")
        
        # Extraction du transcript
        transcript = call_data.get("transcript", [])
        
        # Extraction des tool calls et réponses depuis le transcript
        # Dans Call Rounded, les tools sont dans le transcript avec role="agent" + tool_calls et role="tool" + content
        tools = []
        tool_calls_indexed = {}  # Pour associer les réponses aux appels
        
        for item in transcript:
            if isinstance(item, dict):
                # Si c'est un agent avec tool_calls
                if item.get("role") == "agent" and "tool_calls" in item and item.get("tool_calls"):
                    for tool_call in item.get("tool_calls", []):
                        if "name" in tool_call and "tool_call_id" in tool_call:
                            tool_call_id = tool_call.get("tool_call_id")
                            tool_name = tool_call.get("name")
                            
                            # Parse les arguments
                            try:
                                arguments = json.loads(tool_call.get("arguments", "{}"))
                            except:
                                arguments = {}
                            
                            tool_calls_indexed[tool_call_id] = {
                                "name": tool_name,
                                "input": arguments,
                                "success": True,
                                "error": None,
                                "timestamp": item.get("start_time"),
                                "tool_call_id": tool_call_id
                            }
                            tools.append(tool_calls_indexed[tool_call_id])
                
                # Si c'est une réponse de tool
                elif item.get("role") == "tool" and "tool_calls" in item:
                    for tool_call_ref in item.get("tool_calls", []):
                        if "tool_call_id" in tool_call_ref:
                            tool_call_id = tool_call_ref.get("tool_call_id")
                            
                            # Parse la réponse
                            try:
                                tool_response = json.loads(item.get("content", "{}"))
                            except:
                                tool_response = {"raw_response": item.get("content")}
                            
                            # Associe la réponse au tool call correspondant
                            if tool_call_id in tool_calls_indexed:
                                tool_calls_indexed[tool_call_id]["output"] = tool_response
                                if "success" in tool_response:
                                    tool_calls_indexed[tool_call_id]["success"] = tool_response.get("success", True)
                                
                                # Extrait le message d'erreur depuis plusieurs champs possibles
                                if not tool_response.get("success", True):
                                    error_message = (
                                        tool_response.get("error") or 
                                        tool_response.get("instructions") or 
                                        tool_response.get("message") or
                                        "Erreur inconnue"
                                    )
                                    tool_calls_indexed[tool_call_id]["error"] = error_message
        
        # Extraction des métadonnées
        metadata = call_data.get("metadata", {})
        
        # Calcul de la durée
        duration = call_data.get("duration_seconds")
        
        # Statut
        status = call_data.get("status") or raw_call_data.get("status")
        
        return {
            "call_id": call_id,
            "metadata": metadata,
            "transcript": transcript,
            "tools": tools,
            "status": str(status) if status else None,
            "duration": duration
        }
    
    def get_call_details(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Récupère et affiche les détails bruts d'un appel pour debug."""
        data = self.get_call(call_id)
        if data:
            print("\n📦 DONNÉES BRUTES DE L'APPEL:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        return data

