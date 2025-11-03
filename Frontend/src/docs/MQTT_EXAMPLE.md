# Ejemplo de Implementación MQTT Real

Este documento muestra cómo activar la integración MQTT real en el frontend.

## Instalación de Dependencias

Primero, instala la librería MQTT.js:

```bash
npm install mqtt
# o
yarn add mqtt
```

## Actualizar mqttService.ts

El archivo actual tiene la lógica preparada pero comentada. Para activar MQTT real, descomenta y modifica el servicio:

### 1. Importar la librería

```typescript
// Al inicio del archivo /services/mqttService.ts
import mqtt from 'mqtt';
```

### 2. Actualizar el método connect()

```typescript
async connect(): Promise<void> {
  try {
    console.log('Conectando a MQTT broker:', this.brokerUrl);
    
    // Conectar usando mqtt.js
    this.client = mqtt.connect(this.brokerUrl, {
      clientId: this.options.clientId,
      username: this.options.username,
      password: this.options.password,
      clean: this.options.clean,
      reconnectPeriod: this.options.reconnectPeriod,
    });

    // Manejar eventos de conexión
    this.client.on('connect', () => {
      this.connected = true;
      this.reconnectAttempts = 0;
      
      if (this.onConnectionChangeCallback) {
        this.onConnectionChangeCallback(true);
      }
      
      this.subscribeToTopics();
      console.log('Conectado a MQTT broker exitosamente');
    });

    // Manejar mensajes
    this.client.on('message', (topic: string, payload: Buffer) => {
      this.handleMessage(topic, payload);
    });

    // Manejar errores
    this.client.on('error', (error: Error) => {
      console.error('Error MQTT:', error);
      this.handleReconnect();
    });

    // Manejar desconexión
    this.client.on('close', () => {
      this.connected = false;
      if (this.onConnectionChangeCallback) {
        this.onConnectionChangeCallback(false);
      }
    });

  } catch (error) {
    console.error('Error conectando a MQTT:', error);
    this.handleReconnect();
  }
}
```

### 3. Actualizar el método subscribe()

```typescript
private subscribe(topic: string): void {
  try {
    if (!this.client) return;
    
    this.client.subscribe(topic, { qos: 1 }, (err) => {
      if (err) {
        console.error('Error suscribiendo al tópico:', topic, err);
      } else {
        console.log('Suscrito al tópico:', topic);
      }
    });
  } catch (error) {
    console.error('Error suscribiendo al tópico:', topic, error);
  }
}
```

### 4. Actualizar el método disconnect()

```typescript
disconnect(): void {
  if (this.client) {
    this.client.end();
    this.connected = false;
    if (this.onConnectionChangeCallback) {
      this.onConnectionChangeCallback(false);
    }
    console.log('Desconectado del broker MQTT');
  }
}
```

### 5. Actualizar el método publish()

```typescript
publish(topic: string, message: any): void {
  if (!this.connected || !this.client) {
    console.error('No conectado al broker MQTT');
    return;
  }
  
  try {
    const payload = JSON.stringify(message);
    this.client.publish(topic, payload, { qos: 1 }, (err) => {
      if (err) {
        console.error('Error publicando mensaje:', err);
      } else {
        console.log('Mensaje publicado en', topic);
      }
    });
  } catch (error) {
    console.error('Error publicando mensaje:', error);
  }
}
```

## Uso en Componentes

### Opción A: Con el Hook (Recomendado)

```typescript
import { useWindFarmData } from './hooks/useWindFarmData';
import { MqttConnection } from './components/MqttConnection';

function Dashboard() {
  const {
    turbines,
    alerts,
    farmStats,
    isConnected,
    loading,
    error,
    connect,
    disconnect,
  } = useWindFarmData();

  const handleConnect = (config) => {
    connect();
  };

  return (
    <div>
      <MqttConnection
        isConnected={isConnected}
        onConnect={handleConnect}
        onDisconnect={disconnect}
        error={error}
      />
      
      {/* Resto de tu UI */}
      <div className="grid grid-cols-4">
        {turbines.map(turbine => (
          <TurbineCard key={turbine.id} turbine={turbine} />
        ))}
      </div>
    </div>
  );
}
```

### Opción B: Gestión Manual

