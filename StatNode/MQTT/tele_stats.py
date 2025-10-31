from datetime import datetime, timedelta
import time

from StatNode.DB.TelemetryDB import TelemetryDB

class StatisticalHelper:
    def __init__(self):
        self.db_service = TelemetryDB()

    def get_stadistics(self):
        metrics_per_turbine = self.get_metrics_per_turbine(
            farm_id=1,
            minutes=5,
            rotor_radius_m=40.0  # radio constante
        )

        print(f"Metricas por turbina: {metrics_per_turbine}\n")

        metrics_farm = self.get_metrics_aggregate(
            farm_id=1,
            minutes=5,
            rotor_radius_m=40.0  # radio constante
        )
        
        print(f"Metricas por farm-{1}: {metrics_per_turbine}\n")


        
if __name__ == '__main__':
    helper = StatisticalHelper()
    for i in range(0, 3): 
        helper.get_stadistics()
        time.sleep(10)
        
    print("MAIN estadisticas finalizado!")

"""
# Metrics per turbine (una sola consulta para todo el farm_id=1)
per_turb = db.get_metrics_per_turbine(farm_id=1, minutes=5, rotor_radius_m=40.0)
print(per_turb[10]["avg_wind"], per_turb[10]["energy_kwh"])

# Aggregated farm metrics (una sola consulta)
agg = db.get_metrics_aggregate(farm_id=1, minutes=5, rotor_radius_m=40.0)
print(agg["avg_wind"], agg["energy_kwh"])

radios constantes
db.get_metrics_per_turbine(
    farm_id=1,
    minutes=5,
    rotor_radius_m=40.0  # <-- radio constante
)

"""
