# Simulador de Backend MQTT

Este documento contiene ejemplos de código para simular un backend que publica datos en EMQX.

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
const TURBINE_COUNT = 24;
const UPDATE_INTERVAL = 5000; // 5 segundos

// Conectar al broker
const client = mqtt.connect(BROKER_URL, {
  clientId: 'windfarm-simulator',
  clean: true,
});

// Estados posibles de las turbinas
const STATUSES = ['operational', 'operational', 'operational', 'operational', 'standby', 'maintenance'];

// Estado de las turbinas
const turbineStates = new Map();

// Inicializar estados
for (let i = 1; i <= TURBINE_COUNT; i++) {
  const turbineId = `WT-${String(i).padStart(3, '0')}`;
  turbineStates.set(turbineId, {
    status: 'operational',
    baseWindSpeed: 8 + Math.random() * 10,
    baseWindDirection: Math.floor(Math.random() * 360),
  });
}

// Generar datos de turbina
function generateTurbineData(turbineId) {
  const state = turbineStates.get(turbineId);
  const isActive = state.status === 'operational';
  
  // Variación de viento
  const windSpeed = state.baseWindSpeed + (Math.random() - 0.5) * 2;
  const windDirection = (state.baseWindDirection + (Math.random() - 0.5) * 10 + 360) % 360;
  
  // Calcular potencia basada en velocidad del viento
  const activePower = isActive 
    ? Math.max(0, Math.min(2500, (windSpeed - 3) * 250 + Math.random() * 200))
    : 0;
  
  return {
    turbineId,
    timestamp: new Date().toISOString(),
    status: state.status,
    environmental: {
      windSpeed: parseFloat(windSpeed.toFixed(2)),
      windDirection: Math.floor(windDirection),
    },
    mechanical: {
      rotorSpeed: isActive ? parseFloat((10 + Math.random() * 8).toFixed(2)) : 0,
      pitchAngle: isActive ? parseFloat((5 + Math.random() * 10).toFixed(2)) : 90,
      yawPosition: Math.floor(windDirection),
      vibration: isActive ? parseFloat((0.5 + Math.random() * 1.5).toFixed(2)) : 0,
      gearboxTemperature: isActive ? parseFloat((50 + Math.random() * 20).toFixed(1)) : 25,
      bearingTemperature: isActive ? parseFloat((45 + Math.random() * 15).toFixed(1)) : 25,
      oilPressure: isActive ? parseFloat((2.5 + Math.random() * 1.5).toFixed(2)) : 0,
      oilLevel: parseFloat((80 + Math.random() * 15).toFixed(1)),
    },
    electrical: {
      outputVoltage: isActive ? parseFloat((690 + Math.random() * 10).toFixed(1)) : 0,
      outputCurrent: isActive ? parseFloat((activePower * 1000 / (690 * Math.sqrt(3) * 0.95)).toFixed(1)) : 0,
      activePower: parseFloat(activePower.toFixed(2)),
      reactivePower: isActive ? parseFloat((activePower * 0.3).toFixed(2)) : 0,
      powerFactor: isActive ? parseFloat((0.92 + Math.random() * 0.06).toFixed(3)) : 0,
    },
  };
}

// Generar estadísticas del parque
function generateFarmStats() {
  let totalPower = 0;
  let activeTurbines = 0;
  let totalWindSpeed = 0;
  let maxWindSpeed = 0;
  let minWindSpeed = 999;
  
  turbineStates.forEach((state, turbineId) => {
    const data = generateTurbineData(turbineId);
    
    if (state.status === 'operational') {
      activeTurbines++;
      totalPower += data.electrical.activePower;
    }
    
    totalWindSpeed += data.environmental.windSpeed;
    maxWindSpeed = Math.max(maxWindSpeed, data.environmental.windSpeed);
    minWindSpeed = Math.min(minWindSpeed, data.environmental.windSpeed);
  });
  
  return {
    totalPower: parseFloat(totalPower.toFixed(2)),
    activeTurbines,
    totalTurbines: TURBINE_COUNT,
    farmEnvironmental: {
      avgWindSpeed: parseFloat((totalWindSpeed / TURBINE_COUNT).toFixed(2)),
      maxWindSpeed: parseFloat(maxWindSpeed.toFixed(2)),
      minWindSpeed: parseFloat(minWindSpeed.toFixed(2)),
      predominantWindDirection: 240, // Simplificado
      lastUpdate: new Date().toISOString(),
    },
    timestamp: new Date().toISOString(),
  };
}

