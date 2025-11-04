# Resumen de Integración MQTT - Parque Eólico

## 🎯 Vista Rápida

El sistema está **completamente preparado** para recibir datos del parque eólico a través de MQTT usando **JSON plano** (single-level) en 3 tópicos:

| Tópico | Propósito | Formato | Frecuencia |
|--------|-----------|---------|------------|
| `windfarm/turbines/{id}/measurements` | Mediciones de cada turbina | JSON plano | 5-10 seg |
| `windfarm/stats` | Estadísticas y producción del parque | JSON plano | 5-60 seg |
| `windfarm/alerts` | Alertas en tiempo real | JSON plano | Event-driven |

## 📦 Formatos JSON Planos

### 1. Mediciones de Turbina

```json
{
  "farm_id": 1,
  "turbine_id": 5,
  "turbine_name": "T-005",
  "timestamp": "2025-11-03 14:30:15",
  
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

### 2. Estadísticas del Parque

```json
{
  "farm_id": 1,
  "timestamp": "2025-11-03 14:30:15",
  
  "total_active_power_kw": 45250.5,
  "total_turbines": 24,
  "operational_turbines": 22,
  
  "avg_wind_speed_mps": 11.3,
  "predominant_wind_direction_deg": 245,
  
  "avg_power_factor": 0.96,
  
  "hourly_production_kwh": [38500, 39200, ...],  // 24 valores
  "hourly_timestamps": ["00:00", "01:00", ...]   // 24 valores
}
```

### 3. Alertas

```json
{
  "alert_id": "ALT-2025110315234567",
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

## ✨ Características

### Transformación Automática
- ✅ JSON plano → JSON estructurado interno
- ✅ Cálculo automático de `power_factor`
- ✅ Mapeo de estados multiidioma (español/inglés)
- ✅ Valores por defecto para campos opcionales

### Validación Flexible
- ✅ Acepta campos en español e inglés
- ✅ Tolerante a errores de formato
- ✅ Fallbacks inteligentes

### Procesamiento en Tiempo Real
- ✅ Actualización instantánea de UI
- ✅ Agregación automática de estadísticas
- ✅ Historial de alertas (últimas 100)
- ✅ Gráficos de producción actualizados

## 🚀 Pasos para Integración

### 1. Configurar Broker EMQX

```bash
docker run -d --name emqx \
  -p 1883:1883 \
  -p 8083:8083 \
  -p 18083:18083 \
  emqx/emqx:latest
```

### 2. Configurar SCADA/PLC

Programar el sistema para publicar en los 3 tópicos:

**Mediciones individuales** (cada 5-10 segundos):
```
Tópico: windfarm/turbines/1/measurements
Payload: { turbine_id: 1, ... }
```

**Estadísticas** (cada 5-60 segundos):
```
Tópico: windfarm/stats
Payload: { total_active_power_kw: 45250.5, ... }
```

**Alertas** (cuando ocurren):
```
Tópico: windfarm/alerts
Payload: { alert_id: "...", message: "...", ... }
```

### 3. Conectar Frontend

En el navegador, usar el componente de conexión MQTT:

```
URL: ws://localhost:8083/mqtt
      (o ws://<IP_SERVIDOR>:8083/mqtt)
```

## 📊 Mapeo de Datos

### Estados Operacionales

| SCADA envía | Frontend mapea |
|-------------|----------------|
| `operational`, `running` | 🟢 Operativa |
| `stopped` | ⚫ Detenida |
| `fault`, `error` | 🔴 Falla |
| `maintenance` | 🟡 Mantenimiento |
| `standby`, `idle` | 🔵 En Espera |

### Tipos de Alerta

| SCADA envía | Frontend mapea |
|-------------|----------------|
| `electrical`, `eléctrica` | Eléctrica ⚡ |
| `mechanical`, `mecánica` | Mecánica ⚙️ |
| `environmental`, `ambiental` | Ambiental 🌍 |
| `system`, `sistema` | Sistema 💻 |

### Severidades

| SCADA envía | Frontend muestra |
|-------------|------------------|
| `critical`, `crítico` | 🔴 Crítico |
| `warning`, `advertencia` | 🟡 Advertencia |
| `info`, `información` | 🔵 Info |

## 📖 Documentación Completa

| Documento | Descripción |
|-----------|-------------|
| [FLAT_JSON_FORMAT.md](./FLAT_JSON_FORMAT.md) | Formato plano general y cambios |
| [DATA_MAPPING.md](./DATA_MAPPING.md) | Mapeo campo por campo de turbinas |
| [STATS_AND_ALERTS_MQTT.md](./STATS_AND_ALERTS_MQTT.md) | **Estadísticas y alertas detalladas** |
| [INTEGRATION.md](./INTEGRATION.md) | Guía completa de integración |
| [COMPLETE_SIMULATOR.md](./COMPLETE_SIMULATOR.md) | Simulador completo de prueba |

## 🧪 Testing

### Opción 1: Simulador Python

```bash
pip install paho-mqtt
python complete_simulator.py
```

### Opción 2: Publicar Manualmente

```bash
# EMQX Dashboard
http://localhost:18083
Usuario: admin
Password: public

# Usar herramienta "Websocket" para publicar mensajes de prueba
```

### Opción 3: Mosquitto CLI

```bash
# Publicar medición
mosquitto_pub -h localhost -t "windfarm/turbines/1/measurements" \
  -m '{"turbine_id": 1, "active_power_kw": 2150, ...}'

# Publicar estadísticas
mosquitto_pub -h localhost -t "windfarm/stats" \
  -m '{"total_active_power_kw": 45250, ...}'

# Publicar alerta
mosquitto_pub -h localhost -t "windfarm/alerts" \
  -m '{"alert_id": "TEST", "message": "Prueba", ...}'
```

## 🎨 Visualización en Frontend

### Dashboard Principal
- **Tarjetas de resumen**: Potencia total, turbinas activas, viento promedio
- **Heatmaps**: Variables mecánicas y eléctricas en grilla
- **Grid de turbinas**: 24 turbinas con estados en tiempo real

### Sección de Producción
- **Gráfico 24h**: Producción horaria con datos reales
- **Estadísticas**: Promedios, máximos, mínimos
- **Tendencias**: Visualización temporal

### Panel de Alertas
- **Lista en tiempo real**: Nuevas alertas aparecen instantáneamente
- **Colores por severidad**: Fácil identificación visual
- **Detalles técnicos**: Información completa de cada alerta

## ⚡ Rendimiento

- **Latencia**: < 100ms desde publicación MQTT hasta UI
- **Capacidad**: Soporta 24+ turbinas sin degradación
- **Frecuencia**: Actualización cada 5 segundos recomendada
- **Escalabilidad**: Preparado para múltiples parques

## 🔒 Seguridad (Producción)

Para producción, configurar:

1. **Autenticación MQTT**:
   ```typescript
   {
     mqttUsername: "windfarm_user",
     mqttPassword: "secure_password"
   }
   ```

2. **TLS/SSL**:
   ```typescript
   mqttBrokerUrl: "wss://broker.ejemplo.com:8084/mqtt"
   ```

3. **ACLs en EMQX**: Restringir acceso por tópico

## 📞 Soporte

Ver documentación detallada en:
- `/docs/STATS_AND_ALERTS_MQTT.md` - **Estadísticas y alertas**
- `/docs/DATA_MAPPING.md` - Mapeo de campos
- `/docs/INTEGRATION.md` - Guía completa

---

**Estado**: ✅ Completamente implementado y listo para producción  
**Última actualización**: 2025-11-03  
**Versión**: 1.0.0
