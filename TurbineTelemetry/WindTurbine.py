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
        self.publish_interval = 10
        self._stop_event = threading.Event()
        self._thread = None
        
        self.noise_probability = 0.03
        
        # --- Parametros de Simulacion Realista ---
        self.capacity_mw = 2.5
        self.cut_in_speed = 3.5  # m/s
        self.rated_speed = 14.0  # m/s
        self.cut_out_speed = 25.0 # m/s
        self.max_rotor_speed = 15.0 # RPM
        
        # Estado inicial
        self.wind_speed_mps = random.uniform(3.0, 20.0)
        self.state = "operational"

    def _simulate_wind_speed(self):
        """Simula cambios mas suaves en la velocidad del viento."""
        change = random.uniform(-1.5, 1.5)
        self.wind_speed_mps += change
        self.wind_speed_mps = max(0.0, min(30.0, self.wind_speed_mps)) # Limitar entre 0 y 30 m/s
        return self.wind_speed_mps

    def get_telemetry_data(self) -> dict:
        # 1. Determinar el estado de la turbina
        states = ["operational", "maintenance", "standby", "fault", "stopped"]
        weights = [0.9, 0.03, 0.03, 0.02, 0.02]
        if self.state == "operational":
            self.state = random.choices(states, weights=weights, k=1)[0]
        else: # Si no esta operacional, hay mas chance de que vuelva a estarlo
            self.state = random.choices(states, weights=[0.6, 0.1, 0.1, 0.1, 0.1], k=1)[0]

        # 2. Simular velocidad del viento
        wind_speed = self._simulate_wind_speed()
        wind_direction_deg = random.randint(0, 359)

        # 3. Aplicar logica segun estado y viento
        active_power_kw = 0.0
        rotor_speed_rpm = 0.0
        blade_pitch_angle_deg = 90.0
        vibrations_mms = 0.0
        gear_temperature_c = 25.0
        bearing_temperature_c = 25.0
        output_voltage_v = 0.0
        generated_current_a = 0.0
        reactive_power_kvar = 0.0

        if self.state == "operational":
            # --- Logica de la Curva de Potencia ---
            if self.cut_in_speed <= wind_speed <= self.cut_out_speed:
                # Region 1: Entre cut-in y rated speed (potencia cubica)
                if wind_speed < self.rated_speed:
                    power_ratio = ((wind_speed - self.cut_in_speed) / (self.rated_speed - self.cut_in_speed)) ** 3
                    active_power_kw = self.capacity_mw * 1000 * power_ratio
                    rotor_speed_rpm = self.max_rotor_speed * (wind_speed / self.rated_speed)
                    blade_pitch_angle_deg = 2.0 # Angulo optimo para captura
                # Region 2: Entre rated y cut-out speed (potencia constante)
                else:
                    active_power_kw = self.capacity_mw * 1000
                    rotor_speed_rpm = self.max_rotor_speed # RPM constante
                    # Pitch se ajusta para mantener potencia y RPM constantes
                    pitch_adjustment = (wind_speed - self.rated_speed) * 2.5
                    blade_pitch_angle_deg = 2.0 + pitch_adjustment
            
            # Fuera de rango de operacion, potencia es 0
            else:
                active_power_kw = 0.0
                rotor_speed_rpm = 0.0
                blade_pitch_angle_deg = 90.0 # Embanderada

            # --- Simular otros valores basados en la potencia ---
            power_fraction = active_power_kw / (self.capacity_mw * 1000)
            
            # Temperaturas suben con la potencia
            gear_temperature_c = 30 + (50 * power_fraction) + random.uniform(-2, 2)
            bearing_temperature_c = 28 + (45 * power_fraction) + random.uniform(-2, 2)
            
            # Vibraciones aumentan con la velocidad del rotor
            vibrations_mms = 0.1 + (rotor_speed_rpm / self.max_rotor_speed) * 1.5 + random.uniform(-0.1, 0.1)
            
            # Electricidad
            if power_fraction > 0:
                output_voltage_v = 400.0 + random.uniform(-5, 5)
                pf = 0.95 + random.uniform(-0.02, 0.02)
                generated_current_a = (active_power_kw * 1000) / (output_voltage_v * math.sqrt(3) * pf) if output_voltage_v > 0 else 0
                reactive_power_kvar = active_power_kw * math.tan(math.acos(pf))
            
        elif self.state == "fault":
            # Simular comportamiento erratico en caso de fallo
            vibrations_mms = random.uniform(2.0, 10.0)
            gear_temperature_c = random.uniform(90, 120)
            bearing_temperature_c = random.uniform(80, 110)
            active_power_kw = random.uniform(0, 100)
            rotor_speed_rpm = random.uniform(0, 5)
            
        # Para "maintenance", "standby", "stopped", los valores se quedan en 0 o base.
        
        return {
            "farm_id": self.farm_id,
            "farm_name": f"Farm-00{self.farm_id}",
            "turbine_id": self.turbine_id,
            "turbine_name": f"T-00{self.turbine_id}",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "wind_speed_mps": round(wind_speed, 2),
            "wind_direction_deg": wind_direction_deg,
            "rotor_speed_rpm": round(rotor_speed_rpm, 2),
            "blade_pitch_angle_deg": round(blade_pitch_angle_deg, 2),
            "yaw_position_deg": wind_direction_deg, # Asumimos que el yaw se alinea con el viento
            "vibrations_mms": round(vibrations_mms, 3),
            "gear_temperature_c": round(gear_temperature_c, 2),
            "bearing_temperature_c": round(bearing_temperature_c, 2),
            "output_voltage_v": round(output_voltage_v, 1),
            "generated_current_a": round(generated_current_a, 2),
            "active_power_kw": round(active_power_kw, 2),
            "reactive_power_kvar": round(reactive_power_kvar, 2),
            "operational_state": self.state,
            "capacity_mw": self.capacity_mw
        }
            
    def make_telemetry_noisy(self, raw_payload: dict) -> dict:
        fail_choices = [None, -9999, 999999.9]
        raw_payload["wind_speed_mps"] = random.choice(fail_choices)
        raw_payload["rotor_speed_rpm"] = random.choice(fail_choices)
        raw_payload["bearing_temperature_c"] = random.choice(fail_choices)
        return raw_payload

    def start(self):
        lwt_payload = {
            "farm_id": self.farm_id,
            "farm_name": f"Farm-00{self.farm_id}",
            "turbine_id": self.turbine_id,
            "turbine_name": f"T-00{self.turbine_id}",
            "state": "offline"   
        }
        self.mqtt_client.set_lwt(self.status_topic, lwt_payload, qos=1, retain=True)
        self.mqtt_client.connect()
       
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
            
            self.mqtt_client.publish(self.telemetry_topic, data, qos=0, retain=False)
            self._stop_event.wait(self.publish_interval)

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        self.mqtt_client.clear_retained(self.status_topic)
        self.mqtt_client.disconnect()