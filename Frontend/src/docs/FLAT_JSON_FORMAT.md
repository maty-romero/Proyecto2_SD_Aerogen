# Formato JSON Plano - Integración con Molinos

## ✅ Cambio Implementado

El sistema ahora procesa mensajes MQTT en **formato JSON plano (single-level)** que coincide exactamente con el formato enviado por los molinos.

## 📋 Formato Esperado

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

## 🔄 Transformación Automática

El frontend automáticamente:

1. ✅ **Convierte** del formato plano al formato estructurado interno
2. ✅ **Calcula** `powerFactor` a partir de `active_power_kw` y `reactive_power_kvar`
3. ✅ **Mapea** `operational_state` a los estados SCADA
4. ✅ **Asigna** valores por defecto para `oilPressure` (5.0) y `oilLevel` (85)
5. ✅ **Usa** `turbine_name` y `capacity_mw` del mensaje

## 📂 Archivos Modificados

### Tipos
- `/types/turbine.ts` - Agregado `MqttFlatMessage` interface

### Servicios
- `/services/mqttService.ts` - Agregada función `transformFlatMessage()`

### Hooks
- `/hooks/useWindFarmData.ts` - Actualizado para usar metadata (name, capacity)

### Componentes
- `/components/MqttConnection.tsx` - Actualizada descripción de tópicos

### Documentación
- `/docs/DATA_MAPPING.md` - **NUEVO** - Mapeo detallado de campos
- `/docs/SIMULATOR_EXAMPLE.md` - Actualizado con formato plano
- `/docs/INTEGRATION.md` - Actualizado con formato plano
- `/docs/FLAT_JSON_FORMAT.md` - **NUEVO** - Este archivo

## 🧪 Testing

### Simulador Python

```bash
python simulator.py
```

### Simulador Node.js

```bash
node simulator.js
```

Ambos simuladores generan datos en el formato plano esperado.

## 📊 Estados Aceptados

El campo `operational_state` acepta los siguientes valores:

| Valor en JSON | Estado Mapeado | Color |
|---------------|----------------|-------|
| `operational` | Operativa | 🟢 Verde |
| `running` | Operativa | 🟢 Verde |
| `stopped` | Detenida | ⚫ Gris |
| `fault` | Falla | 🔴 Rojo |
| `error` | Falla | 🔴 Rojo |
| `maintenance` | Mantenimiento | 🟡 Amarillo |
| `standby` | En Espera | 🔵 Azul |
| `idle` | En Espera | 🔵 Azul |
| *otro valor* | En Espera | 🔵 Azul |

## 🔌 Tópicos MQTT

### Mediciones de Turbinas
- **Tópico**: `windfarm/turbines/{turbine_id}/measurements`
- **Ejemplo**: `windfarm/turbines/5/measurements`
- **QoS**: 1
- **Formato**: JSON plano (ver arriba)

### Alertas (futuro)
- **Tópico**: `windfarm/alerts`
- **QoS**: 1

### Estadísticas (futuro)
- **Tópico**: `windfarm/stats`
- **QoS**: 1

## 🚀 Próximos Pasos

### Opción 1: Agregar Oil Pressure y Oil Level

Si los molinos pueden enviar estos datos, agregar al JSON:

```json
{
  ...
  "oil_pressure_bar": 5.2,
  "oil_level_percent": 87.5,
  ...
}
```

Y actualizar la transformación en `mqttService.ts`:

```typescript
oilPressure: flatMsg.oil_pressure_bar || 5.0,
oilLevel: flatMsg.oil_level_percent || 85
```

### Opción 2: Usar Broker EMQX Real

1. Instalar EMQX:
   ```bash
   docker run -d --name emqx \
     -p 1883:1883 \
     -p 8083:8083 \
     -p 18083:18083 \
     emqx/emqx:latest
   ```

2. Configurar molinos para publicar a:
   - Host: `localhost` (o IP del servidor)
   - Puerto: `1883` (MQTT) o `8083` (WebSocket)
   - Tópico: `windfarm/turbines/{turbine_id}/measurements`

3. En el frontend, conectar a:
   - `ws://localhost:8083/mqtt` (desarrollo)
   - `ws://<ip-servidor>:8083/mqtt` (producción)

## 📖 Documentación Relacionada

- `/docs/DATA_MAPPING.md` - Mapeo detallado campo por campo
- `/docs/SIMULATOR_EXAMPLE.md` - Ejemplos de simuladores
- `/docs/INTEGRATION.md` - Guía completa de integración
- `/docs/MQTT_EXAMPLE.md` - Ejemplos de mensajes MQTT

## ✨ Ventajas del Formato Plano

1. **Simplicidad**: Más fácil de generar desde PLCs/SCADA
2. **Sin anidamiento**: Menos propenso a errores de serialización
3. **Nomenclatura clara**: Snake_case con unidades explícitas
4. **Autocontenido**: Incluye toda la metadata necesaria
5. **Flexible**: Fácil de extender con nuevos campos

---

**Última actualización**: 2025-11-02  
**Versión**: 1.0.0
