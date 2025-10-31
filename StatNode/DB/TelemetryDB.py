# telemetry_db.py
from datetime import datetime, timedelta
from math import pi
from typing import Optional, List, Dict, Any

from pymongo.errors import PyMongoError

from Shared.MongoSingleton import MongoSingleton
from Shared.GenericMongoClient import GenericMongoClient

DEFAULT_AIR_DENSITY = 1.225  # kg/m^3
TIMESTAMP_STR_FORMAT = "%Y-%m-%d %H:%M:%S"

class TelemetryDB:
    def __init__(self, mongo_client: Optional[GenericMongoClient] = None, db_name: str = "test_db"):
        if mongo_client is None:
            self.mongo = MongoSingleton.get_singleton_client(db_name=db_name)
        else:
            self.mongo = mongo_client
        
        print(f"Cliente mongo: {self.mongo}")

    def _ensure_numeric_fields(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convierte a tipos numéricos los campos esperados si vienen como strings.
        Calcula active_power_kw si no existe y hay voltage*current.
        """
        def to_float(val):
            try:
                return float(val)
            except (TypeError, ValueError):
                return None

        # campos numéricos previstos
        numeric_candidates = [
            "active_power_kw", "wind_speed_mps", "rotor_speed_rpm",
            "output_voltage_v", "generated_current_a"
        ]

        for key in numeric_candidates:
            if key in payload:
                payload[key] = to_float(payload[key])

        # si falta active_power_kw, intentar calcularlo como V * I / 1000 (kW)
        if payload.get("active_power_kw") is None:
            V = payload.get("output_voltage_v")
            I = payload.get("generated_current_a")
            if V is not None and I is not None:
                try:
                    payload["active_power_kw"] = float(V) * float(I) / 1000.0
                except Exception:
                    payload["active_power_kw"] = None

        return payload

    # -------------------------
    # Inserción con normalización (timestamp string -> datetime)
    # -------------------------

    def _ensure_timestamp(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        - Si payload['timestamp'] es string en formato YYYY-MM-DD HH:MM:SS:
            -> guarda payload['timestamp_str'] = el string (legible)
            -> convierte payload['timestamp'] = datetime (UTC, naive or aware)
        - Si ya es datetime lo deja.
        - Si no existe o falla el parseo, pone datetime.utcnow().
        """
        ts = payload.get("timestamp")

        # Si viene string, lo guardamos legible y convertimos a datetime
        if isinstance(ts, str):
            payload["timestamp_str"] = ts  # conservar legible
            try:
                # parsear como UTC (si tu generador usa local time, ajusta)
                dt = datetime.strptime(ts, TIMESTAMP_STR_FORMAT)
                # dejar como naive UTC (o hacerlo aware con timezone.utc si lo prefieres)
                payload["timestamp"] = dt  # datetime en UTC
            except Exception:
                payload["timestamp"] = datetime.utcnow()

        elif ts is None:
            payload["timestamp"] = datetime.utcnow()

        # si ya es datetime, podrías también setear timestamp_str si lo querés:
        elif isinstance(ts, datetime):
            try:
                payload["timestamp_str"] = ts.strftime(TIMESTAMP_STR_FORMAT)
            except Exception:
                payload["timestamp_str"] = ts.isoformat()

        return payload

    def insert_telemetry(self, payload: Dict[str, Any]) -> Any:
        """
        Inserta un documento en 'telemetry'.
        - Normaliza timestamp (string -> datetime)
        - Convierte campos numéricos a float si vienen como strings
        - Calcula active_power_kw si no existe (V * I / 1000)
        - Retorna inserted_id
        """
        collection_name = "telemetry"
        # normalizar timestamp (muy importante para queries por rango)
        payload = self._ensure_timestamp(payload)
        # normalizar numéricos y calcular active_power_kw si es posible
        payload = self._ensure_numeric_fields(payload)

        # Validación mínima: farm_id/turbine_id como enteros
        if "farm_id" in payload:
            try:
                payload["farm_id"] = int(payload["farm_id"])
            except Exception:
                # dejar como está pero avisar
                print("[TelemetryDB] Advertencia: farm_id no convertible a int:", payload.get("farm_id"))
        if "turbine_id" in payload:
            try:
                payload["turbine_id"] = int(payload["turbine_id"])
            except Exception:
                print("[TelemetryDB] Advertencia: turbine_id no convertible a int:", payload.get("turbine_id"))

        inserted_id = self.mongo.insert_one(collection_name, payload)
        
        print(f"[TelemetryDB] Insertado _id={inserted_id} - farm_id={payload.get('farm_id')} "
            f"turbine_id={payload.get('turbine_id')} active_power_kw={payload.get('active_power_kw')}")
        return inserted_id
        
    # -------------------------
    # Helpers Python (post-process)
    # -------------------------
    @staticmethod
    def _compute_energy_kwh(sum_power_kw: float, count: int, window_minutes: int) -> float:
        if not count:
            return 0.0
        delta_h = window_minutes / (count * 60.0)
        return float(sum_power_kw) * delta_h

    @staticmethod
    def _compute_availability(active_count: int, count: int) -> Optional[float]:
        if not count:
            return None
        return float(active_count) / float(count)

    @staticmethod
    def _compute_cp(p_avg_kw: Optional[float], v_avg: Optional[float], rotor_radius_m: Optional[float],
                    rho: float = DEFAULT_AIR_DENSITY) -> Optional[float]:
        if p_avg_kw is None or v_avg is None or rotor_radius_m is None:
            return None
        A = pi * (rotor_radius_m ** 2)
        p_w = p_avg_kw * 1000.0
        denom = 0.5 * rho * A * (v_avg ** 3)
        if denom <= 0:
            return None
        return float(p_w) / float(denom)

    # -------------------------
    # Método 1: métricas por turbina para todo el farm (UNA CONSULTA)
    # -------------------------
    def get_metrics_per_turbine(self, farm_id: int, minutes: int = 5,
                                rotor_radius_m: Optional[float] = None) -> Dict[str, Any]:
        
        # campos para la consulta 
        power_field: str = "active_power_kw"
        wind_field: str = "wind_speed_mps"
        state_field: str = "operational_state"
        
        """
        Una sola consulta que devuelve métricas por turbine_id (uno por documento).
        farm_id: entero
        rotor_radius_m: opcional, si lo pasas se calcula Cp por turbina usando ese radio (mismo radio para todas).
                        Si querés radios por turbina distintos, podemos añadir $lookup a turbine_config o pasar un map.
        Retorna dict con keys por turbine_id (enteros) y '_farm_total_kwh'.
        """
        since = datetime.utcnow() - timedelta(minutes=minutes)
        pipeline = [
            {"$match": {"farm_id": farm_id, "timestamp": {"$gte": since}}},
            {"$group": {
                "_id": "$turbine_id",
                "avg_wind": {"$avg": f"${wind_field}"},
                "avg_power_kw": {"$avg": f"${power_field}"},
                "sum_power_kw": {"$sum": f"${power_field}"},
                "count": {"$sum": 1},
                "active_count": {"$sum": {"$cond": [{"$eq": [f"${state_field}", "active"]}, 1, 0]}}
            }},
            {"$sort": {"_id": 1}}
        ]

        try:
            col = self.mongo.get_collection("telemetry")
            print(f"COLLECTION: {col}")
            cursor = col.aggregate(pipeline)
        except PyMongoError as e:
            raise

        out: Dict[int, Any] = {}
        farm_total_kwh = 0.0
        print(f"CURSOR: {cursor}")
        for doc in cursor:
            tid = doc["_id"]  # asumo entero
            avg_wind = doc.get("avg_wind")
            avg_power = doc.get("avg_power_kw")
            sum_power = doc.get("sum_power_kw") or 0.0
            count = int(doc.get("count", 0))
            active_count = int(doc.get("active_count", 0))

            energy = self._compute_energy_kwh(sum_power, count, minutes)
            availability = self._compute_availability(active_count, count)
            cp = self._compute_cp(avg_power, avg_wind, rotor_radius_m)

            out[tid] = {
                "avg_wind": avg_wind,
                "avg_power_kw": avg_power,
                "sum_power_kw": sum_power,
                "count": count,
                "active_count": active_count,
                "energy_kwh": energy,
                "availability": availability,
                "cp": cp
            }
            farm_total_kwh += energy

        out["_farm_total_kwh"] = farm_total_kwh
        return out

    # -------------------------
    # Método 2: métricas agregadas del farm (UNA CONSULTA)
    # -------------------------
    def get_metrics_aggregate(self, farm_id: int, minutes: int = 5, 
                              rotor_radius_m: Optional[float] = None) -> Dict[str, Any]:
        # campos para la consulta 
        power_field: str = "active_power_kw"
        wind_field: str = "wind_speed_mps"
        state_field: str = "operational_state"
        
        """
        Devuelve métricas agregadas del farm como un único documento.
        farm_id: entero
        rotor_radius_m: opcional para calcular cp del farm (usa avg_power y avg_wind).
        """
        since = datetime.utcnow() - timedelta(minutes=minutes)
        pipeline = [
            {"$match": {"farm_id": farm_id, "timestamp": {"$gte": since}}},
            {"$group": {
                "_id": None,
                "avg_wind": {"$avg": f"${wind_field}"},
                "avg_power_kw": {"$avg": f"${power_field}"},
                "sum_power_kw": {"$sum": f"${power_field}"},
                "count": {"$sum": 1},
                "active_count": {"$sum": {"$cond": [{"$eq": [f"${state_field}", "active"]}, 1, 0]}}
            }}
        ]

        try:
            col = self.mongo.get_collection("telemetry")
            res = list(col.aggregate(pipeline))
        except PyMongoError as e:
            raise

        if not res:
            return {
                "avg_wind": None,
                "avg_power_kw": None,
                "sum_power_kw": 0.0,
                "count": 0,
                "active_count": 0,
                "energy_kwh": 0.0,
                "availability": None,
                "cp": None
            }

        doc = res[0]
        avg_wind = doc.get("avg_wind")
        avg_power = doc.get("avg_power_kw")
        sum_power = doc.get("sum_power_kw") or 0.0
        count = int(doc.get("count", 0))
        active_count = int(doc.get("active_count", 0))

        energy = self._compute_energy_kwh(sum_power, count, minutes)
        availability = self._compute_availability(active_count, count)
        cp = self._compute_cp(avg_power, avg_wind, rotor_radius_m)

        return {
            "avg_wind": avg_wind,
            "avg_power_kw": avg_power,
            "sum_power_kw": sum_power,
            "count": count,
            "active_count": active_count,
            "energy_kwh": energy,
            "availability": availability,
            "cp": cp
        }
