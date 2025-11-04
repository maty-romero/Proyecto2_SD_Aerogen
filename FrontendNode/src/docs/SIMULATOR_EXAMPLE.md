# Simulador de Backend MQTT

Este documento contiene ejemplos de código para simular un backend que publica datos en EMQX usando el **formato plano (single-level JSON)** que coincide con el formato del molino.

## Formato de Datos

El sistema espera recibir datos en formato JSON plano con los siguientes campos:

```json
{
  "farm_id": 1,
  "farm_name": "Farm-001",
  "turbine_id": 5,
  "turbine_name": "T-005",
  "timestamp": "2025-11-02 14:30:15",
  
  "wind_speed_mps": 12.5,
  "wind_direction_deg": 245,
  
  "rotor_speed_rpm": 15.3,
  "blade_pitch_angle_deg": 8.2,
  "yaw_position_deg": 245,
  "vibrations_mms": 1.2,
  "gear_temperature_c": 62.5,
  "bearing_temperature_c": 55.8,
  
  "output_voltage_v": 695.2,
  "generated_current_a": 1250.5,
  "active_power_kw": 2150.0,
  "reactive_power_kvar": 645.0,
  
  "operational_state": "operational",
  
  "capacity_mw": 2.5
}
```

## Simulador en Python

### Instalación

```bash
pip install paho-mqtt
```

### Código del Simulador

Crea un archivo `simulator.py`:

```python
import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime
import math

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
        self.farm_name = f"Farm-00{farm_id}"
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
        self.client = mqtt.Client("windfarm-simulator")
        self.turbines = []
        self.init_turbines()
    
    def init_turbines(self):
        for i in range(1, TURBINE_COUNT + 1):
            turbine = TurbineSimulator(FARM_ID, i)
            self.turbines.append(turbine)
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("✅ Conectado al broker MQTT")
            print("📡 Iniciando simulación...\n")
        else:
            print(f"❌ Error de conexión: {rc}")
    
    def publish_measurements(self):
        """Publica mediciones de todas las turbinas"""
        total_power = 0
        active_count = 0
        
        for turbine in self.turbines:
            data = turbine.generate_data()
            topic = f"windfarm/turbines/{turbine.turbine_id}/measurements"
            
            self.client.publish(topic, json.dumps(data), qos=1)
            
            if data['operational_state'] == 'operational':
                total_power += data['active_power_kw']
                active_count += 1
            
            print(f"📊 {data['turbine_name']}: {data['active_power_kw']:.0f} kW - {data['operational_state']}")
        
        print(f"\n🌍 Total: {total_power:.0f} kW | {active_count}/{len(self.turbines)} operativas\n")
        print("-" * 50)
    
    def change_random_state(self):
        """Cambia aleatoriamente el estado de una turbina"""
        turbine = random.choice(self.turbines)
        states = ['operational', 'operational', 'operational', 'standby', 'maintenance']
        new_state = random.choice(states)
        
        if turbine.operational_state != new_state:
            old_state = turbine.operational_state
            turbine.operational_state = new_state
            print(f"🔄 {turbine.turbine_name}: {old_state} → {new_state}\n")
    
    def run(self):
        self.client.on_connect = self.on_connect
        self.client.connect(BROKER_URL, BROKER_PORT, 60)
        
        # Loop en background
        self.client.loop_start()
        
        cycle_count = 0
        
        try:
            while True:
                self.publish_measurements()
                
                # Cambiar estado cada 6 ciclos (~30 segundos si UPDATE_INTERVAL=5)
                if cycle_count % 6 == 0:
                    self.change_random_state()
                
                cycle_count += 1
                time.sleep(UPDATE_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n👋 Cerrando simulador...")
            self.client.loop_stop()
            self.client.disconnect()

if __name__ == "__main__":
    print("🚀 Simulador de Parque Eólico - Formato Plano")
    print(f"📍 Broker: {BROKER_URL}:{BROKER_PORT}")
    print(f"🏭 Parque: {FARM_NAME}")
    print(f"⚡ Turbinas: {TURBINE_COUNT}")
    print(f"⏱️  Intervalo: {UPDATE_INTERVAL} segundos")
    print("=" * 50)
    
    simulator = WindFarmSimulator()
    simulator.run()
```

### Ejecutar

```bash
python simulator.py
```

### Salida Esperada

```
🚀 Simulador de Parque Eólico - Formato Plano
📍 Broker: localhost:1883
🏭 Parque: Comodoro Rivadavia
⚡ Turbinas: 24
⏱️  Intervalo: 5 segundos
==================================================
✅ Conectado al broker MQTT
📡 Iniciando simulación...

📊 T-001: 2150 kW - operational
📊 T-002: 1850 kW - operational
📊 T-003: 0 kW - standby
📊 T-004: 2300 kW - operational
...

🌍 Total: 42500 kW | 22/24 operativas

--------------------------------------------------
🔄 T-007: operational → maintenance

📊 T-001: 2180 kW - operational
...
```

