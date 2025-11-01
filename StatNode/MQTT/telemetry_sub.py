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
RAW_TURBINE_TELEMETRY_TOPIC = "farms/{farm_id}/turbines/+/raw_telemetry" # suscription topic

# Se asume 1 instancia Suscriptor por Farm  
class RawTelemetrySuscriber:  
    def __init__(self, farm_id: int):
        self.farm_id = farm_id 
        self.mqtt_client = GenericMQTTClient(client_id="RawTelemSub-Farm"+str(farm_id)) 
        self.db_service = TelemetryDB() # Servicio DB  
        # ---> Resto de la configuracion
    
    # telemetria todas las turbinas para ese farm_id
    def get_topic_telem_raw(self, farm_id: int) -> str: 
        return RAW_TURBINE_TELEMETRY_TOPIC.format(farm_id=farm_id)
    
    def start(self):
        self.mqtt_client.connect()
       
        self.mqtt_client.subscribe(
            self.get_topic_telem_raw(self.farm_id), 
            self._message_callback
        )
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.mqtt_client.disconnect()
    
    
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
        
    
if __name__ == '__main__':
    # Se asume 1 instancia por Farm
    sub = RawTelemetrySuscriber(farm_id=1)
    sub.start()
    