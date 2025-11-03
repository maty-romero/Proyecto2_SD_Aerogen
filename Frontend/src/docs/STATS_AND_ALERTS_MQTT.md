# Integración MQTT - Estadísticas y Alertas

## Resumen

Este documento describe cómo integrar las **estadísticas del parque** y las **alertas** mediante tópicos MQTT, utilizando JSON plano (single-level) para facilitar la generación desde sistemas SCADA/PLC.

## 📊 Estadísticas del Parque (Producción)

### Tópico MQTT

**Tópico**: `windfarm/stats`  
**QoS**: 1  
**Frecuencia recomendada**: Cada 5-60 segundos  

### Formato JSON Plano

```json
{
  "farm_id": 1,
  "farm_name": "Comodoro Rivadavia",
  "timestamp": "2025-11-03 14:30:15",
  
  "total_active_power_kw": 45250.5,
  "total_reactive_power_kvar": 13575.15,
  
  "total_turbines": 24,
  "operational_turbines": 22,
  "stopped_turbines": 0,
  "maintenance_turbines": 1,
  "fault_turbines": 1,
  
  "avg_wind_speed_mps": 11.3,
  "max_wind_speed_mps": 15.8,
  "min_wind_speed_mps": 8.2,
  "predominant_wind_direction_deg": 245,
  
  "avg_power_factor": 0.96,
  "avg_voltage_v": 692.5,
  
  "hourly_production_kwh": [
    38500, 39200, 40100, 41500, 42300, 43800,
    45200, 46100, 47500, 48200, 47800, 46500,
    45800, 44200, 43500, 42800, 41200, 40500,
    39800, 38900, 37500, 36200, 35800, 37200
  ],
  "hourly_timestamps": [
    "00:00", "01:00", "02:00", "03:00", "04:00", "05:00",
    "06:00", "07:00", "08:00", "09:00", "10:00", "11:00",
    "12:00", "13:00", "14:00", "15:00", "16:00", "17:00",
    "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"
  ]
}
```

### Campos Requeridos

#### Identificación
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `farm_id` | number | ID del parque eólico | 1 |
| `farm_name` | string | Nombre del parque | "Comodoro Rivadavia" |
| `timestamp` | string | Timestamp del mensaje | "2025-11-03 14:30:15" |

#### Producción Total
| Campo | Tipo | Unidad | Descripción |
|-------|------|--------|-------------|
| `total_active_power_kw` | number | kW | Potencia activa total del parque |
| `total_reactive_power_kvar` | number | kVAR | Potencia reactiva total del parque |

#### Contadores de Turbinas
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `total_turbines` | number | Total de turbinas en el parque |
| `operational_turbines` | number | Turbinas en estado operativo |
| `stopped_turbines` | number | Turbinas detenidas |
| `maintenance_turbines` | number | Turbinas en mantenimiento |
| `fault_turbines` | number | Turbinas con falla |

#### Estadísticas de Viento
| Campo | Tipo | Unidad | Descripción |
|-------|------|--------|-------------|
| `avg_wind_speed_mps` | number | m/s | Velocidad promedio del viento |
| `max_wind_speed_mps` | number | m/s | Velocidad máxima del viento |
| `min_wind_speed_mps` | number | m/s | Velocidad mínima del viento |
| `predominant_wind_direction_deg` | number | grados | Dirección predominante (0-360°) |

#### Promedios Eléctricos
| Campo | Tipo | Unidad | Descripción |
|-------|------|--------|-------------|
| `avg_power_factor` | number | - | Factor de potencia promedio (0-1) |
| `avg_voltage_v` | number | V | Voltaje promedio de salida |

#### Producción Histórica (24h)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `hourly_production_kwh` | number[] | Array de 24 valores con producción por hora (kWh) |
| `hourly_timestamps` | string[] | Array de 24 timestamps correspondientes |

### Uso en Frontend

Los datos se reciben automáticamente y están disponibles en el hook:

```typescript
const { farmStats, farmEnvironmental, hourlyProduction } = useWindFarmData();

// Estadísticas generales
console.log(farmStats.totalPower); // 45250.5 kW
console.log(farmStats.activeTurbines); // 22
console.log(farmStats.averagePowerFactor); // 0.96

// Datos ambientales
console.log(farmEnvironmental.avgWindSpeed); // 11.3 m/s
console.log(farmEnvironmental.predominantWindDirection); // 245°

// Producción horaria (para gráficos)
console.log(hourlyProduction);
// [
//   { hour: "00:00", power: 38500 },
//   { hour: "01:00", power: 39200 },
//   ...
// ]
```

### Gráficos de Producción

El componente `ProductionCharts` usa estos datos automáticamente:

```typescript
// En ProductionCharts.tsx
import { useWindFarmData } from '../hooks/useWindFarmData';

export function ProductionCharts() {
  const { hourlyProduction } = useWindFarmData();
  
  return (
    <AreaChart data={hourlyProduction}>
      <Area dataKey="power" name="Potencia (kW)" />
    </AreaChart>
  );
}
```

