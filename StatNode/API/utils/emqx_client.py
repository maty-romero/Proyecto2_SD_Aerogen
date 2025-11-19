"""
Cliente HTTP para consultar la API REST de EMQX Broker.
Documentación: https://www.emqx.io/docs/en/v5.0/admin/api.html
"""
import os
import sys
import requests
from typing import List, Dict, Optional
from requests.auth import HTTPBasicAuth

# Importar TokenProvider
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from Shared.TokenProvider import TokenProvider


class EMQXClient:
    """Cliente para interactuar con la API REST de EMQX."""
    
    def __init__(self, token_provider: Optional[TokenProvider] = None):
        self.base_url = os.getenv('EMQX_API_URL', 'http://emqx:18083')
        self.api_user = os.getenv('EMQX_API_USER', 'admin')
        self.timeout = 5  # segundos
    
    def _get_auth(self):
        """Autenticación básica usando credenciales estáticas."""
        api_password = os.getenv('EMQX_API_PASSWORD', 'public')
        return HTTPBasicAuth(self.api_user, api_password)
    
    def get_clients(self) -> Optional[List[Dict]]:
        """
        Obtiene todos los clientes conectados al broker EMQX.
        
        Returns:
            Lista de clientes conectados o None si hay error.
        """
        try:
            url = f"{self.base_url}/api/v5/clients"
            response = requests.get(url, auth=self._get_auth(), timeout=self.timeout)
            
            print(f"[EMQX_DEBUG] Status Code: {response.status_code}")
            if response.status_code != 200:
                print(f"[EMQX_DEBUG] Error respuesta: {response.text}")
                return None
            
            response.raise_for_status()

            data = response.json()

            return data.get('data', [])
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener clientes de EMQX: {e}")
            return None
    
    def get_client_by_farm_and_id(self, farm_id: str, turbine_id: str) -> Optional[Dict]:
        try:
            client_id = f"WF-{farm_id}-T{turbine_id}"

            url = f"{self.base_url}/api/v5/clients/{client_id}"
            response = requests.get(url, auth=self._get_auth(), timeout=self.timeout)

            if response.status_code == 404:
                return None

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Error al obtener cliente {client_id}: {e}")
            return None

    
    def get_clients_by_farm(self, farm_id: str) -> List[Dict]:
        """
        Obtiene todos los clientes conectados de un parque específico.
        
        Args:
            farm_id: ID del parque eólico (ej: 'farm_01')
            
        Returns:
            Lista de clientes del parque.
        """
        all_clients = self.get_clients()
        
        if not all_clients:
            return []
        
        farm_clients = [
            client for client in all_clients
            if client.get('clientid', '').startswith(f'WF-{farm_id}-T')
        ]
        
        return farm_clients
    
    def format_turbine_info(self, client: Dict) -> Dict:
        """
        Formatea la información del cliente EMQX a formato de turbina.
        
        Args:
            client: Diccionario con datos del cliente EMQX
            
        Returns:
            Diccionario con información formateada de la turbina.
        """
        return {
            'turbine_id': client.get('clientid', 'unknown'),
            'connected': client.get('connected', False),
            'ip_address': client.get('ip_address', 'unknown'),
            'connected_at': client.get('connected_at', None),
            'keepalive': client.get('keepalive', 0),
            'proto_ver': client.get('proto_ver', 'MQTT 3.1.1'),
            'recv_msg': client.get('recv_msg', 0),
            'send_msg': client.get('send_msg', 0),
            'subscriptions_cnt': client.get('subscriptions_cnt', 0)
        }


# Instancia global del cliente EMQX
emqx_client = EMQXClient()
