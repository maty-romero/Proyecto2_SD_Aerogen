import threading
import time
import os

from StatNode.MQTT.telemetry_sub import TelemetrySubscriber
from StatNode.MQTT.telemetry_pub import TelemetryPublisher

FARM_ID = int(os.environ.get("FARM_ID", 1))

class StatNodeApp:
    def __init__(self, farm_id: int):
        self.farm_id = farm_id
        self._stop_event = threading.Event()

        # Configurar el suscriptor de telemetría cruda
        self.subscriber = TelemetrySubscriber(
            client_id=f"RawTelemSub-Farm{self.farm_id}",
            farm_id=self.farm_id
        )

        # Configurar el publicador de telemetría procesada
        self.publisher = TelemetryPublisher(
            client_id=f"ProcTelemPub-Farm{self.farm_id}",
            farm_id=self.farm_id,
            publish_interval=30  # Publicar estadísticas cada 30 segundos
        )

    def start(self):
        print(f"--- Iniciando StatNode para Farm ID: {self.farm_id} ---")
        
        # Iniciar suscriptor en su propio hilo
        sub_thread = threading.Thread(target=self.subscriber.run, daemon=True)
        sub_thread.start()
        
        # Iniciar publicador en su propio hilo
        pub_thread = threading.Thread(target=self.publisher.run, daemon=True)
        pub_thread.start()

        print("--- StatNode iniciado. Suscriptor y Publicador corriendo. ---")

    def stop(self):
        print("--- Deteniendo StatNode... ---")
        self.subscriber.stop()
        self.publisher.stop()
        self._stop_event.set()
        print("--- StatNode detenido. ---")

if __name__ == "__main__":
    app = StatNodeApp(farm_id=FARM_ID)
    app.start()
    # Mantener el script principal vivo
    while True:
        time.sleep(1)