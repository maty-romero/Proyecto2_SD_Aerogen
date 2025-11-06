# Guía de Integración del Sistema

Esta guía proporciona toda la información necesaria para integrar un sistema externo (como un SCADA o PLC) con el sistema de monitoreo de parques eólicos. La comunicación se realiza principalmente a través de MQTT para datos en tiempo real y, opcionalmente, a través de una API REST para datos históricos.

## Arquitectura de Comunicación

- **MQTT**: Para la transmisión en tiempo real de mediciones de turbinas, estadísticas del parque y alertas.
- **API REST**: Para solicitar datos históricos y realizar acciones como reconocer alertas.

## Integración MQTT

El sistema se suscribe a tópicos específicos en un broker MQTT para recibir datos en tiempo real. El formato de los mensajes es JSON plano (single-level) para simplificar la generación desde sistemas embebidos.

### Configuración del Broker

- **URL del Broker**: El frontend se conecta a una URL de WebSocket (ej. `ws://localhost:8083/mqtt`).
- **Tópicos**: El sistema se suscribe a tres tópicos principales.

### Tópicos y Formatos de Datos

#### 1. Mediciones de Turbinas

- **Tópico**: `windfarm/turbines/{turbine_id}/clean_telemetry`
- **Frecuencia recomendada**: 5-10 segundos
- **Descripción**: Publica los datos de telemetría de una turbina individual.

**Formato JSON Plano:**

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

#### 2. Estadísticas del Parque

- **Tópico**: `windfarm/stats`
- **Frecuencia recomendada**: 5-60 segundos
- **Descripción**: Publica datos agregados de todo el parque eólico.

**Formato JSON Plano:**

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

#### 3. Alertas del Sistema

- **Tópico**: `windfarm/alerts`
- **Frecuencia**: Basada en eventos (solo cuando ocurre una alerta).
- **Descripción**: Publica alertas generadas en el parque.

**Formato JSON Plano:**

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

## Integración con API REST (Opcional)

El sistema también puede interactuar con una API REST para obtener datos históricos.

### Endpoints

- `GET /api/turbines/{turbineId}/history`: Devuelve el historial de una turbina específica.
- `GET /api/alerts/history`: Devuelve un historial paginado de alertas.
- `POST /api/alerts/{alertId}/acknowledge`: Marca una alerta como reconocida.
- `POST /api/alerts/{alertId}/resolve`: Marca una alerta como resuelta.

Para más detalles sobre el modelo de datos y las transformaciones automáticas, consulte [DATA_MODEL.md](./DATA_MODEL.md).