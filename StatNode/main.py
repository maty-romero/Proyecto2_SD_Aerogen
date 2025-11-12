import json
import time
from threading import Lock, Thread
from typing import Dict, Any

from Shared.GenericMQTTClient import GenericMQTTClient
from StatNode.DB.TelemetryDB import TelemetryDB

CLEAN_TELEMETRY_TOPIC = "farms/{farm_id}/turbines/+/clean_telemetry".format(farm_id=1)
STATS_TOPIC = "farms/{farm_id}/stats".format(farm_id=1)

class StatNode:
    # El StatNode ahora es agnóstico al farm_id, pero lo usará para las consultas. Asumimos farm_id=1 por defecto.
    def __init__(self, client_id: str = "stat_node_client"):
        self.mqtt_client = GenericMQTTClient(client_id=client_id)
        self.turbines_data = {}
        self.data_lock = Lock()
        self.publish_interval = 10  # Publicar estadísticas cada 10 segundos
        self._stop_event = False

        # Instancia del servicio de base de datos
        self.db_service = TelemetryDB()

    def _message_callback(self, client, userdata, msg):
        """Callback para procesar los mensajes de telemetría de las turbinas."""
        try:
            payload = json.loads(msg.payload.decode())
            
            # Insertar en la base de datos
            self.db_service.insert_telemetry(payload)

            turbine_id = payload.get("turbine_id")
            if turbine_id is not None:
                with self.data_lock:
                    # Guardamos los datos más recientes en memoria para tener un conteo rápido de turbinas
                    self.turbines_data[turbine_id] = payload
                # print(f"[StatNode] Datos actualizados para turbina {turbine_id}")
        except (json.JSONDecodeError, KeyError) as e:
            print(f"[StatNode] Error procesando mensaje: {e}")

    def _get_turbine_counts_by_state(self) -> Dict[str, int]:
        """Cuenta las turbinas por estado operacional a partir de los datos en memoria."""
        states = {
            "operational": 0,
            "stopped": 0,
            "fault": 0,
            "maintenance": 0,
            "standby": 0,
            "unknown": 0
        }
        with self.data_lock:
            for data in self.turbines_data.values():
                state = data.get("operational_state", "unknown")
                if state in states:
                    states[state] += 1
                else:
                    states["unknown"] += 1
        return states

    def _publish_stats(self):
        """Calcula y publica las estadísticas agregadas del parque eólico."""
        while not self._stop_event:
            time.sleep(self.publish_interval)

            # Asumimos farm_id=1. En un sistema multi-farm, esto debería ser dinámico.
            farm_id = 1

            # 1. Obtener métricas agregadas del farm desde la BD
            farm_metrics = self.db_service.get_metrics_farm(farm_id=farm_id, minutes=5)
            if not farm_metrics or farm_metrics.get("avg_power_kw") is None:
                print("[StatNode] No hay suficientes datos en la BD para calcular métricas del parque.")
                continue

            # 2. Obtener producción horaria de las últimas 24h
            hourly_data = self.db_service.get_hourly_production_last_24h(farm_id=farm_id)
            print(f"[StatNode] Hourly data: {hourly_data}")

            # 3. Obtener producción diaria de los últimos 7 días
            daily_data = self.db_service.get_daily_production_last_7_days(farm_id=farm_id)
            print(f"[StatNode] Daily data: {daily_data}")

            # 4. Obtener producción mensual de los últimos 12 meses
            monthly_data = self.db_service.get_monthly_production_last_12_months(farm_id=farm_id)
            print(f"[StatNode] Monthly data: {monthly_data}")

            # 5. Obtener promedios horarios de viento y voltaje
            wind_speed_data = self.db_service.get_hourly_avg_windspeed_last_24h(farm_id=farm_id)
            print(f"[StatNode] Wind speed data: {wind_speed_data}")
            voltage_data = self.db_service.get_hourly_avg_voltage_last_24h(farm_id=farm_id)
            print(f"[StatNode] Voltage data: {voltage_data}")

            # 6. Obtener conteo de turbinas por estado desde la memoria (más rápido y en tiempo real)
            turbine_counts = self._get_turbine_counts_by_state()
            total_turbines = len(self.turbines_data)

            # Construir el payload de estadísticas de acuerdo a la documentación del frontend
            stats_payload = {
                # --- Identificación y estado general ---
                "farm_id": farm_id,
                "total_turbines": total_turbines,
                "operational_turbines": turbine_counts.get("operational", 0),
                "turbine_counts_by_state": turbine_counts,

                # --- Métricas agregadas del parque (de la BD) ---
                # Usamos .get() para evitar KeyErrors si una métrica no se puede calcular
                "total_active_power_kw": farm_metrics.get("avg_power_kw"), # El frontend espera total_active_power_kw
                "total_energy_kwh": farm_metrics.get("total_energy_kwh"), # No está en el doc del front, pero es útil
                "avg_wind_speed_mps": farm_metrics.get("avg_wind_speed_mps"),
                "max_wind_speed_mps": farm_metrics.get("max_wind_speed_mps"),
                "min_wind_speed_mps": farm_metrics.get("min_wind_speed_mps"),
                "avg_power_factor": farm_metrics.get("avg_power_factor"),
                "avg_voltage_v": farm_metrics.get("avg_voltage_v"),
                # "predominant_wind_direction_deg": farm_metrics.get("predominant_wind_direction_deg"), # Nota: Esto no se calcula aún

                # --- Datos para gráficos (estructura plana, como espera el frontend) ---
                "hourly_production_kwh": hourly_data.get("hourly_production_kwh", []),
                "hourly_timestamps": hourly_data.get("hourly_timestamps", []),
                "daily_production_kwh": daily_data.get("daily_production_kwh", []),
                "daily_timestamps": daily_data.get("daily_timestamps", []),
                "monthly_production_kwh": monthly_data.get("monthly_production_kwh", []),
                "monthly_timestamps": monthly_data.get("monthly_timestamps", []),
                "hourly_avg_wind_speed": wind_speed_data.get("hourly_avg_wind_speed", []),
                "hourly_avg_voltage": voltage_data.get("hourly_avg_voltage", [])
            }

            print(f"[StatNode] Publishing stats: {stats_payload}")
            self.mqtt_client.publish(STATS_TOPIC, stats_payload, qos=1)
            print(f"[StatNode] Estadísticas publicadas: {turbine_counts.get('operational', 0)}/{total_turbines} activas.")
    
    def run(self):
        """Inicia el StatNode."""
        print("--- [StatNode] Iniciando nodo de estadísticas ---")
        self.mqtt_client.connect() 
        self.mqtt_client.subscribe(
            CLEAN_TELEMETRY_TOPIC,
            self._message_callback,
            qos=0
        )
        print(f"--- [StatNode] Suscrito a: {CLEAN_TELEMETRY_TOPIC} ---")

        # Iniciar el hilo para publicar estadísticas
        stats_thread = Thread(target=self._publish_stats, daemon=True)
        stats_thread.start()

    def stop(self):
        """Detiene el StatNode."""
        print("--- [StatNode] Deteniendo nodo de estadísticas ---")
        self._stop_event = True
        self.mqtt_client.disconnect()

if __name__ == '__main__':
    stat_node = StatNode()
    stat_node.run()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # stat_node.stop()
        print("--- [StatNode] Proceso terminado. ---")