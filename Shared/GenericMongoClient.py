from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, PyMongoError, ServerSelectionTimeoutError
import time
import os


class GenericMongoClient:
    """
    Clase genérica para conectarse a MongoDB usando pymongo.
    Permite operaciones básicas de inserción, consulta y actualización.
    """
    #def __init__(self, uri: str = "mongodb://localhost:27017", db_name: str = "test_db"):
    def __init__(self, uri: str = os.environ.get("MONGO_URI", "mongodb://localhost:27017"), db_name: str = "test_db"):
        self.uri = uri
        self.db_name = db_name
        self.client: MongoClient = None
        self.db = None

    def connect(self, max_retries: int = 5, retry_delay_s: int = 3):
        """Conecta al servidor MongoDB con reintentos y selecciona la base de datos."""
        retries = 0
        while retries < max_retries:
            try:
                print(f"[MongoDB] Connecting to {self.uri}... (Attempt {retries + 1})")
                # Usar serverSelectionTimeoutMS para que el ping no bloquee por mucho tiempo
                self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
                # Test de conexión rápida
                self.client.admin.command("ping")
                self.db = self.client[self.db_name]
                print(f"[MongoDB] Connected to {self.db_name} at {self.uri}")
                return # Conexión exitosa
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                print(f"[MongoDB] Connection failed: {e}. Retrying in {retry_delay_s}s...")
                retries += 1
                time.sleep(retry_delay_s)
        
        print(f"[MongoDB] Could not connect to database after {max_retries} attempts.")
        raise ConnectionFailure(f"Failed to connect to MongoDB at {self.uri}")

    def get_collection(self, collection_name: str) -> Collection:
        """Obtiene una colección específica de la base de datos."""
        if self.db is None:
            raise RuntimeError("No conectado a la base de datos")
        return self.db[collection_name]

    def insert_one(self, collection_name: str, document: dict):
        """Inserta un documento en la colección."""
        try:
            collection = self.get_collection(collection_name)
            result = collection.insert_one(document)
            return result.inserted_id
        except PyMongoError as e:
            print(f"[MongoDB] Error al insertar: {e}")
            raise

    def find(self, collection_name: str, query: dict = None, limit: int = 0):
        """Consulta documentos según un filtro opcional."""
        query = query or {}
        try:
            collection = self.get_collection(collection_name)
            cursor = collection.find(query).limit(limit)
            return list(cursor)
        except PyMongoError as e:
            print(f"[MongoDB] Error al consultar: {e}")
            raise

    def update_one(self, collection_name: str, filter_query: dict, update_values: dict):
        """Actualiza un documento que cumpla el filtro."""
        try:
            collection = self.get_collection(collection_name)
            result = collection.update_one(filter_query, {"$set": update_values})
            return result.modified_count
        except PyMongoError as e:
            print(f"[MongoDB] Error al actualizar: {e}")
            raise

    def close(self):
        """Cierra la conexión con MongoDB."""
        if self.client:
            self.client.close()
            print("[MongoDB] Conexión cerrada")

"""
Ejemplo de uso:


if __name__ == "__main__":
    mongo_client = GenericMongoClient(db_name="my_test_db")
    mongo_client.connect()

    # Insertar
    doc_id = mongo_client.insert_one("turbine_data", {"turbine_id": "T-001", "rpm": 1500})
    print(f"Documento insertado con id: {doc_id}")

    # Consultar
    docs = mongo_client.find("turbine_data", {"turbine_id": "T-001"})
    print("Documentos encontrados:", docs)
    
    # Consulta por fecha
    start_date = datetime(2025, 10, 20) # Fechas ejemplo
    end_date   = datetime(2025, 10, 25)

    # Consulta por rango de fecha
    query = {
        "timestamp": {"$gte": start_date, "$lte": end_date}
    }

    docs = mongo_client.find("turbine_data", query)

    # Actualizar
    updated = mongo_client.update_one("turbine_data", {"turbine_id": "T-001"}, {"rpm": 1550})
    print(f"Documentos modificados: {updated}")

    # Cerrar
    mongo_client.close()

"""