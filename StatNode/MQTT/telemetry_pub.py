import threading
import time
from Shared.GenericMQTTClient import GenericMQTTClient
from StatNode.DB.TelemetryDB import TelemetryDB

"""
Responsabilidades de este fichero: 

Publicaciones de: 
1. Estadisticas por turbina y por parque eolico cada cierto intervalo de tiempo (ProcessedTelemetryPublisher)
2. Alertas si es necesario (no implementado) --> Otra clase 

"""
# --- PLANTILLA TOPICOS MQTT ---
PROC_TELEMETRY_TOPIC = "farms/{farm_id}/proc_telemetry"

class ProcessedTelemetryPublisher:
    def __init__(self, farm_id: int, publish_interval: int = 30):
        self.farm_id = farm_id
        self.publish_interval = publish_interval
        self.mqtt_client = GenericMQTTClient(client_id=f"pub-stats-{farm_id}")
        self.db_service = TelemetryDB()  # usa el mismo conector singleton
        self._stop_event = threading.Event()

    # metodo para obtener el topic
    def get_topic_telem_proc(self) -> str:
        return PROC_TELEMETRY_TOPIC.format(farm_id=self.farm_id)

    # hilo ppal publicacion
    def start(self):
        self.mqtt_client.connect()
        thread = threading.Thread(target=self._publish_loop, daemon=True)
        thread.start()
        print(f"[Publisher] Comienzo publisher telemetria procesada - Farm-{self.farm_id}\n")
        try:
            while not self._stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            print("[Publisher] Stopping...")
            self._stop_event.set()
            self.mqtt_client.disconnect()

    def _publish_loop(self):
        time.sleep(10)  # espera inicial para que haya datos en DB
        while not self._stop_event.is_set():
            
            turbine_metrics = self.db_service.get_metrics_per_turbine(
                farm_id=self.farm_id,
                minutes=3,
                rotor_radius_m=40.0 # Radio constante
            )
            
            farm_metrics = self.db_service.get_metrics_farm(
                farm_id=self.farm_id,
                minutes=3,
                rotor_radius_m=40.0 # Radio constante
            )

            payload = {
                "farm_id": self.farm_id,
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "turbine_metrics": turbine_metrics,
                "farm_metrics": farm_metrics
            }

            topic = self.get_topic_telem_proc()
            self.mqtt_client.publish(topic, payload, qos=1, retain=True)

            print(f"[Publisher] Published processed metrics to '{topic}' at {payload['generated_at']}")

            time.sleep(self.publish_interval)


if __name__ == "__main__":
    # Una instancia por parque eolico 
    publisher = ProcessedTelemetryPublisher(farm_id=1)
    publisher.start()