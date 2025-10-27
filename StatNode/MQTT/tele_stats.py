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

from typing import Dict, List
from Shared.MongoSingleton import MongoSingleton

"""
1. Una sola consulta - traer toda la data de un parque eolico
2. Realizar calculos 

"""

class StadisticalHelper:
    def __init__(self):
        self.mongo_client = MongoSingleton.get_singleton_client()
    
    def get_stats_turbine(self, turbine_id: str, minutes: int = 5, fields: List[str] = ("wind_speed_mps",)) -> Dict[str, Any]:
        return self.db.get_window_stats(turbine_id=turbine_id, minutes=minutes, fields=list(fields))

    def get_stats_farm(self, farm_id: str, minutes: int = 5, fields: List[str] = ("wind_speed_mps",)) -> Dict[str, Any]:
        return self.db.get_window_stats_for_farm(farm_id=farm_id, minutes=minutes, fields=list(fields))
    
    
    
    
    
    