// Generar alerta aleatoria
function generateRandomAlert() {
  const turbineId = `WT-${String(Math.floor(Math.random() * TURBINE_COUNT) + 1).padStart(3, '0')}`;
  
  const alertTypes = ['electrical', 'mechanical', 'environmental', 'system'];
  const severities = ['critical', 'warning', 'info'];
  
  const messages = {
    electrical: ['Voltaje fluctuante', 'Factor de potencia bajo', 'Sobrecorriente detectada'],
    mechanical: ['Vibración elevada', 'Temperatura alta en caja de cambios', 'Nivel de aceite bajo'],
    environmental: ['Viento excede límites', 'Condiciones no óptimas'],
    system: ['Pérdida temporal de comunicación', 'Actualización de firmware disponible'],
  };
  
  const type = alertTypes[Math.floor(Math.random() * alertTypes.length)];
  const severity = severities[Math.floor(Math.random() * severities.length)];
  const message = messages[type][Math.floor(Math.random() * messages[type].length)];
  
  return {
    turbineId,
    type,
    severity,
    message,
    timestamp: new Date().toISOString(),
  };
}

// Cuando se conecta
client.on('connect', () => {
  console.log('✅ Conectado al broker MQTT');
  console.log('📡 Iniciando simulación...\n');
  
  // Publicar datos de turbinas
  setInterval(() => {
    turbineStates.forEach((state, turbineId) => {
      const data = generateTurbineData(turbineId);
      const topic = `windfarm/turbines/${turbineId}/measurements`;
      
      client.publish(topic, JSON.stringify(data), { qos: 1 }, (err) => {
        if (err) {
          console.error(`❌ Error publicando ${turbineId}:`, err);
        } else {
          console.log(`📊 ${turbineId}: ${data.electrical.activePower.toFixed(0)} kW`);
        }
      });
    });
  }, UPDATE_INTERVAL);
  
  // Publicar estadísticas del parque
  setInterval(() => {
    const stats = generateFarmStats();
    const topic = 'windfarm/stats';
    
    client.publish(topic, JSON.stringify(stats), { qos: 1 }, (err) => {
      if (err) {
        console.error('❌ Error publicando estadísticas:', err);
      } else {
        console.log(`\n🌍 Parque: ${stats.totalPower.toFixed(0)} kW | ${stats.activeTurbines}/${stats.totalTurbines} activas\n`);
      }
    });
  }, UPDATE_INTERVAL);
  
  // Generar alertas aleatorias
  setInterval(() => {
    if (Math.random() > 0.7) { // 30% de probabilidad
      const alert = generateRandomAlert();
      const topic = 'windfarm/alerts';
      
      client.publish(topic, JSON.stringify(alert), { qos: 1 }, (err) => {
        if (err) {
          console.error('❌ Error publicando alerta:', err);
        } else {
          console.log(`⚠️  ALERTA [${alert.severity}]: ${alert.turbineId} - ${alert.message}`);
        }
      });
    }
  }, 15000); // Cada 15 segundos
  
  // Cambiar estados aleatorios
  setInterval(() => {
    const turbineId = `WT-${String(Math.floor(Math.random() * TURBINE_COUNT) + 1).padStart(3, '0')}`;
    const state = turbineStates.get(turbineId);
    const newStatus = STATUSES[Math.floor(Math.random() * STATUSES.length)];
    
    if (state.status !== newStatus) {
      state.status = newStatus;
      console.log(`🔄 ${turbineId} cambió a estado: ${newStatus}`);
    }
  }, 30000); // Cada 30 segundos
});

// Manejo de errores
client.on('error', (error) => {
  console.error('❌ Error MQTT:', error);
});

client.on('close', () => {
  console.log('🔌 Desconectado del broker');
});

// Manejo de señales
process.on('SIGINT', () => {
  console.log('\n👋 Cerrando simulador...');
  client.end();
  process.exit(0);
});

console.log('🚀 Simulador de Parque Eólico');
console.log('📍 Broker:', BROKER_URL);
console.log('⚡ Turbinas:', TURBINE_COUNT);
console.log('⏱️  Intervalo:', UPDATE_INTERVAL / 1000, 'segundos');
console.log('-----------------------------------');
```

### Ejecutar el Simulador

```bash
node simulator.js
```

### Salida Esperada

```
🚀 Simulador de Parque Eólico
📍 Broker: mqtt://localhost:1883
⚡ Turbinas: 24
⏱️  Intervalo: 5 segundos
-----------------------------------
✅ Conectado al broker MQTT
📡 Iniciando simulación...

📊 WT-001: 1850 kW
📊 WT-002: 2100 kW
📊 WT-003: 1650 kW
...

🌍 Parque: 42500 kW | 22/24 activas

⚠️  ALERTA [warning]: WT-007 - Vibración elevada
```

## Simulador en Python

### Instalación

```bash
pip install paho-mqtt
```

### Código

Crea un archivo `simulator.py`:

```python
import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

BROKER_URL = "localhost"
BROKER_PORT = 1883
TURBINE_COUNT = 24
UPDATE_INTERVAL = 5  # segundos

