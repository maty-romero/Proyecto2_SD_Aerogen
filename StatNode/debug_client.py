import json
import time
from Shared.GenericMQTTClient import GenericMQTTClient

RAW_TURBINE_TELEMETRY_TOPIC = "windfarm/turbines/+/measurements"

class FrontendDebugSubscriber:
    def __init__(self, client_id: str):
        self.mqtt_client = GenericMQTTClient(client_id=client_id)

    def run(self):
        print("--- [DEBUG CLIENT] Iniciando cliente de depuración para el Frontend ---")
        self.mqtt_client.connect()
        self.mqtt_client.subscribe(
            RAW_TURBINE_TELEMETRY_TOPIC,
            self._message_callback
        )
        print(f"--- [DEBUG CLIENT] Suscrito a: {RAW_TURBINE_TELEMETRY_TOPIC} ---")

    def _message_callback(self, client, userdata, msg):
        payload = msg.payload.decode()
        print("--------------------------------------------------------------------------")
        print(f"[FRONTEND DEBUGGER] Mensaje recibido en tópico: '{msg.topic}'")
        print(f"[FRONTEND DEBUGGER] Payload: {payload}")
        print("--------------------------------------------------------------------------\n")

if __name__ == '__main__':
    debugger = FrontendDebugSubscriber(client_id="frontend_debugger_client")
    debugger.run()
    while True:
        time.sleep(10)