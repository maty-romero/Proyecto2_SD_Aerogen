# telemetry_repository.py
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pymongo.errors import PyMongoError

from Shared.GenericMongoClient import GenericMongoClient
from Shared.MongoSingleton import MongoSingleton


class TelemetryDB:
    """
    Especie de Repository para operaciones de telemetría.
    - Por defecto usa MongoSingleton.get_singleton_client()
    - Pero podés inyectar otro GenericMongoClient (por ejemplo para tests).
    """
    def __init__(self, mongo_client: Optional[GenericMongoClient] = None, db_name: str = "test_db"):
        if mongo_client is None:
            self.mongo = MongoSingleton.get_singleton_client(db_name=db_name)
        else:
            self.mongo = mongo_client
        # self.mongo.db es el objeto Database de pymongo (asumimos que lo expone GenericMongoClient)
        self.db = self.mongo.db

    def insert_telemetry(self, payload: dict) -> object:
        """Inserta un documento de telemetría (usa GenericMongoClient.insert_one)."""
        collection: str = "telemetry"
        return self.mongo.insert_one(collection, payload)

    def get_window_stats(self,
                         turbine_id: Optional[str] = None,
                         farm_id: Optional[str] = None,
                         minutes: int = 5,
                         fields: List[str] = ("wind_speed_mps",),
                         collection: str = "telemetry") -> Dict[str, dict]:
        """
        Calcula avg/min/max/count/stdDev para los campos indicados en la ventana 'minutes'.
        Retorna un dict por campo con las métricas o valores None si no hay datos.
        """
        since = datetime.utcnow() - timedelta(minutes=minutes)

        match = {"timestamp": {"$gte": since}}
        if turbine_id:
            match["turbine_id"] = turbine_id
        if farm_id:
            match["farm_id"] = farm_id

        group_stage = {"_id": None, "count": {"$sum": 1}}
        for f in fields:
            group_stage[f"_avg_{f}"] = {"$avg": f"${f}"}
            group_stage[f"_min_{f}"] = {"$min": f"${f}"}
            group_stage[f"_max_{f}"] = {"$max": f"${f}"}
            group_stage[f"_std_{f}"] = {"$stdDevSamp": f"${f}"}

        pipeline = [
            {"$match": match},
            {"$group": group_stage}
        ]

        try:
            res = list(self.db[collection].aggregate(pipeline))
        except PyMongoError as e:
            # Propaga o maneja el error según tu política
            raise

        if not res:
            return {f: {"avg": None, "min": None, "max": None, "count": 0, "stdDev": None} for f in fields}

        doc = res[0]
        out = {}
        for f in fields:
            out[f] = {
                "avg": doc.get(f"_avg_{f}"),
                "min": doc.get(f"_min_{f}"),
                "max": doc.get(f"_max_{f}"),
                "count": doc.get("count", 0),
                "stdDev": doc.get(f"_std_{f}")
            }
        return out

    def get_window_stats_for_farm(self, farm_id: str, minutes: int = 5, fields: List[str] = ("wind_speed_mps",)):
        """
        Ejemplo: obtener stats para todas las turbinas de un farm en una sola consulta.
        Retorna un dict { turbine_id: {campo: metrics...}, ... }
        """
        since = datetime.utcnow() - timedelta(minutes=minutes)
        pipeline = [
            {"$match": {"farm_id": farm_id, "timestamp": {"$gte": since}}},
            {"$group": {
                "_id": "$turbine_id",
                **{f"_avg_{f}": {"$avg": f"${f}"} for f in fields},
                **{f"_min_{f}": {"$min": f"${f}"} for f in fields},
                **{f"_max_{f}": {"$max": f"${f}"} for f in fields},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]

        try:
            cursor = self.db["telemetry"].aggregate(pipeline)
            results = {}
            for doc in cursor:
                tid = doc["_id"]
                results[tid] = {}
                for f in fields:
                    results[tid][f] = {
                        "avg": doc.get(f"_avg_{f}"),
                        "min": doc.get(f"_min_{f}"),
                        "max": doc.get(f"_max_{f}"),
                        "count": doc.get("count", 0),
                    }
            return results
        except PyMongoError:
            raise
