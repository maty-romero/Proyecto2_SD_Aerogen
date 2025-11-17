"""
Instancia compartida de TelemetryDB para uso en los endpoints de la API.
Se inicializa al arrancar el servidor Flask.
"""
import os
from typing import Optional, List
from StatNode.DB.TelemetryDB import TelemetryDB

# Instancia global de clientes de base de datos
db_clients: Optional[List[TelemetryDB]] = None

def init_db_clients():
    """
    Inicializa los clientes de base de datos a partir de MONGO_URIS.
    Debe ser llamado al iniciar el servidor Flask.
    """
    global db_clients
    
    uris_str = os.environ.get("MONGO_URIS")
    if not uris_str:
        print("[DB] Warning: MONGO_URIS no está configurado")
        db_clients = []
        return
    
    uris = [uri.strip() for uri in uris_str.split(',')]
    db_clients = []
    
    for uri in uris:
        try:
            db_client = TelemetryDB(uri=uri, db_name="windfarm_db")
            db_client.connect()
            db_clients.append(db_client)
            print(f"[DB] Cliente de base de datos conectado: {uri}")
        except Exception as e:
            print(f"[DB] Error al conectar con {uri}: {e}")
    
    if not db_clients:
        print("[DB] Warning: No se pudo conectar a ninguna base de datos")

def get_db_client() -> Optional[TelemetryDB]:
    """
    Obtiene el primer cliente de base de datos disponible.
    
    Returns:
        TelemetryDB o None si no hay clientes disponibles
    """
    if db_clients and len(db_clients) > 0:
        return db_clients[0]
    return None