## Simulador en Node.js

### Instalación

```bash
mkdir mqtt-simulator
cd mqtt-simulator
npm init -y
npm install mqtt
```

### Código del Simulador

Crea un archivo `simulator.js`:

```javascript
const mqtt = require('mqtt');

// Configuración
const BROKER_URL = 'mqtt://localhost:1883';
const FARM_ID = 1;
const FARM_NAME = 'Comodoro Rivadavia';
const TURBINE_COUNT = 24;
const UPDATE_INTERVAL = 5000; // 5 segundos

class TurbineSimulator {
  constructor(farmId, turbineId) {
    this.farmId = farmId;
    this.turbineId = turbineId;
    this.farmName = `Farm-00${farmId}`;
    this.turbineName = `T-${String(turbineId).padStart(3, '0')}`;
    this.capacityMw = 2.5;
    
    // Estado inicial
    this.operationalState = Math.random() > 0.2 ? 'operational' : 'standby';
    this.baseWindSpeed = 8 + Math.random() * 10;
    this.baseWindDirection = Math.floor(Math.random() * 360);
  }
  
  generateData() {
    const isActive = this.operationalState === 'operational';
    
    // Variables ambientales
    const windSpeedMps = this.baseWindSpeed + (Math.random() - 0.5) * 2;
    const windDirectionDeg = Math.floor((this.baseWindDirection + (Math.random() - 0.5) * 10 + 360) % 360);
    
    // Variables mecánicas
    const rotorSpeedRpm = isActive ? parseFloat((10 + Math.random() * 8).toFixed(2)) : 0;
    const bladePitchAngleDeg = isActive ? parseFloat((5 + Math.random() * 10).toFixed(2)) : 90;
    const yawPositionDeg = windDirectionDeg;
    const vibrationsMms = isActive ? parseFloat((0.5 + Math.random() * 1.5).toFixed(2)) : 0;
    const gearTemperatureC = isActive ? parseFloat((50 + Math.random() * 20).toFixed(1)) : 25;
    const bearingTemperatureC = isActive ? parseFloat((45 + Math.random() * 15).toFixed(1)) : 25;
    
    // Variables eléctricas
    let activePowerKw = 0;
    if (isActive) {
      activePowerKw = Math.max(0, Math.min(2500, (windSpeedMps - 3) * 250 + Math.random() * 200));
    }
    
    const outputVoltageV = isActive ? parseFloat((690 + Math.random() * 10).toFixed(1)) : 0;
    const generatedCurrentA = isActive ? parseFloat((activePowerKw * 1000 / (690 * Math.sqrt(3) * 0.95)).toFixed(1)) : 0;
    const reactivePowerKvar = isActive ? parseFloat((activePowerKw * 0.3).toFixed(2)) : 0;
    
    const now = new Date();
    const timestamp = now.toISOString().replace('T', ' ').substring(0, 19);
    
    return {
      // Identificacion
      farm_id: this.farmId,
      farm_name: this.farmName,
      turbine_id: this.turbineId,
      turbine_name: this.turbineName,
      
      timestamp: timestamp,
      
      // Variables
      wind_speed_mps: parseFloat(windSpeedMps.toFixed(2)),
      wind_direction_deg: windDirectionDeg,
      rotor_speed_rpm: rotorSpeedRpm,
      blade_pitch_angle_deg: bladePitchAngleDeg,
      yaw_position_deg: yawPositionDeg,
      vibrations_mms: vibrationsMms,
      gear_temperature_c: gearTemperatureC,
      bearing_temperature_c: bearingTemperatureC,
      output_voltage_v: outputVoltageV,
      generated_current_a: generatedCurrentA,
      active_power_kw: parseFloat(activePowerKw.toFixed(1)),
      reactive_power_kvar: reactivePowerKvar,
      
      // Estado
      operational_state: this.operationalState,
      
      // Info extra
      capacity_mw: this.capacityMw
    };
  }
}

class WindFarmSimulator {
  constructor() {
    this.client = null;
    this.turbines = [];
    this.initTurbines();
  }
  
  initTurbines() {
    for (let i = 1; i <= TURBINE_COUNT; i++) {
      const turbine = new TurbineSimulator(FARM_ID, i);
      this.turbines.push(turbine);
    }
  }
  
  publishMeasurements() {
    let totalPower = 0;
    let activeCount = 0;
    
    this.turbines.forEach(turbine => {
      const data = turbine.generateData();
      const topic = `windfarm/turbines/${turbine.turbineId}/measurements`;
      
      this.client.publish(topic, JSON.stringify(data), { qos: 1 }, (err) => {
        if (err) {
          console.error(`❌ Error publicando ${turbine.turbineName}:`, err);
        }
      });
      
      if (data.operational_state === 'operational') {
        totalPower += data.active_power_kw;
        activeCount++;
      }
      
      console.log(`📊 ${data.turbine_name}: ${data.active_power_kw.toFixed(0)} kW - ${data.operational_state}`);
    });
    
    console.log(`\n🌍 Total: ${totalPower.toFixed(0)} kW | ${activeCount}/${this.turbines.length} operativas\n`);
    console.log('-'.repeat(50));
  }
  
  changeRandomState() {
    const turbine = this.turbines[Math.floor(Math.random() * this.turbines.length)];
    const states = ['operational', 'operational', 'operational', 'standby', 'maintenance'];
    const newState = states[Math.floor(Math.random() * states.length)];
    
    if (turbine.operationalState !== newState) {
      const oldState = turbine.operationalState;
      turbine.operationalState = newState;
      console.log(`🔄 ${turbine.turbineName}: ${oldState} → ${newState}\n`);
    }
  }
  
  run() {
    this.client = mqtt.connect(BROKER_URL, {
      clientId: 'windfarm-simulator',
      clean: true,
    });
    
    this.client.on('connect', () => {
      console.log('✅ Conectado al broker MQTT');
      console.log('📡 Iniciando simulación...\n');
      
      // Publicar datos periódicamente
      setInterval(() => {
        this.publishMeasurements();
      }, UPDATE_INTERVAL);
      
      // Cambiar estados aleatorios cada 30 segundos
      setInterval(() => {
        this.changeRandomState();
      }, 30000);
    });
    
    this.client.on('error', (error) => {
      console.error('❌ Error MQTT:', error);
    });
    
    this.client.on('close', () => {
      console.log('🔌 Desconectado del broker');
    });
  }
}

// Iniciar simulador
console.log('🚀 Simulador de Parque Eólico - Formato Plano');
console.log(`📍 Broker: ${BROKER_URL}`);
console.log(`🏭 Parque: ${FARM_NAME}`);
console.log(`⚡ Turbinas: ${TURBINE_COUNT}`);
console.log(`⏱️  Intervalo: ${UPDATE_INTERVAL / 1000} segundos`);
console.log('='.repeat(50));

const simulator = new WindFarmSimulator();
simulator.run();

// Manejo de señales
process.on('SIGINT', () => {
  console.log('\n👋 Cerrando simulador...');
  process.exit(0);
});
```

