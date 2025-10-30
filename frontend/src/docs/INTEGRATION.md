# Guía de Integración - Sistema de Monitoreo de Parque Eólico

## Resumen

Este sistema está preparado para integrarse con:
- **MQTT/EMQX**: Para datos en tiempo real (mediciones, alertas, estadísticas)
- **API REST**: Para datos históricos (histórico de turbinas y alertas)

## Arquitectura de Datos

### Datos en Tiempo Real (MQTT)

El sistema se suscribe automáticamente a los siguientes tópicos:

#### 1. Mediciones de Turbinas
**Tópico**: `windfarm/turbines/{turbineId}/measurements`

**Formato del mensaje**:
```json
{
  "turbineId": "WT-001",
  "timestamp": "2025-10-29T10:30:00Z",
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

#### 2. Alertas del Sistema
**Tópico**: `windfarm/alerts`

**Formato del mensaje**:
```json
{
  "turbineId": "WT-003",
  "type": "mechanical",
  "severity": "warning",
  "message": "Temperatura de caja de cambios elevada",
  "timestamp": "2025-10-29T10:35:00Z"
}
```

**Tipos de alerta**: `electrical`, `mechanical`, `environmental`, `system`
**Severidades**: `critical`, `warning`, `info`

#### 3. Estadísticas Generales
**Tópico**: `windfarm/stats`

**Formato del mensaje**:
```json
{
  "totalPower": 48500.0,
  "activeTurbines": 22,
  "totalTurbines": 24,
  "farmEnvironmental": {
    "avgWindSpeed": 11.8,
    "maxWindSpeed": 15.2,
    "minWindSpeed": 8.5,
    "predominantWindDirection": 240,
    "lastUpdate": "2025-10-29T10:30:00Z"
  },
  "timestamp": "2025-10-29T10:30:00Z"
}
```

### Datos Históricos (API REST)

#### 1. Histórico de Turbina
**Endpoint**: `GET /api/turbines/{turbineId}/history`

**Parámetros**:
- `from`: Fecha inicio (ISO 8601)
- `to`: Fecha fin (ISO 8601)

**Respuesta**:
```json
{
  "turbineId": "WT-001",
  "from": "2025-10-28T00:00:00Z",
  "to": "2025-10-29T00:00:00Z",
  "data": [
    {
      "timestamp": "2025-10-28T00:00:00Z",
      "turbineId": "WT-001",
      "activePower": 2150.0,
      "windSpeed": 12.5,
      "status": "operational"
    }
  ]
}
```

#### 2. Histórico de Todas las Turbinas
**Endpoint**: `GET /api/turbines/history`

**Parámetros**:
- `from`: Fecha inicio (ISO 8601)
- `to`: Fecha fin (ISO 8601)

**Respuesta**: Array de `HistoricalDataPoint`

#### 3. Histórico de Alertas
**Endpoint**: `GET /api/alerts/history`

**Parámetros**:
- `page`: Número de página (default: 1)
- `size`: Tamaño de página (default: 50)
- `severity`: Filtro por severidad (opcional)

**Respuesta**:
```json
{
  "alerts": [
    {
      "id": "alert-12345",
      "turbineId": "WT-003",
      "turbineName": "Turbina 3",
      "type": "mechanical",
      "severity": "warning",
      "message": "Temperatura elevada",
      "timestamp": "2025-10-29T10:35:00Z",
      "acknowledged": true,
      "resolvedAt": "2025-10-29T11:00:00Z"
    }
  ],
  "total": 145,
  "page": 1,
  "pageSize": 50
}
```

#### 4. Reconocer Alerta
**Endpoint**: `POST /api/alerts/{alertId}/acknowledge`

#### 5. Resolver Alerta
**Endpoint**: `POST /api/alerts/{alertId}/resolve`

## Uso en el Frontend

### Opción 1: Usar el Hook Personalizado (Recomendado)

```typescript
import { useWindFarmData } from './hooks/useWindFarmData';

function MyComponent() {
  const {
    turbines,
    alerts,
    farmStats,
    farmEnvironmental,
    isConnected,
    loading,
    error,
    connect,
    disconnect,
    getTurbineHistory,
    getAlertsHistory,
    acknowledgeAlert,
    resolveAlert,
  } = useWindFarmData({
    mqttBrokerUrl: 'ws://localhost:8083/mqtt',
    mqttUsername: 'admin',
    mqttPassword: 'password',
    apiBaseUrl: '/api',
    apiKey: 'YOUR_API_KEY',
    autoConnect: true, // Conectar automáticamente
  });

  // Usar los datos...
  return (
    <div>
      {turbines.map(turbine => (
        <TurbineCard key={turbine.id} turbine={turbine} />
      ))}
    </div>
  );
}
```

### Opción 2: Usar los Servicios Directamente

```typescript
import { getMqttService } from './services/mqttService';
import { getApiService } from './services/apiService';

