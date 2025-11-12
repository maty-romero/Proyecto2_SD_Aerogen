import math
import random
import threading
import time

from Shared.GenericMQTTClient import GenericMQTTClient

TOPIC_RAW_TELEMETRY = "farms/{farm_id}/turbines/{turbine_id}/raw_telemetry"  
TOPIC_STATUS = "farms/{farm_id}/turbines/{turbine_id}/status"

class WindTurbine:
    def __init__(self, farm_id: int, turbine_id: int):
        self.turbine_id = turbine_id
        self.farm_id = farm_id

        self.telemetry_topic = TOPIC_RAW_TELEMETRY.format(farm_id=farm_id, turbine_id=turbine_id)
        self.status_topic = TOPIC_STATUS.format(farm_id=farm_id, turbine_id=turbine_id)
        
        # cliente mqtt con id unico
        str_turbine_id = f"WF-{farm_id}-T-{turbine_id}" 
        
        self.mqtt_client = GenericMQTTClient(client_id=str_turbine_id) 
        self.publish_interval = 10 # segundos
        self._stop_event = threading.Event()
        self._thread = None
        
        self.noise_probability = 0.05  # 3% de los mensajes seran ruidosos

    def get_telemetry_data(self) -> dict:
        capacity_mw: float = 2.5
        
        states = ["operational", "maintenance", "standby", "fault", "stopped"]
        weights = [0.8, 0.08, 0.06, 0.03, 0.03]
        state = random.choices(states, weights=weights, k=1)[0]
        is_active = state == "operational"

        # Entorno
        wind_speed_mps = round(3.0 + random.random() * 22.0, 2) if is_active else round(random.uniform(0.0, 6.0), 2)
        wind_direction_deg = random.randint(0, 359)

        # Mecánicas
        rotor_speed_rpm = round(10 + random.random() * 20, 2) if is_active else 0.0
        blade_pitch_angle_deg = round(random.uniform(0, 30), 2) if is_active else 90.0
        yaw_position_deg = round(random.uniform(0, 360), 2)
        vibrations_mms = round(random.uniform(0.1, 5.0), 2) if is_active else 0.0
        gear_temperature_c = round(40 + random.random() * 30, 1) if is_active else round(25 + random.random() * 5, 1)
        bearing_temperature_c = round(35 + random.random() * 30, 1) if is_active else round(25 + random.random() * 5, 1)

        # Eléctricas
        capacity_kw = capacity_mw * 1000
        p_frac = min(max(wind_speed_mps / 25.0, 0.0), 1.0) if is_active else 0.0
        p_factor = 0.6 + random.random() * 0.4
        active_power_kw = round(capacity_kw * p_frac * p_factor, 2) if is_active else 0.0

        pf = 0.95 if is_active else 0.0
        output_voltage_v = 400.0 if is_active else 0.0
        generated_current_a = round(
            (active_power_kw * 1000) / (output_voltage_v * math.sqrt(3) * pf),
            2
        ) if (is_active and output_voltage_v and pf) else 0.0

        reactive_power_kvar = round(active_power_kw * 0.3, 2) if is_active else 0.0

        return {
            # Identificacion
            "farm_id": self.farm_id,
            "farm_name": f"Farm-00{self.farm_id}",
            "turbine_id": self.turbine_id,
            "turbine_name": f"T-00{self.turbine_id}",

            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),

            # Variables
            "wind_speed_mps": wind_speed_mps,
            "wind_direction_deg": wind_direction_deg,
            "rotor_speed_rpm": rotor_speed_rpm,
            "blade_pitch_angle_deg": blade_pitch_angle_deg,
            "yaw_position_deg": yaw_position_deg,
            "vibrations_mms": vibrations_mms,
            "gear_temperature_c": gear_temperature_c,
            "bearing_temperature_c": bearing_temperature_c,
            "output_voltage_v": round(output_voltage_v, 1),
            "generated_current_a": generated_current_a,
            "active_power_kw": active_power_kw,
            "reactive_power_kvar": reactive_power_kvar,

            # Estado
            "operational_state": state,

            # Info extra
            "capacity_mw": capacity_mw
        }
            
    # Introduce ruido en los datos de telemetría para simular fallos
    def make_telemetry_noisy(self, raw_payload: dict) -> dict:
        # partimos del payload sin ruido
        fail_choices = [
            None,
            -9999,     # fuera rango negativo
            999999.9   # fuera rango positivo
        ]
        # Forzamos que *todos* fallen (estricto)
        raw_payload["wind_speed_mps"] = random.choice(fail_choices)
        raw_payload["rotor_speed_rpm"] = random.choice(fail_choices)
        raw_payload["bearing_temperature_c"] = random.choice(fail_choices)
        
        return raw_payload



    def start(self):
        """
        1. Configuracion LWT 
        2. Conecta del mqqt client 
        3. loop envio de telemetría 
        """
        # En caso de caida de la turbina
        lwt_payload = {
            "farm_id": self.farm_id,
            "farm_name": f"Farm-00{self.farm_id}",
            "turbine_id": self.turbine_id,
            "turbine_name": f"T-00{self.turbine_id}",
            "state": "offline"   
        }
        self.mqtt_client.set_lwt(self.status_topic, lwt_payload, qos=1, retain=True)

        self.mqtt_client.connect()
       
        # arrancar hilo que publica telemetría
        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._send_telemetry, daemon=True)
            self._thread.start()

    def _send_telemetry(self):
        while not self._stop_event.is_set():
            data: dict = self.get_telemetry_data()

            if random.random() < self.noise_probability:
                data = self.make_telemetry_noisy(data)
                print(f"\n**** [WARN] Enviando telemetría con ruido para turbina {data['turbine_id']}\n")
            
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
        self.mqtt_client.clear_retained(self.status_topic)
        self.mqtt_client.disconnect()