class WindFarmSimulator:
    def __init__(self):
        self.client = mqtt.Client("windfarm-simulator")
        self.turbine_states = {}
        self.init_turbines()
    
    def init_turbines(self):
        for i in range(1, TURBINE_COUNT + 1):
            turbine_id = f"WT-{i:03d}"
            self.turbine_states[turbine_id] = {
                'status': 'operational',
                'base_wind_speed': 8 + random.random() * 10,
                'base_wind_direction': random.randint(0, 359),
            }
    
    def generate_turbine_data(self, turbine_id):
        state = self.turbine_states[turbine_id]
        is_active = state['status'] == 'operational'
        
        wind_speed = state['base_wind_speed'] + (random.random() - 0.5) * 2
        wind_direction = (state['base_wind_direction'] + (random.random() - 0.5) * 10) % 360
        
        active_power = 0
        if is_active:
            active_power = max(0, min(2500, (wind_speed - 3) * 250 + random.random() * 200))
        
        return {
            'turbineId': turbine_id,
            'timestamp': datetime.now().isoformat(),
            'status': state['status'],
            'environmental': {
                'windSpeed': round(wind_speed, 2),
                'windDirection': int(wind_direction),
            },
            'mechanical': {
                'rotorSpeed': round(10 + random.random() * 8, 2) if is_active else 0,
                'pitchAngle': round(5 + random.random() * 10, 2) if is_active else 90,
                'yawPosition': int(wind_direction),
                'vibration': round(0.5 + random.random() * 1.5, 2) if is_active else 0,
                'gearboxTemperature': round(50 + random.random() * 20, 1) if is_active else 25,
                'bearingTemperature': round(45 + random.random() * 15, 1) if is_active else 25,
                'oilPressure': round(2.5 + random.random() * 1.5, 2) if is_active else 0,
                'oilLevel': round(80 + random.random() * 15, 1),
            },
            'electrical': {
                'outputVoltage': round(690 + random.random() * 10, 1) if is_active else 0,
                'outputCurrent': round(active_power * 1000 / (690 * 1.732 * 0.95), 1) if is_active else 0,
                'activePower': round(active_power, 2),
                'reactivePower': round(active_power * 0.3, 2) if is_active else 0,
                'powerFactor': round(0.92 + random.random() * 0.06, 3) if is_active else 0,
            }
        }
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("✅ Conectado al broker MQTT")
            print("📡 Iniciando simulación...\n")
            self.start_simulation()
        else:
            print(f"❌ Error de conexión: {rc}")
    
    def start_simulation(self):
        # Publicar datos de turbinas
        for turbine_id in self.turbine_states.keys():
            data = self.generate_turbine_data(turbine_id)
            topic = f"windfarm/turbines/{turbine_id}/measurements"
            self.client.publish(topic, json.dumps(data), qos=1)
            print(f"📊 {turbine_id}: {data['electrical']['activePower']:.0f} kW")
    
    def run(self):
        self.client.on_connect = self.on_connect
        self.client.connect(BROKER_URL, BROKER_PORT, 60)
        
        # Loop en background
        self.client.loop_start()
        
        try:
            while True:
                time.sleep(UPDATE_INTERVAL)
                self.start_simulation()
        except KeyboardInterrupt:
            print("\n👋 Cerrando simulador...")
            self.client.loop_stop()
            self.client.disconnect()

if __name__ == "__main__":
    print("🚀 Simulador de Parque Eólico")
    print(f"📍 Broker: {BROKER_URL}:{BROKER_PORT}")
    print(f"⚡ Turbinas: {TURBINE_COUNT}")
    print(f"⏱️  Intervalo: {UPDATE_INTERVAL} segundos")
    print("-----------------------------------")
    
    simulator = WindFarmSimulator()
    simulator.run()
```

### Ejecutar

```bash
python simulator.py
```

## Docker Compose Completo

Crea un `docker-compose.yml` que incluya EMQX y el simulador:

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

  simulator:
    build: ./simulator
    container_name: windfarm-simulator
    depends_on:
      - emqx
    environment:
      - MQTT_BROKER=emqx
      - MQTT_PORT=1883
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
   docker-compose up emqx -d
   ```

2. **Ejecutar simulador**:
   ```bash
   node simulator.js
   # o
   python simulator.py
   ```

3. **Abrir frontend**:
   ```bash
   npm run dev
   ```

4. **Conectar desde el navegador**: Usa el componente `MqttConnection` para conectar a `ws://localhost:8083/mqtt`

5. **Verificar datos**: Los heatmaps y turbinas deberían actualizarse en tiempo real

---

**Nota**: Estos simuladores generan datos realistas para testing. En producción, reemplázalos con datos reales de los PLCs/SCADA de las turbinas.
