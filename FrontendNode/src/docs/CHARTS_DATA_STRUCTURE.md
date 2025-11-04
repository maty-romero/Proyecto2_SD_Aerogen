# Estructura de Datos para Gráficos de Producción

## Librería Utilizada

Los gráficos del sistema utilizan **Recharts** (https://recharts.org/), una librería de componentes de gráficos para React construida con D3.

### Importación
```typescript
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';
```

---

## Tipos de Gráficos y Estructuras de Datos

### 1. Potencia Activa en Tiempo Real (24h) - AreaChart

**Tipo de gráfico:** `AreaChart`

**Estructura de datos:**
```typescript
interface HourlyData {
  hour: string;        // Formato: "HH:00" (ej: "00:00", "13:00")
  power: number;       // Potencia en kW
  windSpeed: number;   // Velocidad del viento en m/s (opcional)
  voltage: number;     // Voltaje en V (opcional)
}

// Ejemplo
const hourlyData: HourlyData[] = [
  { hour: "00:00", power: 25430, windSpeed: 12.5, voltage: 690 },
  { hour: "01:00", power: 28950, windSpeed: 13.2, voltage: 692 },
  { hour: "02:00", power: 31200, windSpeed: 14.1, voltage: 688 },
  // ... 24 registros en total
];
```

**Datos mostrados:**
- **Eje X:** Hora del día
- **Eje Y:** Potencia (kW)
- **Serie:** Potencia activa con gradiente azul

---

### 2. Producción Semanal - BarChart

**Tipo de gráfico:** `BarChart` (barras comparativas)

**Estructura de datos:**
```typescript
interface WeeklyData {
  day: string;          // Día de la semana: "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"
  production: number;   // Producción real en MWh
  target: number;       // Objetivo de producción en MWh
  activePower: number;  // Potencia activa promedio en kW (opcional)
}

// Ejemplo
const weeklyData: WeeklyData[] = [
  { day: "Lun", production: 1150, target: 1200, activePower: 48500 },
  { day: "Mar", production: 1280, target: 1200, activePower: 53300 },
  { day: "Mié", production: 980, target: 1200, activePower: 40800 },
  { day: "Jue", production: 1420, target: 1200, activePower: 59200 },
  { day: "Vie", production: 1350, target: 1200, activePower: 56300 },
  { day: "Sáb", production: 1180, target: 1200, activePower: 49200 },
  { day: "Dom", production: 1050, target: 1200, activePower: 43800 },
];
```

**Datos mostrados:**
- **Eje X:** Días de la semana
- **Eje Y:** Producción (MWh)
- **Series:** 
  - Producción Real (verde)
  - Objetivo (gris)

---

### 3. Velocidad del Viento y Voltaje (24h) - LineChart

**Tipo de gráfico:** `LineChart` (doble eje Y)

**Estructura de datos:**
```typescript
interface HourlyTrendsData {
  hour: string;        // Formato: "HH:00"
  windSpeed: number;   // Velocidad del viento en m/s
  voltage: number;     // Voltaje en V
}

// Ejemplo (puede reutilizar hourlyData del primer gráfico)
const hourlyTrends: HourlyTrendsData[] = [
  { hour: "00:00", windSpeed: 8.5, voltage: 685 },
  { hour: "01:00", windSpeed: 9.2, voltage: 688 },
  { hour: "02:00", windSpeed: 10.1, voltage: 692 },
  // ... 24 registros
];
```

**Datos mostrados:**
- **Eje X:** Hora del día
- **Eje Y Izquierdo:** Velocidad del viento (m/s) - Línea cyan
- **Eje Y Derecho:** Voltaje (V) - Línea naranja

---

### 4. Tendencias Mensuales - LineChart

**Tipo de gráfico:** `LineChart` (doble eje Y)

**Estructura de datos:**
```typescript
interface MonthlyData {
  month: string;        // Mes: "Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"
  production: number;   // Producción total en MWh
  powerFactor: number;  // Factor de potencia (0-1)
}

// Ejemplo
const monthlyData: MonthlyData[] = [
  { month: "Ene", production: 32400, powerFactor: 0.94 },
  { month: "Feb", production: 29800, powerFactor: 0.92 },
  { month: "Mar", production: 35200, powerFactor: 0.96 },
  { month: "Abr", production: 34100, powerFactor: 0.95 },
  { month: "May", production: 36800, powerFactor: 0.97 },
  { month: "Jun", production: 33500, powerFactor: 0.94 },
  { month: "Jul", production: 31200, powerFactor: 0.93 },
  { month: "Ago", production: 33900, powerFactor: 0.95 },
  { month: "Sep", production: 35600, powerFactor: 0.96 },
  { month: "Oct", production: 37200, powerFactor: 0.97 },
  { month: "Nov", production: 35800, powerFactor: 0.96 },
  { month: "Dic", production: 33200, powerFactor: 0.94 },
];
```

**Datos mostrados:**
- **Eje X:** Meses del año
- **Eje Y Izquierdo:** Producción (MWh) - Línea azul
- **Eje Y Derecho:** Factor de Potencia (0.9-1.0) - Línea violeta

---

## Integración con MQTT y API REST

### Datos en Tiempo Real (MQTT)

Para actualizar los gráficos en tiempo real con datos del broker MQTT:

#### Tópico: `windfarm/stats`
```typescript
interface MqttStatsMessage {
  timestamp: string;
  totalPower: number;           // Potencia total del parque en kW
  activeTurbines: number;       // Número de turbinas activas
  totalTurbines: number;        // Total de turbinas
  farmEnvironmental: {
    windSpeed: number;          // Velocidad promedio del viento
    windDirection: number;      // Dirección del viento
  };
}
```

**Uso:** Actualizar el gráfico de potencia en tiempo real agregando nuevos puntos cada X segundos/minutos.

#### Tópico por turbina: `windfarm/turbine/{turbineId}`
```typescript
interface MqttTurbineMessage {
  timestamp: string;
  electrical: {
    voltage: number;            // Voltaje en V
    current: number;            // Corriente en A
    activePower: number;        // Potencia activa en kW
    reactivePower: number;      // Potencia reactiva en kVAr
    powerFactor: number;        // Factor de potencia
  };
  environmental: {
    windSpeed: number;          // Velocidad del viento en m/s
    windDirection: number;      // Dirección del viento en grados
  };
}
```

**Uso:** Agregar datos de cada turbina y calcular promedios para los gráficos.

---

### Datos Históricos (API REST)

Para cargar datos históricos de producción:

#### Endpoint: `GET /api/turbines/{turbineId}/history`

**Query Parameters:**
- `from`: Fecha inicio (ISO 8601)
- `to`: Fecha fin (ISO 8601)
- `interval`: "hourly", "daily", "weekly", "monthly"

**Respuesta:**
```typescript
interface HistoricalDataResponse {
  turbineId: string;
  interval: string;
  data: Array<{
    timestamp: string;          // ISO 8601
    activePower: number;        // kW
    voltage: number;            // V
    current: number;            // A
    powerFactor: number;        // 0-1
    windSpeed: number;          // m/s
    windDirection: number;      // grados
    production: number;         // MWh (acumulado según intervalo)
  }>;
}
```

#### Endpoint: `GET /api/farm/production`

**Query Parameters:**
- `from`: Fecha inicio
- `to`: Fecha fin
- `aggregation`: "hourly", "daily", "weekly", "monthly"

**Respuesta:**
```typescript
interface ProductionResponse {
  aggregation: string;
  data: Array<{
    period: string;             // Etiqueta del período
    timestamp: string;          // ISO 8601
    totalProduction: number;    // MWh
    targetProduction: number;   // MWh
    avgPowerFactor: number;     // 0-1
    avgWindSpeed: number;       // m/s
    avgVoltage: number;         // V
    activeTurbines: number;     // Número promedio de turbinas activas
  }>;
}
```

---

## Ejemplo de Integración

### Actualizar gráfico en tiempo real con MQTT

```typescript
import { useState, useEffect } from 'react';
import { getMqttService } from '../services/mqttService';

export function ProductionChartsLive() {
  const [hourlyData, setHourlyData] = useState([]);
  const mqttService = getMqttService();

  useEffect(() => {
    mqttService.onStats((message) => {
      const newPoint = {
        hour: new Date(message.timestamp).toLocaleTimeString('es-ES', { 
          hour: '2-digit', 
          minute: '2-digit' 
        }),
        power: message.totalPower,
        windSpeed: message.farmEnvironmental.windSpeed,
      };

      // Mantener solo últimas 24 horas (agregando cada minuto = 1440 puntos)
      setHourlyData(prev => [...prev.slice(-1439), newPoint]);
    });

    mqttService.connect();

    return () => mqttService.disconnect();
  }, []);

  return (
    <AreaChart data={hourlyData}>
      {/* Configuración del gráfico */}
    </AreaChart>
  );
}
```

### Cargar datos históricos de API

```typescript
import { useEffect, useState } from 'react';
import { getApiService } from '../services/apiService';

export function ProductionChartsHistorical() {
  const [weeklyData, setWeeklyData] = useState([]);
  const apiService = getApiService();

  useEffect(() => {
    const loadWeeklyData = async () => {
      const to = new Date();
      const from = new Date(to.getTime() - 7 * 24 * 60 * 60 * 1000); // 7 días atrás

      const response = await apiService.getProductionHistory(from, to, 'daily');
      
      const formattedData = response.data.map(item => ({
        day: new Date(item.timestamp).toLocaleDateString('es-ES', { weekday: 'short' }),
        production: item.totalProduction,
        target: item.targetProduction,
        activePower: item.avgActivePower,
      }));

      setWeeklyData(formattedData);
    };

    loadWeeklyData();
  }, []);

  return (
    <BarChart data={weeklyData}>
      {/* Configuración del gráfico */}
    </BarChart>
  );
}
```

---

## Resumen de Campos Requeridos

### Datos Mínimos para Gráficos

| Gráfico | Campos Requeridos | Frecuencia Sugerida |
|---------|-------------------|---------------------|
| Potencia 24h | `hour`, `power` | Cada 1-5 minutos |
| Producción Semanal | `day`, `production`, `target` | Diario |
| Viento y Voltaje | `hour`, `windSpeed`, `voltage` | Cada 5-15 minutos |
| Tendencias Mensuales | `month`, `production`, `powerFactor` | Mensual |

### Unidades Estándar

- **Potencia Activa:** kW (kilovatios)
- **Producción:** MWh (megavatios-hora)
- **Voltaje:** V (voltios)
- **Corriente:** A (amperios)
- **Velocidad del Viento:** m/s (metros por segundo)
- **Factor de Potencia:** Valor decimal entre 0 y 1
- **Temperatura:** °C (grados Celsius)

---

## Configuración de Recharts

### Instalación
La librería ya está disponible en el proyecto, no requiere instalación adicional.

### Características Clave

1. **ResponsiveContainer:** Permite que los gráficos se adapten al tamaño del contenedor
2. **Tooltips personalizables:** Información detallada al hacer hover
3. **Múltiples ejes Y:** Para combinar diferentes métricas en un solo gráfico
4. **Animaciones:** Transiciones suaves al actualizar datos
5. **Estilos adaptables:** Soporte para modo oscuro/claro

### Ejemplo de Configuración Básica

```typescript
<ResponsiveContainer width="100%" height={350}>
  <LineChart data={data}>
    <CartesianGrid strokeDasharray="3 3" />
    <XAxis dataKey="hour" />
    <YAxis />
    <Tooltip />
    <Legend />
    <Line 
      type="monotone" 
      dataKey="power" 
      stroke="#3b82f6" 
      strokeWidth={2}
    />
  </LineChart>
</ResponsiveContainer>
```

---

Para más información sobre Recharts, consulta la documentación oficial:
https://recharts.org/en-US/api