## 🚨 Alertas del Sistema

### Tópico MQTT

**Tópico**: `windfarm/alerts`  
**QoS**: 1  
**Frecuencia**: Cuando ocurre una alerta (event-driven)  

### Formato JSON Plano

```json
{
  "alert_id": "ALT-2025110315234567",
  "farm_id": 1,
  "turbine_id": 7,
  "turbine_name": "T-007",
  "alert_type": "mechanical",
  "severity": "warning",
  "message": "Temperatura del engranaje elevada",
  "details": "Temp. actual: 72°C (límite: 70°C)",
  "timestamp": "2025-11-03 15:23:45",
  "acknowledged": false,
  "resolved": false
}
```

### Campos Requeridos

#### Identificación
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `alert_id` | string | ID único de la alerta | "ALT-2025110315234567" |
| `farm_id` | number | ID del parque | 1 |
| `turbine_id` | number | ID de la turbina | 7 |
| `turbine_name` | string | Nombre de la turbina | "T-007" |
| `timestamp` | string | Timestamp de la alerta | "2025-11-03 15:23:45" |

#### Clasificación
| Campo | Tipo | Valores Posibles | Descripción |
|-------|------|------------------|-------------|
| `alert_type` | string | electrical, mechanical, environmental, system | Tipo de alerta |
| `severity` | string | critical, warning, info | Severidad de la alerta |

**Valores de `alert_type`**:
- `electrical` / `eléctrica` / `electrica` - Problemas eléctricos
- `mechanical` / `mecánica` / `mecanica` - Problemas mecánicos
- `environmental` / `ambiental` - Condiciones ambientales
- `system` / `sistema` - Sistema SCADA/control

**Valores de `severity`**:
- `critical` / `crítico` / `critico` - Requiere atención inmediata
- `warning` / `advertencia` - Requiere atención pronto
- `info` / `información` / `informacion` - Informativa

#### Descripción
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `message` | string | ✅ Sí | Mensaje principal de la alerta |
| `details` | string | ❌ Opcional | Detalles adicionales técnicos |

#### Estado
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `acknowledged` | boolean | Si la alerta fue reconocida |
| `resolved` | boolean | Si la alerta fue resuelta |

### Ejemplos de Alertas

#### Alerta Crítica - Eléctrica
```json
{
  "alert_id": "ALT-2025110315001234",
  "farm_id": 1,
  "turbine_id": 3,
  "turbine_name": "T-003",
  "alert_type": "electrical",
  "severity": "critical",
  "message": "Sobrecorriente detectada",
  "details": "Corriente: 1850A (límite: 1600A) - Desconexión automática activada",
  "timestamp": "2025-11-03 15:00:12",
  "acknowledged": false,
  "resolved": false
}
```

#### Alerta Warning - Mecánica
```json
{
  "alert_id": "ALT-2025110314523456",
  "farm_id": 1,
  "turbine_id": 12,
  "turbine_name": "T-012",
  "alert_type": "mechanical",
  "severity": "warning",
  "message": "Vibración elevada en rotor",
  "details": "Vibración: 2.8 mm/s (límite: 2.5 mm/s)",
  "timestamp": "2025-11-03 14:52:34",
  "acknowledged": false,
  "resolved": false
}
```

#### Alerta Info - Sistema
```json
{
  "alert_id": "ALT-2025110306001111",
  "farm_id": 1,
  "turbine_id": 0,
  "turbine_name": "Sistema General",
  "alert_type": "system",
  "severity": "info",
  "message": "Actualización de firmware completada",
  "details": "Versión 2.5.3 instalada en todas las turbinas",
  "timestamp": "2025-11-03 06:00:11",
  "acknowledged": true,
  "resolved": true
}
```

### Uso en Frontend

Las alertas se reciben automáticamente:

```typescript
const { alerts } = useWindFarmData();

// Filtrar por severidad
const criticalAlerts = alerts.filter(a => a.severity === 'critical');
const warningAlerts = alerts.filter(a => a.severity === 'warning');

// Filtrar por estado
const pendingAlerts = alerts.filter(a => !a.acknowledged);
const unresolvedAlerts = alerts.filter(a => !a.resolvedAt);

// Contar alertas por tipo
const electricalCount = alerts.filter(a => a.type === 'electrical').length;
const mechanicalCount = alerts.filter(a => a.type === 'mechanical').length;
```

### Panel de Alertas

El componente `AlertsPanel` muestra las alertas automáticamente con colores según severidad:

- 🔴 **Critical** - Rojo
- 🟡 **Warning** - Amarillo
- 🔵 **Info** - Azul

## 🔄 Transformación Automática

El frontend realiza transformación automática de ambos formatos:

### Estadísticas: Plano → Estructurado

