"""
- Calculos por turbina, parque o periodo:

* Estadistica descriptiva
- Media, mediana, desviación estándar
- Minimos y maximos por variable
- Percentiles (p25, p75) ?? 

* Analisis temporal
- Tendencias por hora/dia/semana
- Correlacion entre variables 
    - Viento vs voltaje
    
* Alertas / Deteccion de umbrales --> Delegar al broker? Que republique en el topico de alertas?? 
- Valores fuera de rango --> Definir
- Alertas por temperatura, vibracion o presion, etc
"""

from Shared.MongoSingleton import MongoSingleton

"""
1. Una sola consulta - traer toda la data de un parque eolico
2. Realizar calculos 

"""

class StadisticalHelper:
    def __init__(self):
        self.mongo_client = MongoSingleton.get_singleton_client()
    
    def get_raw_data(self):
        pass 
    
    
    
    
    

