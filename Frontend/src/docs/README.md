# Documentación - Sistema de Monitoreo de Parque Eólico

## 📚 Índice de Documentación

### 🚀 Inicio Rápido
| Documento | Descripción | Prioridad |
|-----------|-------------|-----------|
| [MQTT_INTEGRATION_SUMMARY.md](./MQTT_INTEGRATION_SUMMARY.md) | **Resumen ejecutivo de toda la integración MQTT** | ⭐⭐⭐ |
| [FLAT_JSON_FORMAT.md](./FLAT_JSON_FORMAT.md) | Vista general del formato JSON plano | ⭐⭐⭐ |

### 📊 Integración de Datos

#### Mediciones de Turbinas
| Documento | Descripción |
|-----------|-------------|
| [DATA_MAPPING.md](./DATA_MAPPING.md) | Mapeo detallado campo por campo de turbinas |

#### Estadísticas y Alertas
| Documento | Descripción |
|-----------|-------------|
| [STATS_AND_ALERTS_MQTT.md](./STATS_AND_ALERTS_MQTT.md) | **Formato completo de estadísticas del parque y alertas** |

#### Guía General
| Documento | Descripción |
|-----------|-------------|
| [INTEGRATION.md](./INTEGRATION.md) | Guía completa de integración (MQTT + API) |
| [MQTT_EXAMPLE.md](./MQTT_EXAMPLE.md) | Ejemplos de mensajes MQTT |

### 🧪 Testing y Simulación
| Documento | Descripción |
|-----------|-------------|
| [COMPLETE_SIMULATOR.md](./COMPLETE_SIMULATOR.md) | **Simulador completo: turbinas + estadísticas + alertas** |
| [SIMULATOR_EXAMPLE.md](./SIMULATOR_EXAMPLE.md) | Simuladores individuales (Python y Node.js) |

### 📈 Gráficos y Visualización
| Documento | Descripción |
|-----------|-------------|
| [CHARTS_DATA_STRUCTURE.md](./CHARTS_DATA_STRUCTURE.md) | Estructura de datos para gráficos de producción |

## 🎯 Guías por Caso de Uso

### Para Integrar el Sistema SCADA

1. **Leer primero**: [MQTT_INTEGRATION_SUMMARY.md](./MQTT_INTEGRATION_SUMMARY.md)
2. **Mediciones de turbinas**: [DATA_MAPPING.md](./DATA_MAPPING.md)
3. **Estadísticas y alertas**: [STATS_AND_ALERTS_MQTT.md](./STATS_AND_ALERTS_MQTT.md)
4. **Testing**: [COMPLETE_SIMULATOR.md](./COMPLETE_SIMULATOR.md)

### Para Desarrolladores Frontend

1. **Estructura general**: [INTEGRATION.md](./INTEGRATION.md)
2. **Formato de datos**: [FLAT_JSON_FORMAT.md](./FLAT_JSON_FORMAT.md)
3. **Gráficos**: [CHARTS_DATA_STRUCTURE.md](./CHARTS_DATA_STRUCTURE.md)

### Para Testing y QA

1. **Simulador completo**: [COMPLETE_SIMULATOR.md](./COMPLETE_SIMULATOR.md)
2. **Ejemplos MQTT**: [MQTT_EXAMPLE.md](./MQTT_EXAMPLE.md)
3. **Validación de datos**: [DATA_MAPPING.md](./DATA_MAPPING.md)

## 📡 Tópicos MQTT

El sistema se suscribe a 3 tópicos principales:

### 1. Mediciones de Turbinas
```
Tópico: windfarm/turbines/{turbine_id}/measurements
QoS: 1
Formato: JSON plano
Frecuencia: 5-10 segundos
```

**Documentación**: [DATA_MAPPING.md](./DATA_MAPPING.md)

### 2. Estadísticas del Parque
```
Tópico: windfarm/stats
QoS: 1
Formato: JSON plano
Frecuencia: 5-60 segundos
```

**Documentación**: [STATS_AND_ALERTS_MQTT.md](./STATS_AND_ALERTS_MQTT.md)

### 3. Alertas
```
Tópico: windfarm/alerts
QoS: 1
Formato: JSON plano
Frecuencia: Event-driven
```

**Documentación**: [STATS_AND_ALERTS_MQTT.md](./STATS_AND_ALERTS_MQTT.md)

## 🔄 Flujo de Datos

```
┌─────────────┐
│  SCADA/PLC  │
│   Sistema   │
└──────┬──────┘
       │ Publica JSON plano
       ↓
┌─────────────┐
│  Broker     │
│  EMQX       │
└──────┬──────┘
       │ Distribuye mensajes
       ↓
┌─────────────┐
│  Frontend   │
│  React      │
└──────┬──────┘
       │ Transforma automáticamente
       ↓
┌─────────────┐
│  Componentes│
│  UI         │
└─────────────┘
```

## 📋 Formatos Soportados

### JSON Plano (Recomendado)
✅ Single-level JSON  
✅ Snake_case  
✅ Unidades explícitas  
✅ Fácil de generar desde PLCs  

**Ejemplo**:
```json
{
  "turbine_id": 5,
  "active_power_kw": 2150.0,
  "wind_speed_mps": 12.5
}
```