```typescript
import { useEffect, useState } from 'react';
import { getMqttService } from './services/mqttService';

function MyComponent() {
  const [turbines, setTurbines] = useState<Map<string, Turbine>>(new Map());
  const mqttService = getMqttService();

  useEffect(() => {
    // Configurar callbacks
    mqttService.onTurbineData((turbineId, data) => {
      setTurbines(prev => {
        const updated = new Map(prev);
        updated.set(turbineId, {
          id: turbineId,
          name: `Turbina ${turbineId}`,
          status: data.status,
          capacity: 2.5,
          environmental: data.environmental,
          mechanical: data.mechanical,
          electrical: data.electrical,
          // ... resto de campos
        });
        return updated;
      });
    });

    // Conectar
    mqttService.connect();

    // Cleanup
    return () => {
      mqttService.disconnect();
    };
  }, []);

  return (
    <div>
      {Array.from(turbines.values()).map(turbine => (
        <div key={turbine.id}>{turbine.name}</div>
      ))}
    </div>
  );
}
```

## Configuración de Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
VITE_MQTT_BROKER_URL=ws://localhost:8083/mqtt
VITE_MQTT_USERNAME=admin
VITE_MQTT_PASSWORD=your_password
VITE_API_BASE_URL=/api
VITE_API_KEY=your_api_key
```

Luego úsalas en tu código:

```typescript
const {
  turbines,
  // ...
} = useWindFarmData({
  mqttBrokerUrl: import.meta.env.VITE_MQTT_BROKER_URL,
  mqttUsername: import.meta.env.VITE_MQTT_USERNAME,
  mqttPassword: import.meta.env.VITE_MQTT_PASSWORD,
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL,
  apiKey: import.meta.env.VITE_API_KEY,
  autoConnect: true,
});
```

## Problemas Comunes

### Error: "WebSocket connection failed"

**Causa**: El broker EMQX no está configurado para WebSocket o usa puerto incorrecto.

**Solución**:
1. Verifica que EMQX esté escuchando en el puerto 8083 (WS) o 8084 (WSS)
2. Verifica la URL: debe empezar con `ws://` o `wss://`
3. Verifica que no haya CORS bloqueando la conexión

### Error: "Authentication failed"

**Causa**: Credenciales incorrectas.

**Solución**:
1. Verifica usuario y contraseña en EMQX dashboard
2. Asegúrate de que el cliente tenga permisos de suscripción/publicación

### Mensajes no se reciben

**Causa**: Tópicos mal configurados o QoS incorrecto.

**Solución**:
1. Verifica los nombres de los tópicos (case-sensitive)
2. Usa QoS 1 o 2 para mensajes importantes
3. Verifica en EMQX dashboard que los mensajes se están publicando

## Testing con MQTT Explorer

Para probar la integración, usa MQTT Explorer:

1. Descarga: http://mqtt-explorer.com/
2. Conecta al broker EMQX
3. Publica mensajes de prueba:

```json
// Tópico: windfarm/turbines/WT-001/measurements
{
  "turbineId": "WT-001",
  "timestamp": "2025-10-29T12:00:00Z",
  "status": "operational",
  "environmental": {
    "windSpeed": 12.5,
    "windDirection": 235
  },
  "mechanical": {
    "rotorSpeed": 15.2,
    "pitchAngle": 8.5,
    "yawPosition": 235,
    "vibration": 1.2,
    "gearboxTemperature": 65.3,
    "bearingTemperature": 58.7,
    "oilPressure": 3.2,
    "oilLevel": 92.5
  },
  "electrical": {
    "outputVoltage": 695.0,
    "outputCurrent": 1250.5,
    "activePower": 2150.0,
    "reactivePower": 320.0,
    "powerFactor": 0.989
  }
}
```

## Monitoreo de Conexión

Agrega el componente `MqttConnection` a tu interfaz para monitorear el estado de la conexión:

```typescript
import { MqttConnection } from './components/MqttConnection';

<MqttConnection
  isConnected={isConnected}
  onConnect={(config) => {
    // Configurar conexión con los datos del formulario
    mqttService.connect();
  }}
  onDisconnect={() => mqttService.disconnect()}
  error={error}
  lastUpdate={lastUpdate}
/>
```

## Próximos Pasos

1. Instalar `mqtt` con npm/yarn
2. Actualizar `mqttService.ts` con el código real
3. Configurar variables de entorno
4. Probar conexión con MQTT Explorer
5. Implementar backend que publique datos
6. Integrar con componentes de UI

---

**Nota**: El código actual funciona en modo simulado. Sigue estos pasos para activar la integración real con EMQX.
