import random
import threading
import time

from Shared.GenericMQTTClient import GenericMQTTClient


# TOPIC_TELEMETRY = "farms/{farm_id}/turbines/+/raw_telemetry"  
#TOPIC_TELEMETRY = "farms/1/turbines/+/raw_telemetry" # Para pruebas
TOPIC_STATUS = "farm/turbine/status"

class WindTurbine:
    def __init__(self, farm_id: int, turbine_id: int):
        self.turbine_id = turbine_id
        self.farm_id = farm_id
        
        self.telemetry_topic = f"farms/{farm_id}/turbines/{turbine_id}/raw_telemetry"
        # self.status_topic = TOPIC_STATUS
        
        # cliente mqtt con id unico
        str_turbine_id = f"T-00{self.turbine_id}" # T-001, T-002, etc 
        self.mqtt_client = GenericMQTTClient(client_id=str_turbine_id) 
        self.publish_interval = 5 # segundos
        self._stop_event = threading.Event()
        self._thread = None

    #LAS VARIABLES COMENTADAS NO ESTAN IMPLEMENTADAS EN EL FRONTEND
    def get_telemetry_data(self)->dict:
        '''Telemetria adaptada al frontend'''
        #Estado de turbina
        # Estados del molino y sus probabilidades
        states = ["operational","maintenance", "standby", "fault","stopped"]
        probability = [0.8, 0.1, 0.05, 0.05]  # deben sumar 1
        # Selección ponderada
        state = random.choices(states, weights=probability, k=1)[0]
        is_active = state == "operational"
        wind_speed = 8 + random.random() * 10
        active_power = (wind_speed / 18) * 2.5 * (0.7 + random.random() * 0.3) if is_active else 0

        turbina = {
            "id": f"T-{str(self.turbine_id).zfill(3)}",
            "name": f"Turbina {self.turbine_id}",
            #"farm_name": f"Farm-00{self.farm_id}",
            #"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": state,
            "capacity": 2.5,  # MW


            "environmental": {
                "windSpeed": wind_speed,
                "windDirection": random.randint(0, 359),
                #"atmospheric_pressure_hpa": round(random.uniform(980, 1030), 1),
                #"ambience_temperature": random.randint(-10, 20)     
            },

            "mechanical": {
                "rotorSpeed": 10 + random.random() * 8 if is_active else 0,
                "pitchAngle": 5 + random.random() * 10 if is_active else 90,
                "yawPosition": random.randint(0, 359),
                "vibration": 0.5 + random.random() * 1.5 if is_active else 0,
                "gearboxTemperature": 50 + random.random() * 20 if is_active else 25,
                "bearingTemperature": 45 + random.random() * 15 if is_active else 25,
                "oilPressure": 2.5 + random.random() * 1.5 if is_active else 0,
                "oilLevel": 80 + random.random() * 15,
            },

            "electrical": {
                "outputVoltage": 690 + random.random() * 10 if is_active else 0,
                "activePower": active_power * 1000,  # kW
                "outputCurrent": (active_power * 1000) / (690 * math.sqrt(3) * 0.95) if is_active else 0,
                "reactivePower": active_power * 1000 * 0.3 if is_active else 0,
                "powerFactor": round(math.cos(math.atan((active_power * 1000 * 0.3) / (active_power * 1000))), 4) if is_active else 0,#calcula el factor de potencia
                #"output_frequency_hz": round(random.uniform(49.5, 50.5), 2),
            },

            "lastMaintenance": "2025-09-15",
            "nextMaintenance": "2025-12-15",
            "operatingHours": 12500 + random.randint(0, 1999),
        }
        return turbina
    
    # def get_telemetry_data(self) -> dict:

    

    #     # Genera datos de turbina 
    #     return {
    #         # Datos identificacion 
    #         "farm_id": self.farm_id,
    #         "farm_name": f"Farm-00{self.farm_id}",
    #         "turbine_id": self.turbine_id,
    #         "turbine_name": f"T-00{self.turbine_id}",

    #         "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    #         # Variables entorno
    #         "wind_speed_mps": round(random.uniform(3.0, 25.0), 2),
    #         "wind_direction_deg": random.randint(0, 360),
    #         "ambience_temperature": random.randint(-10, 20),
    #         "atmospheric_pressure_hpa": round(random.uniform(980, 1030), 1),
    #         # Variables mecanicas 
    #         "rotor_speed_rpm": round(random.uniform(10, 20), 2),
    #         "blade_pitch_angle_deg": round(random.uniform(0, 30), 1),
    #         "yaw_position_deg": round(random.uniform(0.0, 360.0), 2),              # grados
    #         "vibrations_mms": round(random.uniform(0.1, 5.0), 2),                  # mm/s
    #         "gear_temperature_c": round(random.uniform(30.0, 90.0), 1),           # °C
    #         "bearing_temperature_c": round(random.uniform(25.0, 80.0), 1),        # °C
    #         "oil_pressure_bar": round(random.uniform(1.0, 10.0), 2),              # bar
    #         "oil_level_percent": round(random.uniform(20.0, 100.0), 1),
    #         # Variables electricas
    #         "output_voltage_v": round(random.uniform(380.0, 420.0), 1),           # Voltaje de salida en V
    #         "generated_current_a": round(random.uniform(10.0, 200.0), 2),         # Corriente generada en A
    #         "active_power_kw": round(random.uniform(50.0, 500.0), 2),             # Potencia activa en kW
    #         "reactive_power_kvar": round(random.uniform(10.0, 300.0), 2),         # Potencia reactiva en kVAR
    #         "output_frequency_hz": round(random.uniform(49.5, 50.5), 2),
    #         # Estado del sistema 
    #         "operational_state": "active" # por ahora siempre activo
    #         #"operational_state": random.choice(["active", "stopped", "fault", "maintenance"])
    #     }
        
        

    def start(self):
        """
        1. Configuracion LWT 
        2. Conecta del mqqt client 
        3. loop envio de telemetría 
        """
        # En caso de caida de la turbina
        lwt_payload = {"turbine_id": self.turbine_id, "state": "offline"}
        self.mqtt_client.set_lwt(TOPIC_STATUS, lwt_payload, qos=1, retain=True)

        self.mqtt_client.connect()
       
        # arrancar hilo que publica telemetría
        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._send_telemetry, daemon=True)
            self._thread.start()

    def _send_telemetry(self):
        while not self._stop_event.is_set():
            data: dict = self.get_telemetry_data()
            # el payload lo crea la entidad; el cliente solo publica en el topic que se le pasa
            # conversion data a JSON lo hace mqtt_client 
            self.mqtt_client.publish(self.telemetry_topic, data, qos=0, retain=False)
            self._stop_event.wait(self.publish_interval)

    def stop(self):
        """Detiene el hilo, limpia retained status y desconecta (todo desde la entidad)."""
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        # limpiar retained status 
        self.mqtt_client.clear_retained(TOPIC_STATUS)
        self.mqtt_client.disconnect()