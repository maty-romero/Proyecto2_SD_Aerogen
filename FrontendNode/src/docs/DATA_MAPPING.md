# Mapeo de Datos - Formato Plano a Estructurado

## Resumen

El sistema recibe datos en **formato plano (single-level JSON)** desde los molinos a través de MQTT, y los transforma automáticamente al **formato estructurado interno** usado por los componentes React.

## Formato de Entrada (del Molino)

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

## Formato de Salida (Interno)

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
    "oilPressure": 5.0,
    "oilLevel": 85
  },
  "electrical": {
    "outputVoltage": 695.2,
    "outputCurrent": 1250.5,
    "activePower": 2150.0,
    "reactivePower": 645.0,
    "powerFactor": 0.958
  }
}
```

## Tabla de Mapeo de Campos

### Identificación

| Campo Plano | Campo Estructurado | Notas |
|-------------|-------------------|-------|
| `turbine_id` | `turbineId` (string) | Se convierte a string |
| `turbine_name` | Metadata: `name` | Usado para actualizar el nombre de la turbina |
| `timestamp` | `timestamp` | Se mantiene igual |
| `capacity_mw` | Metadata: `capacity` | Usado para actualizar la capacidad |
| `operational_state` | `status` | Ver tabla de mapeo de estados |

### Variables Ambientales

| Campo Plano | Campo Estructurado | Transformación |
|-------------|-------------------|----------------|
| `wind_speed_mps` | `environmental.windSpeed` | Directo |
| `wind_direction_deg` | `environmental.windDirection` | Directo |

### Variables Mecánicas

| Campo Plano | Campo Estructurado | Transformación |
|-------------|-------------------|----------------|
| `rotor_speed_rpm` | `mechanical.rotorSpeed` | Directo |
| `blade_pitch_angle_deg` | `mechanical.pitchAngle` | Directo |
| `yaw_position_deg` | `mechanical.yawPosition` | Directo |
| `vibrations_mms` | `mechanical.vibration` | Directo |
| `gear_temperature_c` | `mechanical.gearboxTemperature` | Directo |
| `bearing_temperature_c` | `mechanical.bearingTemperature` | Directo |
| N/A | `mechanical.oilPressure` | **Valor por defecto: 5.0** |
| N/A | `mechanical.oilLevel` | **Valor por defecto: 85** |

### Variables Eléctricas

| Campo Plano | Campo Estructurado | Transformación |
|-------------|-------------------|----------------|
| `output_voltage_v` | `electrical.outputVoltage` | Directo |
| `generated_current_a` | `electrical.outputCurrent` | Directo |
| `active_power_kw` | `electrical.activePower` | Directo |
| `reactive_power_kvar` | `electrical.reactivePower` | Directo |
| N/A | `electrical.powerFactor` | **Calculado automáticamente** |

## Mapeo de Estados (operational_state → status)

| Estado del Molino | Estado SCADA | Descripción |
|-------------------|--------------|-------------|
| `operational` | `operational` | Turbina operando normalmente |
| `running` | `operational` | Turbina operando normalmente |
| `stopped` | `stopped` | Turbina detenida |
| `fault` | `fault` | Turbina con falla |
| `error` | `fault` | Turbina con error |
| `maintenance` | `maintenance` | Turbina en mantenimiento |
| `standby` | `standby` | Turbina en espera |
| `idle` | `standby` | Turbina inactiva |
| *otro* | `standby` | Cualquier otro valor → standby |

## Cálculos Automáticos

### 1. Power Factor (Factor de Potencia)

```javascript
const apparentPower = Math.sqrt(
  active_power_kw ** 2 + reactive_power_kvar ** 2
);

const powerFactor = apparentPower > 0 
  ? active_power_kw / apparentPower 
  : 0;