```typescript
// JSON Plano (del SCADA)
{
  "total_active_power_kw": 45250.5,
  "operational_turbines": 22,
  "avg_wind_speed_mps": 11.3,
  ...
}

// ↓ Transformación automática ↓

// JSON Estructurado (interno)
{
  totalPower: 45250.5,
  activeTurbines: 22,
  farmEnvironmental: {
    avgWindSpeed: 11.3,
    ...
  },
  hourlyProduction: [...],
  ...
}
```

### Alertas: Plano → Estructurado

```typescript
// JSON Plano (del SCADA)
{
  "alert_type": "mechanical",
  "severity": "warning",
  "turbine_id": 7,
  ...
}

// ↓ Transformación automática ↓

// JSON Estructurado (interno)
{
  type: 'mechanical',
  severity: 'warning',
  turbineId: '7',
  ...
}
```

## 📍 Ubicación del Código

### Transformaciones

**Archivo**: `/services/mqttService.ts`

```typescript
// Transformación de estadísticas
private transformFlatStats(flatStats: MqttFlatStats): MqttStatsMessage

// Transformación de alertas
private transformFlatAlert(flatAlert: MqttFlatAlert): MqttAlertMessage
```

### Tipos

**Archivo**: `/types/turbine.ts`

```typescript
export interface MqttFlatStats { ... }
export interface MqttFlatAlert { ... }
```

### Hook

**Archivo**: `/hooks/useWindFarmData.ts`

```typescript
export const useWindFarmData = () => {
  // Retorna: alerts, farmStats, hourlyProduction, etc.
}
```

## 🧪 Testing

### Simulador Python - Estadísticas

```python
import paho.mqtt.client as mqtt
import json
import time

client = mqtt.Client("stats-simulator")
client.connect("localhost", 1883, 60)

stats = {
    "farm_id": 1,
    "farm_name": "Comodoro Rivadavia",
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    
    "total_active_power_kw": 45250.5,
    "total_reactive_power_kvar": 13575.15,
    
    "total_turbines": 24,
    "operational_turbines": 22,
    "stopped_turbines": 0,
    "maintenance_turbines": 1,
    "fault_turbines": 1,
    
    "avg_wind_speed_mps": 11.3,
    "max_wind_speed_mps": 15.8,
    "min_wind_speed_mps": 8.2,
    "predominant_wind_direction_deg": 245,
    
    "avg_power_factor": 0.96,
    "avg_voltage_v": 692.5,
    
    "hourly_production_kwh": [38500, 39200, ...],  # 24 valores
    "hourly_timestamps": ["00:00", "01:00", ...]   # 24 timestamps
}

client.publish("windfarm/stats", json.dumps(stats), qos=1)
print("✅ Estadísticas publicadas")
```

### Simulador Python - Alertas

```python
import paho.mqtt.client as mqtt
import json
import time
import uuid

client = mqtt.Client("alerts-simulator")
client.connect("localhost", 1883, 60)

alert = {
    "alert_id": f"ALT-{int(time.time())}{uuid.uuid4().hex[:8]}",
    "farm_id": 1,
    "turbine_id": 7,
    "turbine_name": "T-007",
    "alert_type": "mechanical",
    "severity": "warning",
    "message": "Temperatura del engranaje elevada",
    "details": "Temp. actual: 72°C (límite: 70°C)",
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "acknowledged": False,
    "resolved": False
}

client.publish("windfarm/alerts", json.dumps(alert), qos=1)
print("⚠️ Alerta publicada:", alert['message'])
```

## 📦 Integración Completa

### 1. Configurar Broker EMQX

```bash
docker run -d --name emqx \
  -p 1883:1883 \
  -p 8083:8083 \
  -p 18083:18083 \
  emqx/emqx:latest
```

### 2. Publicar Estadísticas Periódicamente

Desde su sistema SCADA, publicar al tópico `windfarm/stats` cada 5-60 segundos.

### 3. Publicar Alertas en Tiempo Real

Cuando ocurra una alerta, publicar inmediatamente al tópico `windfarm/alerts`.

### 4. Conectar Frontend

```typescript
// En el componente principal
const { 
  farmStats,           // Estadísticas generales
  hourlyProduction,    // Producción últimas 24h
  alerts               // Alertas recibidas
} = useWindFarmData({
  mqttBrokerUrl: 'ws://localhost:8083/mqtt',
  autoConnect: true
});
```

## ✨ Características

### Estadísticas
- ✅ JSON plano (fácil de generar desde SCADA)
- ✅ Producción horaria para gráficos (24 valores)
- ✅ Contadores de turbinas por estado
- ✅ Promedios eléctricos (power factor, voltaje)
- ✅ Estadísticas de viento completas
- ✅ Actualización en tiempo real

### Alertas
- ✅ JSON plano con soporte multiidioma
- ✅ Clasificación por tipo y severidad
- ✅ Detalles técnicos opcionales
- ✅ Estados: acknowledged, resolved
- ✅ Colores automáticos según severidad
- ✅ Histórico persistente (últimas 100)

---

**Última actualización**: 2025-11-03  
**Versión**: 1.0.0
