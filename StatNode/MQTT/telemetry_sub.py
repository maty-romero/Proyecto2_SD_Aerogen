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

# TOPIC_TELEMETRY = "farms/{farm_id}/turbines/+/raw_telemetry"

class RawTelemetrySuscriber:
    def __init__(self, farm_id: int):
        # self.RAW_TELEMETRY_TOPIC = f"farms/{farm_id}/turbines/+/raw_telemetry"
        
        self.raw_telemetry_topic = f"farms/{farm_id}/turbines/+/raw_telemetry" # suscription topic 
        self.mqtt_client = GenericMQTTClient(client_id="stat-processor") 
        self.db_service = TelemetryDB() # Servicio DB 

        
        # Ejemplo uso MongoSingleton
        # self.mongo_client.insert_one("turbine_data", {"turbine_id": "T-001", "rpm": 1500})
        
        # ---> Resto de la configuracion
        
    def start(self):
        self.mqtt_client.connect()
        self.mqtt_client.subscribe(self.raw_telemetry_topic, self._message_callback)
        import time
        try:
            # thread calculo estadisticas
            thread_stats = threading.Thread(target=self.get_stadistics)
            thread_stats.start()
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            self.mqtt_client.disconnect()
    
    
    def _message_callback(self, client, userdata, msg):
        payload = msg.payload.decode()
        try:
            data: dict = json.loads(payload)
            print(f"\nRecibido en '{msg.topic}': {data} \n******")
        
            # Insercion en BD 
            self.db_service.insert_telemetry(data)
            #insertion_id = self.mongo_client.insert_one("Telemtry", data)
            #print(f"Documento insertado en 'Telemetry' con _id={insertion_id}\n")
            
        except json.JSONDecodeError:
            data = payload
        except Exception as e:
            print(f"Error genérico: {e}\n")
        
    def get_stadistics(self):
        while True: 
            metrics_per_turbine = self.db_service.get_metrics_per_turbine(
                farm_id=1,
                minutes=1,
                rotor_radius_m=40.0  # radio constante
            )

            print(f"Metricas por turbina: {metrics_per_turbine}\n")
            
            metrics_farm = self.db_service.get_metrics_aggregate(
                farm_id=1,
                minutes=1,
                rotor_radius_m=40.0  # radio constante
            )
            
            print(f"Metricas por farm-{1}: {metrics_per_turbine}\n")
            time.sleep(15)

        
if __name__ == '__main__':
    sub = RawTelemetrySuscriber(farm_id=1)
    sub.start()
    