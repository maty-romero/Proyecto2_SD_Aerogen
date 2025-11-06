# Modelo de Datos del Sistema

Este documento describe el modelo de datos utilizado en el sistema de monitoreo, incluyendo los formatos de datos, las transformaciones y las estructuras utilizadas para la visualización.

## Formato de Datos de Entrada (JSON Plano)

El sistema está diseñado para recibir datos en un formato JSON plano (single-level) a través de MQTT. Este formato es fácil de generar desde sistemas SCADA/PLC.

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

## Formato de Datos Interno (Estructurado)

Internamente, el frontend transforma el JSON plano a un formato estructurado para facilitar su uso en los componentes de React.

```json
{
  "turbineId": "5",
  "timestamp": "2025-11-02 14:30:15",
  "status": "operational",
  "environmental": {
    "windSpeed": 12.5,
    "windDirection": 245
  },
  "mechanical": {
    "rotorSpeed": 15.3,
    "pitchAngle": 8.2,
    "yawPosition": 245,
    "vibration": 1.2,
    "gearboxTemperature": 62.5,
    "bearingTemperature": 55.8,
    "oilPressure": 5.0, // Valor por defecto
    "oilLevel": 85 // Valor por defecto
  },
  "electrical": {
    "outputVoltage": 695.2,
    "outputCurrent": 1250.5,
    "activePower": 2150.0,
    "reactivePower": 645.0,
    "powerFactor": 0.958 // Calculado
  }
}
```

## Mapeo y Transformación de Datos

La transformación del formato plano al estructurado se realiza automáticamente en el frontend.

### Mapeo de Campos

| Campo Plano (`snake_case`) | Campo Estructurado (`camelCase`) |
|---|---|
| `turbine_id` | `turbineId` |
| `wind_speed_mps` | `environmental.windSpeed` |
| `rotor_speed_rpm` | `mechanical.rotorSpeed` |
| `active_power_kw` | `electrical.activePower` |

### Cálculos Automáticos

- **Factor de Potencia (`powerFactor`)**: Se calcula a partir de la potencia activa y reactiva.
- **Valores por Defecto**: Si `oil_pressure_bar` y `oil_level_percent` no se proporcionan, se asignan valores por defecto (5.0 bar y 85%).

### Mapeo de Estados

El campo `operational_state` se mapea a un estado interno estandarizado:

| `operational_state` | Estado Interno | Color en UI |
|---|---|---|
| `operational`, `running` | `operational` | Verde 🟢 |
| `stopped` | `stopped` | Gris ⚫ |
| `fault`, `error` | `fault` | Rojo 🔴 |
| `maintenance` | `maintenance` | Amarillo 🟡 |
| `standby`, `idle` | `standby` | Azul 🔵 |

## Estructura de Datos para Gráficos

Los gráficos de producción utilizan la librería **Recharts** y esperan los datos en un formato específico.

### Potencia Activa en Tiempo Real (Gráfico de Área)

- **Componente**: `AreaChart`
- **Estructura de datos**:

```typescript
interface HourlyData {
  hour: string; // Formato: "HH:00"
  power: number; // Potencia en kW
}

const data: HourlyData[] = [
  { hour: "00:00", power: 25430 },
  { hour: "01:00", power: 28950 },
  // ...
];
```

### Producción Semanal (Gráfico de Barras)

- **Componente**: `BarChart`
- **Estructura de datos**:

```typescript
interface WeeklyData {
  day: string; // "Lun", "Mar", ...
  production: number; // Producción real en MWh
  target: number; // Objetivo de producción en MWh
}

const data: WeeklyData[] = [
  { day: "Lun", production: 1150, target: 1200 },
  { day: "Mar", production: 1280, target: 1200 },
  // ...
];
```
