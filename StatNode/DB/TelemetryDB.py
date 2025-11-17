# telemetry_db.py
from datetime import datetime, timedelta, timezone
from math import pi
from typing import Optional, List, Dict, Any

from pymongo.errors import PyMongoError

from Shared.GenericMongoClient import GenericMongoClient

DEFAULT_AIR_DENSITY = 1.225  # kg/m^3
TIMESTAMP_STR_FORMAT = "%Y-%m-%d %H:%M:%S"

class TelemetryDB:
    def __init__(self, uri: str, db_name: str = "windfarm_db"):
        """
        Inicializa el servicio de base de datos para telemetría.
        La URI de conexión debe ser proporcionada explícitamente.
        """
        self.uri = uri
        self.mongo = GenericMongoClient(uri=self.uri, db_name=db_name)
        # La conexión no se establece aquí, sino a través del método connect().

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
            # La potencia activa en un sistema trifásico es P = V_LL * I * sqrt(3) * PF.
            # WindTurbine.py no envía el PF, pero podemos asumir un valor típico (ej. 0.95)
            # o simplemente no calcularlo si no viene el valor explícito.
            # Aquí lo calculamos asumiendo un PF de 1 para el peor caso.
            if V is not None and I is not None:
                try:
                    payload["active_power_kw"] = (float(V) * float(I) * (3**0.5)) / 1000.0
                except (TypeError, ValueError):
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

    def connect(self):
        """Delega la conexión al cliente genérico de MongoDB."""
        self.mongo.connect()

    def get_turbine_telemetry_by_date_range(
        self, 
        turbine_id: int, 
        from_date: str, 
        to_date: str, 
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Obtiene telemetría de una turbina específica entre dos fechas.
        
        Args:
            turbine_id: ID de la turbina
            from_date: Fecha inicio en formato ISO 8601 (ej: "2025-11-08T00:00:00Z")
            to_date: Fecha fin en formato ISO 8601 (ej: "2025-11-16T23:59:59Z")
            limit: Número máximo de registros a devolver (default: 1000)
            
        Returns:
            Lista de documentos de telemetría ordenados por timestamp descendente
        """
        try:
            # Parsear fechas ISO 8601 a datetime UTC
            from_dt = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
            to_dt = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
            
            # Convertir a UTC si no lo son
            if from_dt.tzinfo is None:
                from_dt = from_dt.replace(tzinfo=timezone.utc)
            else:
                from_dt = from_dt.astimezone(timezone.utc)
                
            if to_dt.tzinfo is None:
                to_dt = to_dt.replace(tzinfo=timezone.utc)
            else:
                to_dt = to_dt.astimezone(timezone.utc)
            
            # Construir query MongoDB
            query = {
                "turbine_id": turbine_id,
                "timestamp": {
                    "$gte": from_dt,
                    "$lte": to_dt
                }
            }
            
            # Usar el método find de GenericMongoClient
            collection = self.mongo.get_collection("telemetry")
            cursor = collection.find(query).sort("timestamp", -1).limit(limit)
            results = list(cursor)
            
            # Convertir ObjectId y datetime a strings para serialización JSON
            for doc in results:
                if "_id" in doc:
                    doc["_id"] = str(doc["_id"])
                if "timestamp" in doc and isinstance(doc["timestamp"], datetime):
                    doc["timestamp"] = doc["timestamp"].isoformat()
            
            return results
            
        except Exception as e:
            print(f"[TelemetryDB] Error al consultar telemetría: {e}")
            return []
        
    
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
        Métricas por turbina optimizadas con una única consulta de agregación.
        - avg_wind_speed_mps
        - avg_active_power_kw
        - energy_kwh
        - capacity_factor_pct
        - availability_pct
        - avg_power_coefficient_cp
        """
        since = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        window_hours = minutes / 60.0

        # El pipeline calcula todas las métricas directamente en la base de datos.
        pipeline = [
            {"$match": {"farm_id": farm_id, "timestamp": {"$gte": since}}},
            {"$group": {
                "_id": "$turbine_id",
                "avg_wind": {"$avg": "$wind_speed_mps"},
                "avg_power_kw": {"$avg": "$active_power_kw"},
                "sample_count": {"$sum": 1},
                "active_samples": {"$sum": {"$cond": [{"$eq": ["$operational_state", "operational"]}, 1, 0]}},
                "avg_capacity_mw": {"$avg": "$capacity_mw"}
            }},
            {"$addFields": {
                "energy_kwh": {
                    "$ifNull": [{"$multiply": ["$avg_power_kw", window_hours]}, 0]
                },
                "availability_pct": {
                    "$cond": {
                        "if": {"$gt": ["$sample_count", 0]},
                        "then": {"$multiply": [{"$divide": ["$active_samples", "$sample_count"]}, 100]},
                        "else": 0
                    }
                },
                "avg_power_coefficient_cp": {
                    "$cond": {
                        "if": {
                            "$and": [
                                {"$gt": ["$avg_power_kw", 0]},
                                {"$gt": ["$avg_wind", 0]},
                                {"$ne": [rotor_radius_m, None]}
                            ]
                        },
                        "then": {
                            "$divide": [
                                {"$multiply": ["$avg_power_kw", 1000]},
                                {
                                    "$multiply": [
                                        0.5, DEFAULT_AIR_DENSITY, pi,
                                        {"$pow": [rotor_radius_m, 2]},
                                        {"$pow": ["$avg_wind", 3]}
                                    ]
                                }
                            ]
                        },
                        "else": None
                    }
                }
            }},
            {"$addFields": {
                "capacity_factor_pct": {
                    "$cond": {
                        "if": {"$and": [
                            {"$gt": ["$avg_capacity_mw", 0]},
                            {"$gt": [window_hours, 0]}
                        ]},
                        "then": {
                            "$multiply": [
                                {"$divide": [
                                    "$energy_kwh",
                                    {"$multiply": ["$avg_capacity_mw", 1000, window_hours]}
                                ]},
                                100
                            ]
                        },
                        "else": None
                    }
                }
            }},
            {"$sort": {"_id": 1}}
        ]

        try:
            col = self.mongo.get_collection("telemetry")
            cursor = list(col.aggregate(pipeline))
        except PyMongoError:
            raise

        # El post-procesamiento es mínimo, solo para formatear la salida.
        out: Dict[int, dict] = {}
        for doc in cursor:
            tid = doc["_id"]
            out[tid] = {
                "avg_wind_speed_mps": round(doc["avg_wind"], 3) if doc.get("avg_wind") is not None else None,
                "avg_active_power_kw": round(doc["avg_power_kw"], 3) if doc.get("avg_power_kw") is not None else None,
                "energy_kwh": round(doc.get("energy_kwh", 0), 4),
                "capacity_factor_pct": round(doc["capacity_factor_pct"], 3) if doc.get("capacity_factor_pct") is not None else None,
                "availability_pct": round(doc.get("availability_pct", 0), 2),
                "avg_power_coefficient_cp": round(doc["avg_power_coefficient_cp"], 4) if doc.get("avg_power_coefficient_cp") is not None else None,
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
                "avg_voltage": {"$avg": "$output_voltage_v"},
                "sum_reactive_power_kvar": {"$sum": "$reactive_power_kvar"},
                "max_wind": {"$max": "$wind_speed_mps"},
                "min_wind": {"$min": "$wind_speed_mps"},
                "sample_count": {"$sum": 1},
                "active_samples": {"$sum": {"$cond": [{"$eq": ["$operational_state", "operational"]}, 1, 0]}},
                "last_state": {"$last": "$operational_state"},
                "avg_capacity_mw": {"$avg": "$capacity_mw"}
            }},
            # Pre-cálculo de métricas por turbina antes de la agregación final
            {"$addFields": {
                "energy_kwh": {"$multiply": ["$avg_power_kw", minutes / 60.0]},
                "cp_estimate": {
                    "$let": {
                        "vars": {
                            "p_w": {"$multiply": ["$avg_power_kw", 1000]},
                            "denom": {
                                "$multiply": [0.5, DEFAULT_AIR_DENSITY, pi, {"$pow": [rotor_radius_m, 2]}, {"$pow": ["$avg_wind", 3]}]
                            }
                        },
                        "in": {
                            "$cond": {
                                "if": {"$gt": ["$$denom", 0]},
                                "then": {"$divide": ["$$p_w", "$$denom"]},
                                "else": None
                            }
                        }
                    }}
            }},
            # Segundo group: sumar/contar a nivel farm
            # Aquí calculamos los promedios y totales para todo el parque.
            # El factor de potencia se calcula aquí usando la potencia activa y reactiva total.
            {"$group": {
                "_id": None,
                "avg_wind_farm": {"$avg": "$avg_wind"},
                "avg_power_kw_farm": {"$avg": "$avg_power_kw"},
                "sum_power_kw_farm": {"$sum": "$sum_power_kw"},
                "total_samples": {"$sum": "$sample_count"},
                "total_active_samples": {"$sum": "$active_samples"},
                "avg_voltage_farm": {"$avg": "$avg_voltage"},
                "max_wind_farm": {"$max": "$max_wind"},
                "min_wind_farm": {"$min": "$min_wind"},
                "sum_reactive_power_kvar_farm": {"$sum": "$sum_reactive_power_kvar"},
                "turbine_count": {"$sum": 1},
                "turbines_operational_now": {"$sum": {"$cond": [{"$eq": ["$last_state", "operational"]}, 1, 0]}},
                "total_capacity_mw": {"$sum": {"$ifNull": ["$avg_capacity_mw", 0]}},
                # Para el CP ponderado, necesitamos sumar (cp * energia) y (energia)
                "cp_weighted_numerator": {"$sum": 
                    {"$multiply": ["$cp_estimate", "$energy_kwh"]}
                },
                "cp_weighted_denominator": {"$sum": "$energy_kwh"}
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
                "max_wind_speed_mps": None,
                "min_wind_speed_mps": None,
                "avg_voltage_v": None,
                "avg_power_factor": None,
                "time_based_availability_pct": None,
                "farm_cp_weighted": None
            }

        doc = res[0]
        avg_wind_farm = doc.get("avg_wind_farm")
        avg_power_kw_farm = doc.get("avg_power_kw_farm")
        sum_power_kw_farm = doc.get("sum_power_kw_farm") or 0.0
        sum_reactive_power_kvar_farm = doc.get("sum_reactive_power_kvar_farm") or 0.0
        total_samples = int(doc.get("total_samples", 0))
        total_active_samples = int(doc.get("total_active_samples", 0))
        turbine_count = int(doc.get("turbine_count", 0))
        turbines_operational_now = int(doc.get("turbines_operational_now", 0))
        total_capacity_mw = float(doc.get("total_capacity_mw") or 0.0)
        max_wind_farm = doc.get("max_wind_farm")
        min_wind_farm = doc.get("min_wind_farm")
        avg_voltage_farm = doc.get("avg_voltage_farm")
        cp_num = doc.get("cp_weighted_numerator")
        cp_den = doc.get("cp_weighted_denominator")

        # Calcular el factor de potencia promedio del parque
        avg_power_factor = None
        apparent_power = (sum_power_kw_farm**2 + sum_reactive_power_kvar_farm**2)**0.5
        if apparent_power > 0:
            avg_power_factor = round(sum_power_kw_farm / apparent_power, 2)

        # Calcular CP ponderado
        farm_cp_weighted = None
        if cp_den is not None and cp_num is not None and cp_den > 0:
            farm_cp_weighted = round(cp_num / cp_den, 4)

        # Calcular disponibilidad basada en tiempo
        time_based_availability_pct = None
        if total_samples > 0:
            time_based_availability_pct = round((total_active_samples / total_samples) * 100.0, 2)


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

        return {
            "avg_wind_speed_mps": round(avg_wind_farm, 3) if avg_wind_farm is not None else None,
            "total_energy_kwh": round(total_energy_kwh, 4),
            "avg_power_kw": round(avg_power_kw_farm, 3) if avg_power_kw_farm is not None else None,
            "farm_capacity_factor_pct": farm_capacity_factor_pct,
            "farm_availability_pct": farm_availability_pct,
            "farm_cp_weighted": farm_cp_weighted,
            "max_wind_speed_mps": round(max_wind_farm, 2) if max_wind_farm is not None else None,
            "min_wind_speed_mps": round(min_wind_farm, 2) if min_wind_farm is not None else None,
            "avg_voltage_v": round(avg_voltage_farm, 2) if avg_voltage_farm is not None else None,
            "avg_power_factor": avg_power_factor,
            "time_based_availability_pct": time_based_availability_pct
        }

    def get_hourly_production_last_24h(self, farm_id: int) -> List[Dict[str, Any]]:
        """
        Calcula la producción de energía (kWh) por hora para las últimas 24 horas.
        CORREGIDO: Ahora calcula correctamente la energía por hora.
        """
        col = self.mongo.get_collection("telemetry")
        latest_record = col.find_one({"farm_id": farm_id}, sort=[("timestamp", -1)])

        if not latest_record:
            return []

        # Usar la fecha del último registro como referencia
        ref_time = latest_record['timestamp']
        end_time = (ref_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
        start_time = end_time - timedelta(hours=24)

        pipeline = [
            {"$match": {
                "farm_id": farm_id,
                "timestamp": {"$gte": start_time, "$lt": end_time},
                "active_power_kw": {"$exists": True, "$ne": None}
            }},
            {"$group": {
                "_id": {"$dateTrunc": {"date": "$timestamp", "unit": "hour"}},
                "avg_power_kw": {"$avg": "$active_power_kw"},
                "sample_count": {"$sum": 1}
            }},
            # CORRECCIÓN: Calcular energía considerando el número de muestras
            {"$project": {
                "energy_kwh": {
                    "$cond": {
                        "if": {"$gt": ["$sample_count", 0]},
                        "then": {
                            "$multiply": [
                                "$avg_power_kw",
                                {"$divide": [60, "$sample_count"]}  # minutos/muestra * horas
                            ]
                        },
                        "else": 0.0
                    }
                }
            }},
            {"$sort": {"_id": 1}}
        ]

        try:
            results = list(col.aggregate(pipeline))
            production_by_hour = {doc["_id"]: round(doc["energy_kwh"], 2) for doc in results}
        except PyMongoError as e:
            print(f"Error en get_hourly_production_last_24h: {e}")
            return []

        chart_data = []
        for i in range(24):
            current_hour = start_time + timedelta(hours=i)
            chart_data.append({
                "timestamp": current_hour.strftime("%H:00"),
                "value": production_by_hour.get(current_hour, 0.0)
            })

        return chart_data


    def get_daily_production_last_7_days(self, farm_id: int) -> List[Dict[str, Any]]:
        """
        Calcula la producción de energía (kWh) por día para los últimos 7 días.
        CORREGIDO: Calcula correctamente la energía horaria antes de sumarla por día.
        """
        col = self.mongo.get_collection("telemetry")
        latest_record = col.find_one({"farm_id": farm_id}, sort=[("timestamp", -1)])

        if not latest_record:
            return []

        end_date = latest_record['timestamp'].replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        start_date = end_date - timedelta(days=7)
        
        pipeline = [
            {"$match": {
                "farm_id": farm_id, 
                "timestamp": {"$gte": start_date, "$lt": end_date},
                "active_power_kw": {"$exists": True, "$ne": None}
            }},
            # Etapa 1: Agrupar por hora y calcular energía horaria
            {"$group": {
                "_id": {"$dateTrunc": {"date": "$timestamp", "unit": "hour", "timezone": "UTC"}},
                "avg_power_kw": {"$avg": "$active_power_kw"},
                "sample_count": {"$sum": 1}
            }},
            # CORRECCIÓN: Calcular energía horaria correctamente
            {"$addFields": {
                "hourly_energy_kwh": {
                    "$cond": {
                        "if": {"$gt": ["$sample_count", 0]},
                        "then": {"$multiply": ["$avg_power_kw", {"$divide": [60, "$sample_count"]}]},
                        "else": 0.0
                    }
                }
            }},
            # Etapa 2: Agrupar por día
            {"$group": {
                "_id": {"$dateTrunc": {"date": "$_id", "unit": "day", "timezone": "UTC"}},
                "daily_energy_kwh": {"$sum": "$hourly_energy_kwh"}
            }},
            {"$sort": {"_id": 1}}
        ]

        try:
            results = list(col.aggregate(pipeline))
            production_by_day = {doc["_id"]: round(doc["daily_energy_kwh"], 2) for doc in results}
        except PyMongoError as e:
            print(f"Error en get_daily_production_last_7_days: {e}")
            return []

        chart_data = []
        day_map = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

        for i in range(7):
            day_to_check = start_date + timedelta(days=i)
            chart_data.append({
                "timestamp": day_map[day_to_check.weekday()],
                "value": production_by_day.get(day_to_check, 0.0)
            })
        
        return chart_data


    def get_monthly_production_last_12_months(self, farm_id: int) -> List[Dict[str, Any]]:
        """
        Calcula la producción de energía (kWh) por mes para los últimos 12 meses.
        CORREGIDO: Calcula correctamente la energía horaria antes de agrupar por día y mes.
        """
        col = self.mongo.get_collection("telemetry")
        latest_record = col.find_one({"farm_id": farm_id}, sort=[("timestamp", -1)])

        if not latest_record:
            return []
        
        ref_date = latest_record['timestamp']
        start_of_ref_month = ref_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        since_year = start_of_ref_month.year
        since_month = start_of_ref_month.month - 11
        if since_month <= 0:
            since_month += 12
            since_year -= 1
        since = start_of_ref_month.replace(year=since_year, month=since_month)

        pipeline = [
            {"$match": {
                "farm_id": farm_id, 
                "timestamp": {"$gte": since},
                "active_power_kw": {"$exists": True, "$ne": None}
            }},
            # Etapa 1: Calcular energía por hora
            {"$group": {
                "_id": {"$dateTrunc": {"date": "$timestamp", "unit": "hour", "timezone": "UTC"}},
                "avg_power_kw": {"$avg": "$active_power_kw"},
                "sample_count": {"$sum": 1}
            }},
            # CORRECCIÓN: Calcular energía horaria correctamente
            {"$addFields": {
                "hourly_energy_kwh": {
                    "$cond": {
                        "if": {"$gt": ["$sample_count", 0]},
                        "then": {"$multiply": ["$avg_power_kw", {"$divide": [60, "$sample_count"]}]},
                        "else": 0.0
                    }
                }
            }},
            # Etapa 2: Agrupar por día
            {"$group": {
                "_id": {"$dateTrunc": {"date": "$_id", "unit": "day", "timezone": "UTC"}},
                "daily_energy_kwh": {"$sum": "$hourly_energy_kwh"}
            }},
            # Etapa 3: Agrupar por mes
            {"$group": {
                "_id": {"$dateTrunc": {"date": "$_id", "unit": "month", "timezone": "UTC"}},
                "monthly_energy_kwh": {"$sum": "$daily_energy_kwh"}
            }},
            {"$sort": {"_id": 1}}
        ]

        try:
            results = list(col.aggregate(pipeline))
            production_by_month = {
                doc["_id"].strftime("%Y-%m"): round(doc["monthly_energy_kwh"], 2) for doc in results
            }
        except PyMongoError as e:
            print(f"Error en get_monthly_production_last_12_months: {e}")
            return []

        chart_data = []
        month_map = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

        current_month_date = since
        for _ in range(12):
            year = current_month_date.year
            month = current_month_date.month
            month_key = f"{year}-{month:02d}"
            chart_data.append({
                "timestamp": month_map[month - 1],
                "value": production_by_month.get(month_key, 0.0)
            })
            next_month = month + 1
            next_year = year
            if next_month > 12:
                next_month = 1
                next_year += 1
            current_month_date = current_month_date.replace(year=next_year, month=next_month)

        return chart_data


    def get_hourly_avg_windspeed_last_24h(self, farm_id: int) -> List[Dict[str, Any]]:
        """
        Calcula el promedio de velocidad del viento por hora para las últimas 24 horas.
        CORREGIDO: Filtro mejorado para valores nulos.
        """
        col = self.mongo.get_collection("telemetry")
        latest_record = col.find_one({"farm_id": farm_id}, sort=[("timestamp", -1)])

        if not latest_record:
            return []

        ref_time = latest_record['timestamp']
        end_time = (ref_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
        start_time = end_time - timedelta(hours=24)
        
        pipeline = [
            {"$match": {
                "farm_id": farm_id, 
                "timestamp": {"$gte": start_time, "$lt": end_time}, 
                "wind_speed_mps": {"$exists": True, "$ne": None, "$type": "number"}
            }},
            {"$group": {
                "_id": {"$dateTrunc": {"date": "$timestamp", "unit": "hour", "timezone": "UTC"}},
                "avg_wind_speed": {"$avg": "$wind_speed_mps"}
            }},
            {"$sort": {"_id": 1}}
        ]

        try:
            results = list(col.aggregate(pipeline))
        except PyMongoError as e:
            print(f"Error en get_hourly_avg_windspeed_last_24h: {e}")
            return []

        avg_by_hour = {doc["_id"]: round(doc.get("avg_wind_speed", 0.0), 2) for doc in results}

        chart_data = []
        for i in range(24):
            hour_to_check = start_time + timedelta(hours=i)
            chart_data.append({
                "timestamp": hour_to_check.strftime("%H:00"),
                "value": avg_by_hour.get(hour_to_check, 0.0)
            })
        
        return chart_data


    def get_hourly_avg_voltage_last_24h(self, farm_id: int) -> List[Dict[str, Any]]:
        """
        Calcula el promedio de voltaje por hora para las últimas 24 horas.
        CORREGIDO: Filtro mejorado para valores nulos.
        """
        col = self.mongo.get_collection("telemetry")
        latest_record = col.find_one({"farm_id": farm_id}, sort=[("timestamp", -1)])

        if not latest_record:
            return []

        ref_time = latest_record['timestamp']
        end_time = (ref_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
        start_time = end_time - timedelta(hours=24)
        
        pipeline = [
            {"$match": {
                "farm_id": farm_id, 
                "timestamp": {"$gte": start_time, "$lt": end_time}, 
                "output_voltage_v": {"$exists": True, "$ne": None, "$type": "number"}
            }},
            {"$group": {
                "_id": {"$dateTrunc": {"date": "$timestamp", "unit": "hour", "timezone": "UTC"}},
                "avg_voltage": {"$avg": "$output_voltage_v"}
            }},
            {"$sort": {"_id": 1}}
        ]

        try:
            results = list(col.aggregate(pipeline))
        except PyMongoError as e:
            print(f"Error en get_hourly_avg_voltage_last_24h: {e}")
            return []

        avg_by_hour = {doc["_id"]: round(doc.get("avg_voltage", 0.0), 2) for doc in results}

        chart_data = []
        for i in range(24):
            hour_to_check = start_time + timedelta(hours=i)
            chart_data.append({
                "timestamp": hour_to_check.strftime("%H:00"),
                "value": avg_by_hour.get(hour_to_check, 0.0)
            })
        
        return chart_data
