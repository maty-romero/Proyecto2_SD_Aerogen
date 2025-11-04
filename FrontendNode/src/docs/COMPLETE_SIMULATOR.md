# Simulador Completo - Turbinas, Estadísticas y Alertas

Este simulador completo genera:
- 📊 Mediciones de turbinas individuales
- 📈 Estadísticas del parque (producción)
- 🚨 Alertas en tiempo real

## Simulador Python Completo

### Instalación

```bash
pip install paho-mqtt
```

### Código Completo

Crea un archivo `complete_simulator.py`:

```python
import paho.mqtt.client as mqtt
import json
import time
import random
import uuid
from datetime import datetime, timedelta

BROKER_URL = "localhost"
BROKER_PORT = 1883
FARM_ID = 1
FARM_NAME = "Comodoro Rivadavia"
TURBINE_COUNT = 24
UPDATE_INTERVAL = 5  # segundos

class TurbineSimulator:
    def __init__(self, farm_id, turbine_id):
        self.farm_id = farm_id
        self.turbine_id = turbine_id
        self.farm_name = f"Farm-{farm_id:03d}"
        self.turbine_name = f"T-{turbine_id:03d}"
        self.capacity_mw = 2.5
        
        # Estado inicial
        self.operational_state = random.choice(['operational', 'operational', 'operational', 'standby'])
        self.base_wind_speed = 8 + random.random() * 10
        self.base_wind_direction = random.randint(0, 359)
    
    def generate_data(self):
        """Genera datos en formato plano (single-level JSON)"""
        is_active = self.operational_state == 'operational'
        
        # Variables ambientales
        wind_speed_mps = self.base_wind_speed + (random.random() - 0.5) * 2
        wind_direction_deg = int((self.base_wind_direction + (random.random() - 0.5) * 10) % 360)
        
        # Variables mecánicas
        rotor_speed_rpm = round(10 + random.random() * 8, 2) if is_active else 0
        blade_pitch_angle_deg = round(5 + random.random() * 10, 2) if is_active else 90
        yaw_position_deg = wind_direction_deg
        vibrations_mms = round(0.5 + random.random() * 1.5, 2) if is_active else 0
        gear_temperature_c = round(50 + random.random() * 20, 1) if is_active else 25
        bearing_temperature_c = round(45 + random.random() * 15, 1) if is_active else 25
        
        # Variables eléctricas
        active_power_kw = 0
        if is_active:
            active_power_kw = max(0, min(2500, (wind_speed_mps - 3) * 250 + random.random() * 200))
        
        output_voltage_v = round(690 + random.random() * 10, 1) if is_active else 0
        generated_current_a = round(active_power_kw * 1000 / (690 * 1.732 * 0.95), 1) if is_active else 0
        reactive_power_kvar = round(active_power_kw * 0.3, 2) if is_active else 0
        
        return {
            # Identificacion
            "farm_id": self.farm_id,
            "farm_name": self.farm_name,
            "turbine_id": self.turbine_id,
            "turbine_name": self.turbine_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            
            # Variables
            "wind_speed_mps": round(wind_speed_mps, 2),
            "wind_direction_deg": wind_direction_deg,
            "rotor_speed_rpm": rotor_speed_rpm,
            "blade_pitch_angle_deg": blade_pitch_angle_deg,
            "yaw_position_deg": yaw_position_deg,
            "vibrations_mms": vibrations_mms,
            "gear_temperature_c": gear_temperature_c,
            "bearing_temperature_c": bearing_temperature_c,
            "output_voltage_v": output_voltage_v,
            "generated_current_a": generated_current_a,
            "active_power_kw": round(active_power_kw, 1),
            "reactive_power_kvar": reactive_power_kvar,
            
            # Estado
            "operational_state": self.operational_state,
            
            # Info extra
            "capacity_mw": self.capacity_mw
        }

class WindFarmSimulator:
    def __init__(self):
        self.client = mqtt.Client("windfarm-complete-simulator")
        self.turbines = []
        self.hourly_history = []
        self.init_turbines()
        self.init_hourly_history()
    
    def init_turbines(self):
        """Inicializar todas las turbinas"""
        for i in range(1, TURBINE_COUNT + 1):
            turbine = TurbineSimulator(FARM_ID, i)
            self.turbines.append(turbine)
    
    def init_hourly_history(self):
        """Inicializar histórico de 24 horas"""
        now = datetime.now()
        for i in range(24):
            hour = (now - timedelta(hours=23-i)).strftime("%H:00")
            production = 35000 + random.random() * 15000
            self.hourly_history.append({
                "hour": hour,
                "production": round(production, 0)
            })
    
    def update_hourly_history(self, current_power):
        """Actualizar histórico cada hora"""
        # Eliminar el más antiguo y agregar el actual
        self.hourly_history.pop(0)
        current_hour = datetime.now().strftime("%H:00")
        self.hourly_history.append({
            "hour": current_hour,
            "production": round(current_power, 0)
        })
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("✅ Conectado al broker MQTT")
            print("📡 Iniciando simulación completa...\n")
        else:
            print(f"❌ Error de conexión: {rc}")
    
    def publish_turbine_measurements(self):
        """Publicar mediciones de todas las turbinas"""
        print("📊 Publicando mediciones de turbinas...")
        for turbine in self.turbines:
            data = turbine.generate_data()
            topic = f"windfarm/turbines/{turbine.turbine_id}/measurements"
            self.client.publish(topic, json.dumps(data), qos=1)
    
    def publish_farm_stats(self):
        """Publicar estadísticas del parque"""
        # Calcular estadísticas agregadas
        total_power = 0
        total_reactive = 0
        operational_count = 0
        stopped_count = 0
        maintenance_count = 0
        fault_count = 0
        
        wind_speeds = []
        power_factors = []
        voltages = []
        wind_directions = []
        
        for turbine in self.turbines:
            data = turbine.generate_data()
            
            # Contadores
            if data['operational_state'] == 'operational':
                operational_count += 1
                total_power += data['active_power_kw']
                total_reactive += data['reactive_power_kvar']
                
                # Promedios
                wind_speeds.append(data['wind_speed_mps'])
                wind_directions.append(data['wind_direction_deg'])
                voltages.append(data['output_voltage_v'])
                
                # Power factor
                apparent = (data['active_power_kw']**2 + data['reactive_power_kvar']**2)**0.5
                if apparent > 0:
                    pf = data['active_power_kw'] / apparent
                    power_factors.append(pf)
            
            elif data['operational_state'] == 'stopped':
                stopped_count += 1
            elif data['operational_state'] == 'maintenance':
                maintenance_count += 1
            elif data['operational_state'] == 'fault':
                fault_count += 1
        
        # Calcular promedios
        avg_wind = sum(wind_speeds) / len(wind_speeds) if wind_speeds else 0
        max_wind = max(wind_speeds) if wind_speeds else 0
        min_wind = min(wind_speeds) if wind_speeds else 0
        avg_pf = sum(power_factors) / len(power_factors) if power_factors else 0
        avg_voltage = sum(voltages) / len(voltages) if voltages else 0
        
        # Dirección predominante (promedio circular simplificado)
        predominant_dir = int(sum(wind_directions) / len(wind_directions)) if wind_directions else 0
        
        stats = {
            "farm_id": FARM_ID,
            "farm_name": FARM_NAME,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            
            "total_active_power_kw": round(total_power, 1),
            "total_reactive_power_kvar": round(total_reactive, 1),
            
            "total_turbines": TURBINE_COUNT,
            "operational_turbines": operational_count,
            "stopped_turbines": stopped_count,
            "maintenance_turbines": maintenance_count,
            "fault_turbines": fault_count,
            
            "avg_wind_speed_mps": round(avg_wind, 2),
            "max_wind_speed_mps": round(max_wind, 2),
            "min_wind_speed_mps": round(min_wind, 2),
            "predominant_wind_direction_deg": predominant_dir,
            
            "avg_power_factor": round(avg_pf, 3),
            "avg_voltage_v": round(avg_voltage, 1),
            
            "hourly_production_kwh": [h["production"] for h in self.hourly_history],
            "hourly_timestamps": [h["hour"] for h in self.hourly_history]
        }
        
        self.client.publish("windfarm/stats", json.dumps(stats), qos=1)
        
        print(f"📈 Estadísticas: {stats['total_active_power_kw']:.0f} kW | "
              f"{operational_count}/{TURBINE_COUNT} operativas | "
              f"Viento: {avg_wind:.1f} m/s")
    
    def generate_random_alert(self):
        """Generar alerta aleatoria"""
        turbine = random.choice(self.turbines)
        
        alert_templates = [
            {
                "type": "mechanical",
                "severity": "warning",
                "message": "Temperatura del engranaje elevada",
                "details": f"Temp. actual: {random.randint(70, 80)}°C (límite: 70°C)"
            },
            {
                "type": "mechanical",
                "severity": "warning",
                "message": "Vibración elevada detectada",
                "details": f"Vibración: {random.uniform(2.5, 3.5):.1f} mm/s (límite: 2.5 mm/s)"
            },
            {
                "type": "electrical",
                "severity": "critical",
                "message": "Voltaje fuera de rango",
                "details": f"Voltaje: {random.randint(650, 670)}V (rango: 680-700V)"
            },
            {
                "type": "environmental",
                "severity": "info",
                "message": "Velocidad de viento por encima del promedio",
                "details": f"Viento: {random.uniform(16, 20):.1f} m/s"
            },
            {
                "type": "system",
                "severity": "info",
                "message": "Calibración de sensores completada",
                "details": "Anemómetro y veleta recalibrados exitosamente"
            }
        ]
        
        template = random.choice(alert_templates)
        
        alert = {
            "alert_id": f"ALT-{int(time.time())}{uuid.uuid4().hex[:8]}",
            "farm_id": FARM_ID,
            "turbine_id": turbine.turbine_id,
            "turbine_name": turbine.turbine_name,
            "alert_type": template["type"],
            "severity": template["severity"],
            "message": template["message"],
            "details": template["details"],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "acknowledged": False,
            "resolved": False
        }
        
        self.client.publish("windfarm/alerts", json.dumps(alert), qos=1)
        
        severity_icon = {
            "critical": "🔴",
            "warning": "🟡",
            "info": "🔵"
        }
        
        print(f"{severity_icon[alert['severity']]} Alerta [{alert['severity'].upper()}]: "
              f"{alert['turbine_name']} - {alert['message']}")
    
    def change_random_state(self):
        """Cambiar estado aleatorio de una turbina"""
        turbine = random.choice(self.turbines)
        states = ['operational', 'operational', 'operational', 'standby', 'maintenance']
        new_state = random.choice(states)
        
        if turbine.operational_state != new_state:
            old_state = turbine.operational_state
            turbine.operational_state = new_state
            print(f"🔄 {turbine.turbine_name}: {old_state} → {new_state}")
    
    def run(self):
        """Ejecutar simulador"""
        self.client.on_connect = self.on_connect
        self.client.connect(BROKER_URL, BROKER_PORT, 60)
        self.client.loop_start()
        
        cycle_count = 0
        last_hour = datetime.now().hour
        
        try:
            while True:
                print(f"\n{'='*60}")
                print(f"Ciclo #{cycle_count + 1} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print('='*60)
                
                # Publicar mediciones de turbinas
                self.publish_turbine_measurements()
                
                # Publicar estadísticas del parque
                self.publish_farm_stats()
                
                # Generar alerta aleatoria (30% probabilidad)
                if random.random() > 0.7:
                    self.generate_random_alert()
                
                # Cambiar estado de turbina cada 6 ciclos (~30 seg si UPDATE_INTERVAL=5)
                if cycle_count % 6 == 0:
                    self.change_random_state()
                
                # Actualizar histórico cada hora
                current_hour = datetime.now().hour
                if current_hour != last_hour:
                    # Calcular potencia actual
                    total_power = sum(
                        t.generate_data()['active_power_kw'] 
                        for t in self.turbines 
                        if t.operational_state == 'operational'
                    )
                    self.update_hourly_history(total_power)
                    last_hour = current_hour
                    print(f"⏰ Histórico actualizado - Nueva hora: {current_hour:02d}:00")
                
                cycle_count += 1
                time.sleep(UPDATE_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n\n👋 Cerrando simulador...")
            self.client.loop_stop()
            self.client.disconnect()

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Simulador Completo de Parque Eólico")
    print("=" * 60)
    print(f"📍 Broker: {BROKER_URL}:{BROKER_PORT}")
    print(f"🏭 Parque: {FARM_NAME}")
    print(f"⚡ Turbinas: {TURBINE_COUNT}")
    print(f"⏱️  Intervalo: {UPDATE_INTERVAL} segundos")
    print("=" * 60)
    print("\nTópicos publicados:")
    print("  • windfarm/turbines/{id}/measurements - Mediciones individuales")
    print("  • windfarm/stats - Estadísticas del parque")
    print("  • windfarm/alerts - Alertas en tiempo real")
    print("=" * 60)
    
    simulator = WindFarmSimulator()
    simulator.run()
```