```

**Ejemplo**:
- `active_power_kw`: 2150.0
- `reactive_power_kvar`: 645.0
- `apparentPower`: √(2150² + 645²) = 2244.54
- `powerFactor`: 2150 / 2244.54 = **0.958**

### 2. Valores por Defecto

Si los siguientes campos NO están presentes en el JSON del molino, se usan estos valores:

| Campo | Valor por Defecto | Razón |
|-------|------------------|-------|
| `oilPressure` | 5.0 bar | Presión nominal típica |
| `oilLevel` | 85% | Nivel nominal de operación |

## Ubicación del Código de Transformación

La transformación se realiza en:

**Archivo**: `/services/mqttService.ts`  
**Función**: `transformFlatMessage(flatMsg: MqttFlatMessage): MqttTurbineMessage`

```typescript
private transformFlatMessage(flatMsg: MqttFlatMessage): MqttTurbineMessage {
  // Mapear estado
  const statusMap: Record<string, TurbineStatus> = {
    'operational': 'operational',
    'running': 'operational',
    'stopped': 'stopped',
    'fault': 'fault',
    'error': 'fault',
    'maintenance': 'maintenance',
    'standby': 'standby',
    'idle': 'standby'
  };
  
  const status = statusMap[flatMsg.operational_state.toLowerCase()] || 'standby';
  
  // Calcular factor de potencia
  const apparentPower = Math.sqrt(
    flatMsg.active_power_kw ** 2 + flatMsg.reactive_power_kvar ** 2
  );
  const powerFactor = apparentPower > 0 
    ? flatMsg.active_power_kw / apparentPower 
    : 0;
  
  // Retornar formato estructurado
  return {
    turbineId: String(flatMsg.turbine_id),
    timestamp: flatMsg.timestamp,
    environmental: {
      windSpeed: flatMsg.wind_speed_mps,
      windDirection: flatMsg.wind_direction_deg
    },
    mechanical: {
      rotorSpeed: flatMsg.rotor_speed_rpm,
      pitchAngle: flatMsg.blade_pitch_angle_deg,
      yawPosition: flatMsg.yaw_position_deg,
      vibration: flatMsg.vibrations_mms,
      gearboxTemperature: flatMsg.gear_temperature_c,
      bearingTemperature: flatMsg.bearing_temperature_c,
      oilPressure: 5.0, // Valor por defecto
      oilLevel: 85      // Valor por defecto
    },
    electrical: {
      outputVoltage: flatMsg.output_voltage_v,
      outputCurrent: flatMsg.generated_current_a,
      activePower: flatMsg.active_power_kw,
      reactivePower: flatMsg.reactive_power_kvar,
      powerFactor: powerFactor
    },
    status: status
  };
}
```

## Extensibilidad

### Agregar Oil Pressure y Oil Level al JSON del Molino

Si en el futuro el molino puede enviar `oil_pressure_bar` y `oil_level_percent`, actualizar la función:

```typescript
mechanical: {
  // ... otros campos
  oilPressure: flatMsg.oil_pressure_bar || 5.0,
  oilLevel: flatMsg.oil_level_percent || 85
}
```

### Agregar Nuevas Variables

1. Agregar el campo al tipo `MqttFlatMessage` en `/types/turbine.ts`
2. Agregar el mapeo en `transformFlatMessage()` en `/services/mqttService.ts`
3. Actualizar la interfaz estructurada si es necesario

## Validación de Datos

El sistema es **tolerante a errores**:
- ✅ Si `operational_state` no es reconocido → asume `standby`
- ✅ Si faltan campos → usa valores por defecto
- ✅ Si hay errores de parsing → se registra en consola pero no detiene el sistema

## Testing

Para probar el mapeo, usar el simulador incluido:

```bash
# Python
python simulator.py

# Node.js
node simulator.js
```

Ver `/docs/SIMULATOR_EXAMPLE.md` para más detalles.

---

**Última actualización**: 2025-11-02  
**Versión del sistema**: 1.0.0
