# telemetry_db.py
from datetime import datetime, timedelta, timezone
from math import pi
from typing import Optional, List, Dict, Any

from pymongo.errors import PyMongoError

from Shared.GenericMongoClient import GenericMongoClient

DEFAULT_AIR_DENSITY = 1.225  # kg/m^3
TIMESTAMP_STR_FORMAT = "%Y-%m-%d %H:%M:%S"

class TelemetryDB:
    def __init__(self, db_name: str = "windfarm_db"):
        # Creamos una instancia de GenericMongoClient que leerá la variable de entorno MONGO_URI
        # y se conectará a la base de datos correcta dentro de la red de Docker.
        self.mongo = GenericMongoClient(db_name=db_name)
        # La conexión se establece explícitamente.
        self.mongo.connect()

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


    # Insercion con normalizacion (timestamp string -> datetime)

    def _ensure_timestamp(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        - Interpreta incoming timestamp string como hora LOCAL del productor,
        lo convierte a UTC (timezone-aware) y lo guarda en payload['timestamp'].
        - Conserva payload['timestamp_str'] con la forma legible original.
        - Si no puede parsear, usa ahora en UTC.
        """
        ts = payload.get("timestamp")

        # Detectar zona local (del host donde corre este código)
        local_tz = datetime.now().astimezone().tzinfo

        # Si viene string, lo parseamos como hora local y lo convertimos a UTC
        if isinstance(ts, str):
            payload["timestamp_str"] = ts
            try:
                dt_local_naive = datetime.strptime(ts, TIMESTAMP_STR_FORMAT)
                # hacemos aware asumiendo zona local
                dt_local = dt_local_naive.replace(tzinfo=local_tz)
                dt_utc = dt_local.astimezone(timezone.utc)
                payload["timestamp"] = dt_utc
            except Exception:
                payload["timestamp"] = datetime.now(timezone.utc)

        elif ts is None:
            payload["timestamp"] = datetime.now(timezone.utc)
            payload["timestamp_str"] = payload["timestamp"].astimezone(local_tz).strftime(TIMESTAMP_STR_FORMAT)

        # Si ya es datetime (puede ser naive o aware)
        elif isinstance(ts, datetime):
            if ts.tzinfo is None:
                # asumimos que es hora local si viene naive
                ts_local = ts.replace(tzinfo=local_tz)
                payload["timestamp"] = ts_local.astimezone(timezone.utc)
                payload["timestamp_str"] = ts_local.strftime(TIMESTAMP_STR_FORMAT)
            else:
                # ya es aware: convertimos a UTC
                payload["timestamp"] = ts.astimezone(timezone.utc)
                payload["timestamp_str"] = payload["timestamp"].astimezone(local_tz).strftime(TIMESTAMP_STR_FORMAT)

        return payload

    def insert_telemetry(self, payload: Dict[str, Any]):
        collection_name = "telemetry"

        # normalizar timestamp y campos numericos
        payload = self._ensure_timestamp(payload)
        payload = self._ensure_numeric_fields(payload)

        # forzar farm/turbine a int si es posible
        if "farm_id" in payload:
            try:
                payload["farm_id"] = int(payload["farm_id"])
            except Exception:
                pass
        if "turbine_id" in payload:
            try:
                payload["turbine_id"] = int(payload["turbine_id"])
            except Exception:
                pass

        inserted_id = self.mongo.insert_one(collection_name, payload)
        print(f"--- [TelemetryDB] Insertado _id={inserted_id} - farm_id={payload.get('farm_id')} "
            f"turbine_id={payload.get('turbine_id')} ---\n")

        
    
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

    def get_metrics_per_turbine(self, farm_id: int, minutes: int = 5,
                                 rotor_radius_m: Optional[float] = None) -> Dict[int, dict]:
        """
        Métricas por turbina:
        - avg_wind_speed_mps
        - avg_active_power_kw
        - energy_kwh
        - capacity_factor_pct (si capacity_mw existe)
        - availability_pct (samples operational / total samples) * 100
        - avg_power_coefficient_cp (Cp calculado con avg_power & avg_wind)
        """
        since = datetime.now(timezone.utc) - timedelta(minutes=minutes)

        # Pipeline: match por farm y ventana; ordenar por timestamp para usar $last; agrupar por turbine
        pipeline = [
            {"$match": {"farm_id": farm_id, "timestamp": {"$gte": since}}},
            {"$sort": {"timestamp": 1}},  # necesario para $last funcione como "último" en la ventana
            {"$group": {
                "_id": "$turbine_id",
                "avg_wind": {"$avg": "$wind_speed_mps"},
                "avg_power_kw": {"$avg": "$active_power_kw"},
                "sum_power_kw": {"$sum": "$active_power_kw"},
                "sample_count": {"$sum": 1},
                "active_samples": {"$sum": {"$cond": [{"$eq": ["$operational_state", "operational"]}, 1, 0]}},
                "last_state": {"$last": "$operational_state"},
                "avg_capacity_mw": {"$avg": "$capacity_mw"}  # si existe
            }},
            {"$sort": {"_id": 1}}
        ]

        try:
            col = self.mongo.get_collection("telemetry")
            cursor = list(col.aggregate(pipeline))
        except PyMongoError:
            raise

        out: Dict[int, dict] = {}
        for doc in cursor:
            tid = doc["_id"]
            avg_wind = doc.get("avg_wind")
            avg_power = doc.get("avg_power_kw")
            sum_power = doc.get("sum_power_kw") or 0.0
            sample_count = int(doc.get("sample_count", 0))
            active_samples = int(doc.get("active_samples", 0))
            avg_capacity_mw = doc.get("avg_capacity_mw")  # puede ser None

            # energy_kwh: usar helper (usa sum_power en kW y sample_count para estimar intervalo)
            energy_kwh = self._compute_energy_kwh(sum_power_kw=sum_power, count=sample_count, window_minutes=minutes)

            # capacity factor: energy / (capacity_kw * window_hours) * 100
            if avg_capacity_mw:
                capacity_kw = float(avg_capacity_mw) * 1000.0
                window_hours = minutes / 60.0
                denom = capacity_kw * window_hours
                capacity_factor_pct = None
                if denom > 0:
                    capacity_factor_pct = round((energy_kwh / denom) * 100.0, 3)
            else:
                capacity_factor_pct = None

            availability_pct = None
            if sample_count > 0:
                availability_pct = round((active_samples / sample_count) * 100.0, 2)

            cp_avg = self._compute_cp(p_avg_kw=avg_power, v_avg=avg_wind, rotor_radius_m=rotor_radius_m)

            out[tid] = {
                "avg_wind_speed_mps": None if avg_wind is None else round(avg_wind, 3),
                "avg_active_power_kw": None if avg_power is None else round(avg_power, 3),
                "energy_kwh": round(energy_kwh, 4),
                "capacity_factor_pct": capacity_factor_pct,
                "availability_pct": availability_pct,
                "avg_power_coefficient_cp": None if cp_avg is None else round(cp_avg, 4),
            }

        return out


    def get_metrics_farm(self, farm_id: int, minutes: int = 5,
                                rotor_radius_m: Optional[float] = None) -> Dict[str, Any]:
        """
        Devuelve métricas agregadas del farm (UNA CONSULTA):
        - avg_wind_speed_mps (farm avg)
        - total_energy_kwh (suma de energies por turbina)
        - avg_power_kw (farm average power)
        - farm_capacity_factor_pct (total energy / total_capacity *100) (si capacity_mw existe)
        - farm_availability_pct (percent of turbines whose last_state == 'operational')
        - farm_cp_weighted (Cp promedio ponderado por energy)
        """
        since = datetime.now(timezone.utc) - timedelta(minutes=minutes)

        # Pipeline en dos etapas: primero agrupar por turbine para obtener sum/count/last_state/avg capacity,
        # luego agrupar todo para farm-level aggregations.
        pipeline = [
            {"$match": {"farm_id": farm_id, "timestamp": {"$gte": since}}},
            {"$sort": {"timestamp": 1}},
            {"$group": {
                "_id": "$turbine_id",
                "avg_wind": {"$avg": "$wind_speed_mps"},
                "avg_power_kw": {"$avg": "$active_power_kw"},
                "sum_power_kw": {"$sum": "$active_power_kw"},
                "sample_count": {"$sum": 1},
                "active_samples": {"$sum": {"$cond": [{"$eq": ["$operational_state", "operational"]}, 1, 0]}},
                "last_state": {"$last": "$operational_state"},
                "avg_capacity_mw": {"$avg": "$capacity_mw"}
            }},
            # Segundo group: sumar/contar a nivel farm
            {"$group": {
                "_id": None,
                "avg_wind_farm": {"$avg": "$avg_wind"},
                "avg_power_kw_farm": {"$avg": "$avg_power_kw"},
                "sum_power_kw_farm": {"$sum": "$sum_power_kw"},
                "total_samples": {"$sum": "$sample_count"},
                "total_active_samples": {"$sum": "$active_samples"},
                "turbine_count": {"$sum": 1},
                "turbines_operational_now": {"$sum": {"$cond": [{"$eq": ["$last_state", "operational"]}, 1, 0]}},
                "total_capacity_mw": {"$sum": {"$ifNull": ["$avg_capacity_mw", 0]}},
                # Also pass arrays of (avg_cp_estimate * energy) if needed later — but we cannot compute Cp here easily
            }}
        ]

        try:
            col = self.mongo.get_collection("telemetry")
            res = list(col.aggregate(pipeline))
        except PyMongoError:
            raise

        if not res:
            return {
                "avg_wind_speed_mps": None,
                "total_energy_kwh": 0.0,
                "avg_power_kw": None,
                "farm_capacity_factor_pct": None,
                "farm_availability_pct": None,
                "farm_cp_weighted": None
            }

        doc = res[0]
        avg_wind_farm = doc.get("avg_wind_farm")
        avg_power_kw_farm = doc.get("avg_power_kw_farm")
        sum_power_kw_farm = doc.get("sum_power_kw_farm") or 0.0
        total_samples = int(doc.get("total_samples", 0))
        total_active_samples = int(doc.get("total_active_samples", 0))
        turbine_count = int(doc.get("turbine_count", 0))
        turbines_operational_now = int(doc.get("turbines_operational_now", 0))
        total_capacity_mw = float(doc.get("total_capacity_mw") or 0.0)

        # total energy (kWh) aproximado para el farm usando la suma de potencia de muestras
        # energy_kwh = sum_power_kw_farm * (window_minutes / (total_samples * 60))  -- solo si total_samples>0
        if total_samples > 0:
            total_energy_kwh = self._compute_energy_kwh(sum_power_kw=sum_power_kw_farm, count=total_samples, window_minutes=minutes)
        else:
            total_energy_kwh = 0.0

        # farm capacity factor: total_energy_kwh / (total_capacity_kw * window_hours) * 100
        if total_capacity_mw and total_energy_kwh > 0:
            total_capacity_kw = total_capacity_mw * 1000.0
            window_hours = minutes / 60.0
            denom = total_capacity_kw * window_hours
            farm_capacity_factor_pct = round((total_energy_kwh / denom) * 100.0, 3) if denom > 0 else None
        else:
            farm_capacity_factor_pct = None

        # farm availability %: percentage of turbines whose last_state == operational (as requested)
        farm_availability_pct = None
        if turbine_count > 0:
            farm_availability_pct = round((turbines_operational_now / turbine_count) * 100.0, 2)

        # avg cp weighted: to compute properly we need per-turbine avg_power & avg_wind -> get with get_metrics_per_turbine_plus
        per_turbine = self.get_metrics_per_turbine(farm_id=farm_id, minutes=minutes, rotor_radius_m=rotor_radius_m)
        # compute cp weighted by turbine energy
        weighted_num = 0.0
        weighted_den = 0.0
        for tid, tmetrics in per_turbine.items():
            e = float(tmetrics.get("energy_kwh") or 0.0)
            cp = tmetrics.get("avg_power_coefficient_cp")
            if e and cp is not None:
                weighted_num += cp * e
                weighted_den += e
        farm_cp_weighted = None
        if weighted_den > 0:
            farm_cp_weighted = round(weighted_num / weighted_den, 4)

        result = {
            "avg_wind_speed_mps": None if avg_wind_farm is None else round(avg_wind_farm, 3),
            "total_energy_kwh": round(total_energy_kwh, 4),
            "avg_power_kw": None if avg_power_kw_farm is None else round(avg_power_kw_farm, 3),
            "farm_capacity_factor_pct": farm_capacity_factor_pct,
            "farm_availability_pct": farm_availability_pct,
            "farm_cp_weighted": farm_cp_weighted
        }

        return result