### Ejecutar el Simulador

```bash
node simulator.js
```

## Tópicos MQTT

El simulador publica datos en los siguientes tópicos:

- **Mediciones individuales**: `windfarm/turbines/{turbine_id}/measurements`
  - Ejemplo: `windfarm/turbines/1/measurements`
  - Formato: JSON plano con todas las variables

## Transformación Automática

El frontend **automáticamente transforma** el JSON plano al formato estructurado interno:

**JSON Plano (del molino)** → **JSON Estructurado (interno)**

La transformación incluye:
- ✅ Mapeo de nombres de campos
- ✅ Cálculo automático de `powerFactor` desde `active_power_kw` y `reactive_power_kvar`
- ✅ Mapeo de `operational_state` a estados SCADA
- ✅ Valores por defecto para `oilPressure` y `oilLevel` (si no vienen en el JSON)

## Docker Compose Completo

Crea un `docker-compose.yml`:

```yaml
version: '3.8'

services:
  emqx:
    image: emqx/emqx:latest
    container_name: emqx
    ports:
      - "1883:1883"      # MQTT
      - "8083:8083"      # WebSocket
      - "8084:8084"      # WSS
      - "18083:18083"    # Dashboard
    environment:
      - EMQX_NAME=emqx
      - EMQX_HOST=127.0.0.1
    volumes:
      - emqx-data:/opt/emqx/data
      - emqx-log:/opt/emqx/log
    networks:
      - windfarm

volumes:
  emqx-data:
  emqx-log:

networks:
  windfarm:
    driver: bridge
```

## Probar la Integración

1. **Iniciar EMQX**:
   ```bash
   docker-compose up -d
   ```

2. **Ejecutar simulador**:
   ```bash
   python simulator.py
   # o
   node simulator.js
   ```

3. **Abrir frontend**:
   ```bash
   npm run dev
   ```

4. **Conectar desde el navegador**: 
   - Accede a http://localhost:5173
   - Usa el componente `MqttConnection` 
   - Conecta a `ws://localhost:8083/mqtt`

5. **Verificar datos**: Las turbinas deberían actualizarse en tiempo real

---

**Nota**: Este simulador usa el formato plano exacto que enviarán los molinos. El frontend realiza la transformación automáticamente.