### Ejecutar

```bash
python complete_simulator.py
```

### Salida Esperada

```
============================================================
🚀 Simulador Completo de Parque Eólico
============================================================
📍 Broker: localhost:1883
🏭 Parque: Comodoro Rivadavia
⚡ Turbinas: 24
⏱️  Intervalo: 5 segundos
============================================================

Tópicos publicados:
  • windfarm/turbines/{id}/measurements - Mediciones individuales
  • windfarm/stats - Estadísticas del parque
  • windfarm/alerts - Alertas en tiempo real
============================================================
✅ Conectado al broker MQTT
📡 Iniciando simulación completa...

============================================================
Ciclo #1 - 2025-11-03 15:30:45
============================================================
📊 Publicando mediciones de turbinas...
📈 Estadísticas: 45250 kW | 22/24 operativas | Viento: 11.3 m/s
🟡 Alerta [WARNING]: T-007 - Temperatura del engranaje elevada

============================================================
Ciclo #2 - 2025-11-03 15:30:50
============================================================
📊 Publicando mediciones de turbinas...
📈 Estadísticas: 45180 kW | 22/24 operativas | Viento: 11.4 m/s
🔄 T-012: operational → maintenance

...
```

## Simulador Node.js Completo

### Instalación

```bash
npm install mqtt
```

### Código

Similar estructura en JavaScript - contactar para implementación completa.

## Características del Simulador

### ✅ Mediciones de Turbinas
- Publicación individual por turbina
- Formato JSON plano
- Datos realistas según estado

### ✅ Estadísticas del Parque
- Agregación de todas las turbinas
- Contadores por estado
- Promedios eléctricos y de viento
- Histórico de 24 horas actualizado

### ✅ Alertas Aleatorias
- Generación probabilística (30%)
- Múltiples tipos y severidades
- Detalles técnicos incluidos

### ✅ Cambios de Estado
- Transiciones realistas
- Periodicidad configurable

## Integración con Frontend

Una vez ejecutando el simulador:

1. **Iniciar EMQX**:
   ```bash
   docker run -d --name emqx -p 1883:1883 -p 8083:8083 -p 18083:18083 emqx/emqx:latest
   ```

2. **Ejecutar simulador**:
   ```bash
   python complete_simulator.py
   ```

3. **Abrir frontend** y conectar a `ws://localhost:8083/mqtt`

4. **Ver datos en tiempo real**:
   - Turbinas actualizándose
   - Gráficos de producción con datos reales
   - Alertas apareciendo en el panel

---

**Última actualización**: 2025-11-03  
**Versión**: 1.0.0