// Servicio MQTT
const mqttService = getMqttService('ws://localhost:8083/mqtt', {
  username: 'admin',
  password: 'password',
});

mqttService.onTurbineData((turbineId, data) => {
  console.log('Datos de turbina:', turbineId, data);
});

mqttService.onAlert((alert) => {
  console.log('Nueva alerta:', alert);
});

mqttService.onStats((stats) => {
  console.log('Estadísticas:', stats);
});

await mqttService.connect();

// Servicio API
const apiService = getApiService('/api', 'YOUR_API_KEY');

const history = await apiService.getTurbineHistory(
  'WT-001',
  new Date('2025-10-28'),
  new Date('2025-10-29')
);
```

## Configuración del Broker MQTT (EMQX)

### Docker Compose

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

volumes:
  emqx-data:
  emqx-log:
```

### Acceso al Dashboard
- URL: http://localhost:18083
- Usuario por defecto: admin
- Contraseña por defecto: public

## Integración con Backend

### Ejemplo de Publicación de Datos (Node.js)

```javascript
const mqtt = require('mqtt');
const client = mqtt.connect('mqtt://localhost:1883');

client.on('connect', () => {
  // Publicar mediciones de turbina
  setInterval(() => {
    const data = {
      turbineId: 'WT-001',
      timestamp: new Date().toISOString(),
      status: 'operational',
      environmental: {
        windSpeed: 12.5,
        windDirection: 235
      },
      mechanical: {
        rotorSpeed: 15.2,
        pitchAngle: 8.5,
        yawPosition: 235,
        vibration: 1.2,
        gearboxTemperature: 65.3,
        bearingTemperature: 58.7,
        oilPressure: 3.2,
        oilLevel: 92.5
      },
      electrical: {
        outputVoltage: 695.0,
        outputCurrent: 1250.5,
        activePower: 2150.0,
        reactivePower: 320.0,
        powerFactor: 0.989
      }
    };
    
    client.publish(
      'windfarm/turbines/WT-001/measurements',
      JSON.stringify(data)
    );
  }, 5000); // Cada 5 segundos
});
```

### Ejemplo de API REST (Express.js)

```javascript
const express = require('express');
const app = express();

// Histórico de turbina
app.get('/api/turbines/:turbineId/history', (req, res) => {
  const { turbineId } = req.params;
  const { from, to } = req.query;
  
  // Consultar base de datos...
  const data = queryDatabase(turbineId, from, to);
  
  res.json({
    turbineId,
    from,
    to,
    data
  });
});

// Histórico de alertas
app.get('/api/alerts/history', (req, res) => {
  const { page = 1, size = 50, severity } = req.query;
  
  // Consultar base de datos...
  const alerts = queryAlerts(page, size, severity);
  
  res.json({
    alerts,
    total: alerts.length,
    page: parseInt(page),
    pageSize: parseInt(size)
  });
});

app.listen(3000);
```

## Variables de Entorno Eliminadas

Las siguientes variables ya NO se sensarán ni mostrarán en la sección de entorno individual de cada molino:
- ❌ Temperatura Ambiente (ambientTemperature)
- ❌ Presión Atmosférica (atmosphericPressure)

Estas variables generales del parque se mostrarán en el overview general si son necesarias.

## Heatmaps Disponibles

El sistema incluye los siguientes heatmaps visuales:

1. **Generación de Energía**: Muestra la potencia activa de cada turbina
2. **Eficiencia Relativa**: Porcentaje de utilización respecto a capacidad
3. **Factor de Potencia**: Calidad de la energía generada
4. **Temperatura de Caja de Cambios**: Monitoreo térmico
5. **Vibraciones**: Detección de anomalías mecánicas
6. **Disponibilidad**: Uptime de cada turbina
7. **Velocidad del Viento**: Distribución del recurso eólico
8. **Estado de Turbinas**: Visualización del estado SCADA

## Próximos Pasos

1. **Configurar EMQX**: Levantar el broker MQTT
2. **Implementar Backend**: Crear servicios que publiquen datos en los tópicos
3. **Configurar API**: Implementar endpoints REST para históricos
4. **Conectar Frontend**: Usar el hook `useWindFarmData` en los componentes
5. **Probar Integración**: Verificar flujo completo de datos

## Soporte

Para más información sobre la integración, consulte:
- Documentación de EMQX: https://www.emqx.io/docs
- Tipos de datos: `/types/turbine.ts`
- Servicios: `/services/mqttService.ts` y `/services/apiService.ts`
- Hook personalizado: `/hooks/useWindFarmData.ts`