### Transformación Automática

El frontend transforma automáticamente a formato estructurado:

```json
{
  "turbineId": "5",
  "electrical": {
    "activePower": 2150.0
  },
  "environmental": {
    "windSpeed": 12.5
  }
}
```

## 🧪 Testing

### Simulador Completo (Recomendado)

```bash
# Instalar dependencias
pip install paho-mqtt

# Ejecutar simulador
python complete_simulator.py
```

Ver: [COMPLETE_SIMULATOR.md](./COMPLETE_SIMULATOR.md)

### Simuladores Individuales

Ver: [SIMULATOR_EXAMPLE.md](./SIMULATOR_EXAMPLE.md)

## 📊 Datos Procesados

### Turbinas (24 unidades)
- ✅ Variables mecánicas (8 variables)
- ✅ Variables eléctricas (5 variables)
- ✅ Variables ambientales (2 variables)
- ✅ Estados SCADA (5 estados)

### Estadísticas del Parque
- ✅ Producción total en tiempo real
- ✅ Contadores por estado
- ✅ Promedios eléctricos
- ✅ Estadísticas de viento
- ✅ Histórico 24 horas

### Alertas
- ✅ Clasificación por tipo (4 tipos)
- ✅ Severidad (3 niveles)
- ✅ Detalles técnicos
- ✅ Estados (acknowledged, resolved)

## 🎨 Visualización

### Dashboard Principal
- Tarjetas de resumen (KPIs)
- Grid de turbinas (24 unidades)
- Heatmaps de variables
- Rosa de vientos

### Sección Producción
- Gráfico de área (24h)
- Gráfico de barras (semanal)
- Estadísticas agregadas

### Panel de Alertas
- Lista en tiempo real
- Filtros por severidad
- Detalles expandibles

### Diálogos de Detalle
- Información completa de turbina
- Todas las variables
- Rosa de vientos individual

## ⚙️ Configuración

### Broker EMQX (Desarrollo)
```bash
docker run -d --name emqx \
  -p 1883:1883 \
  -p 8083:8083 \
  -p 18083:18083 \
  emqx/emqx:latest
```

### Frontend
```typescript
const { turbines, alerts, farmStats } = useWindFarmData({
  mqttBrokerUrl: 'ws://localhost:8083/mqtt',
  autoConnect: true
});
```

## 🔒 Producción

Para producción, configurar:

1. **TLS/SSL**: `wss://broker.ejemplo.com:8084/mqtt`
2. **Autenticación**: Username + Password
3. **ACLs**: Permisos por tópico en EMQX
4. **Firewall**: Restringir acceso al broker

Ver: [INTEGRATION.md](./INTEGRATION.md) - Sección "Seguridad"

## 📞 Soporte Técnico

### Por Componente

| Componente | Documentación |
|------------|---------------|
| Mediciones de turbinas | [DATA_MAPPING.md](./DATA_MAPPING.md) |
| Estadísticas | [STATS_AND_ALERTS_MQTT.md](./STATS_AND_ALERTS_MQTT.md) |
| Alertas | [STATS_AND_ALERTS_MQTT.md](./STATS_AND_ALERTS_MQTT.md) |
| Gráficos | [CHARTS_DATA_STRUCTURE.md](./CHARTS_DATA_STRUCTURE.md) |
| Testing | [COMPLETE_SIMULATOR.md](./COMPLETE_SIMULATOR.md) |

### Debugging

1. **Verificar conexión MQTT**: Console del navegador
2. **Ver mensajes MQTT**: EMQX Dashboard → WebSocket Test
3. **Validar JSON**: Usar simulador con datos conocidos
4. **Logs del frontend**: DevTools → Console

## ✅ Checklist de Integración

### Preparación
- [ ] Broker EMQX instalado y funcionando
- [ ] Puertos abiertos (1883, 8083, 18083)
- [ ] Frontend conectado al broker

### SCADA/PLC
- [ ] Publicar mediciones de turbinas cada 5-10 seg
- [ ] Publicar estadísticas del parque cada 5-60 seg
- [ ] Publicar alertas cuando ocurran
- [ ] Usar formato JSON plano documentado

### Testing
- [ ] Simulador completo ejecutándose
- [ ] Datos visibles en frontend
- [ ] Alertas apareciendo en tiempo real
- [ ] Gráficos actualizándose

### Validación
- [ ] Todas las turbinas reportando
- [ ] Estados mapeados correctamente
- [ ] Producción horaria completa (24 valores)
- [ ] Alertas con severidad correcta

## 🚀 Quick Start

```bash
# 1. Iniciar broker EMQX
docker run -d --name emqx -p 1883:1883 -p 8083:8083 emqx/emqx:latest

# 2. Ejecutar simulador
pip install paho-mqtt
python complete_simulator.py

# 3. Abrir frontend
npm run dev

# 4. Conectar en navegador
http://localhost:5173
# Conectar a: ws://localhost:8083/mqtt
```

---

**Estado**: ✅ Sistema completo y documentado  
**Última actualización**: 2025-11-03  
**Versión**: 1.0.0  
**Mantenedor**: Equipo de Desarrollo Parque Eólico Comodoro Rivadavia
