import json
import time
from threading import Lock, Thread

from Shared.GenericMQTTClient import GenericMQTTClient

CLEAN_TELEMETRY_TOPIC = "farms/{farm_id}/turbines/+/clean_telemetry".format(farm_id=1)
STATS_TOPIC = "farms/{farm_id}/stats".format(farm_id=1)

class StatNode:
    def __init__(self, client_id: str = "stat_node_client"):
        self.mqtt_client = GenericMQTTClient(client_id=client_id)
        self.turbines_data = {}
        self.data_lock = Lock()
        self.publish_interval = 10  # Publicar estadísticas cada 10 segundos
        self._stop_event = False

    def _message_callback(self, client, userdata, msg):
        """Callback para procesar los mensajes de telemetría de las turbinas."""
        try:
            payload = json.loads(msg.payload.decode())
            turbine_id = payload.get("turbine_id")
            if turbine_id is not None:
                with self.data_lock:
                    self.turbines_data[turbine_id] = payload
                # print(f"[StatNode] Datos actualizados para turbina {turbine_id}")
        except (json.JSONDecodeError, KeyError) as e:
            print(f"[StatNode] Error procesando mensaje: {e}")

    def _publish_stats(self):
        """Calcula y publica las estadísticas agregadas del parque eólico."""
        while not self._stop_event:
            with self.data_lock:
                # Copiamos los datos para trabajar de forma segura
                current_data = list(self.turbines_data.values())

            if not current_data:
                time.sleep(self.publish_interval)
                continue

            total_turbines = len(current_data)
            operational_turbines = 0
            total_active_power_kw = 0
            wind_speeds = []
            stopped_turbines = 0
            fault_turbines = 0

            for data in current_data:
                if data.get("operational_state") == "operational":
                    operational_turbines += 1
                    total_active_power_kw += data.get("active_power_kw", 0)
                    wind_speeds.append(data.get("wind_speed_mps", 0))
                elif data.get("operational_state") == "stopped":
                    stopped_turbines += 1
                elif data.get("operational_state") == "fault":
                    fault_turbines += 1

            avg_wind_speed = sum(wind_speeds) / len(wind_speeds) if wind_speeds else 0

            # Generamos datos de producción horaria simulados (esto debería venir de una base de datos en un caso real)
            hourly_production = [
                round(max(0, (total_active_power_kw * (0.8 + random.random() * 0.4))), 2) for _ in range(24)
            ]
            hourly_timestamps = [f"{h:02d}:00" for h in range(24)]

            stats_payload = {
                "farm_id": 1,
                "farm_name": "Comodoro Rivadavia",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_active_power_kw": round(total_active_power_kw, 2),
                "total_reactive_power_kvar": round(total_active_power_kw * 0.3, 2),
                "totalTurbines": total_turbines,
                "operational_turbines": operational_turbines,
                "stopped_turbines": stopped_turbines,
                "maintenance_turbines": total_turbines - operational_turbines - stopped_turbines - fault_turbines,
                "fault_turbines": fault_turbines,
                "avg_wind_speed_mps": round(avg_wind_speed, 2),
                "max_wind_speed_mps": max(wind_speeds) if wind_speeds else 0,
                "min_wind_speed_mps": min(wind_speeds) if wind_speeds else 0,
                "predominant_wind_direction_deg": 245,
                "avg_power_factor": 0.96,
                "avg_voltage_v": 692.5,
                "hourly_production_kwh": hourly_production,
                "hourly_timestamps": hourly_timestamps
            }

            self.mqtt_client.publish(STATS_TOPIC, stats_payload, qos=1)
            print(f"[StatNode] Estadísticas publicadas: {operational_turbines}/{total_turbines} activas, {total_active_power_kw:.2f} kW")

            time.sleep(self.publish_interval)

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
    import random
    stat_node = StatNode()
    stat_node.run()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # stat_node.stop()
        print("--- [StatNode] Proceso terminado. ---")