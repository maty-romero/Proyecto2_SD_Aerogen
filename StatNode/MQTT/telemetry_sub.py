# Raw Telemetry Suscriber 
"""
1. Suscripcion a Topico telemetria datos crudos
2. Formateo de datos 
3. Guardado en BD - Colecciones por Parques/Wind_Farms 
"""
import json
import threading
import time

from Shared.GenericMQTTClient import GenericMQTTClient
from Shared.MongoSingleton import MongoSingleton
from StatNode.DB.TelemetryDB import TelemetryDB 

# --- PLANTILLA TOPICOS MQTT ---
RAW_TURBINE_TELEMETRY_TOPIC = "windfarm/turbines/+/clean_telemetry" # suscription topic

# Se asume 1 instancia Suscriptor por Farm  
class TelemetrySubscriber:  
    def __init__(self, client_id: str, farm_id: int):
        self.farm_id = farm_id 
        self.mqtt_client = GenericMQTTClient(client_id=client_id) 
        self.db_service = TelemetryDB() # Servicio DB  
        # ---> Resto de la configuracion
    
    # telemetria todas las turbinas para ese farm_id
    def get_subscription_topic(self) -> str:
        return RAW_TURBINE_TELEMETRY_TOPIC
    
    def run(self):
        self.mqtt_client.connect()
       
        self.mqtt_client.subscribe(
            self.get_subscription_topic(),
            self._message_callback
        )
        # El bucle principal se maneja en main.py, aquí solo nos aseguramos de que el cliente MQTT siga corriendo.
    
    def _message_callback(self, client, userdata, msg):
        payload = msg.payload.decode()
        try:
            data: dict = json.loads(payload)
            print(f"\nRecibido en '{msg.topic}': {data} \n******")
        
            self.db_service.insert_telemetry(data) # Insercion para historial
            
        except json.JSONDecodeError:
            data = payload
        except Exception as e:
            print(f"Error genérico: {e}\n")

    def stop(self):
        self.mqtt_client.disconnect()
    
if __name__ == '__main__':
    # Se asume 1 instancia por Farm
    sub = TelemetrySubscriber(client_id="TestSub", farm_id=1)
    sub.run()
    # Mantener vivo para pruebas
    while True: time.sleep(1)
    