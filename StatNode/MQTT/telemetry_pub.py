"""
1. Extraccion datos telemetria cada cierto intervalo tiempo - 10/15 seg (N parques eolicos) 
2. Calculo de estadisticas
3. Publicar estadisticas en topico: farms/{farm_id}/proc_telemetry - que consume o suscribe dashboard
"""

from Shared.GenericMQTTClient import GenericMQTTClient
from StatNode.DB.TelemetryDB import TelemetryDB


class StadisticalPublisher: 
       def __init__(self, farm_id: int):
        # self.RAW_TELEMETRY_TOPIC = f"farms/{farm_id}/turbines/+/raw_telemetry"
        
        #self.stat_topic_turbine = f"farms/{farm_id}/turbine{turbine_id}/proc_telemetry" # suscription topic 
        self.stat_topic_farm = f"farms/{farm_id}/proc_telemetry"
        
        self.mqtt_client = GenericMQTTClient(client_id="stat-processor") 
        self.db_service = TelemetryDB() # Servicio DB 
 
        self.db_service

        def start(self):
            pass 


        
if __name__ == '__main__':
    pass 