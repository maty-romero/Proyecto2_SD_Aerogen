# Sistema de Monitoreo de Parque Eólico

Sistema de visualización de estadísticas en tiempo real para monitoreo de parques eólicos con integración MQTT/EMQX y API REST.

## 🚀 Características

- ✅ **Monitoreo en Tiempo Real**: Visualización de variables eléctricas, mecánicas y ambientales
- ✅ **Integración MQTT/EMQX**: Datos en tiempo real a través de broker MQTT
- ✅ **API REST**: Consulta de históricos de turbinas y alertas
- ✅ **Heatmaps Visuales**: 8 tipos de análisis visual del parque
- ✅ **Estados SCADA**: Operativa, Detenida, Falla, Mantenimiento, Standby
- ✅ **Modo Claro/Oscuro**: Soporte completo para temas
- ✅ **Responsive**: Optimizado para desktop y mobile

## 📊 Variables Monitoreadas

### Variables Mecánicas
- RPM del rotor
- Ángulo de pitch
- Posición yaw
- Vibraciones
- Temperatura de engranaje
- Temperatura de rodamientos
- Presión y nivel de aceite

### Variables Eléctricas
- Voltaje de salida
- Corriente generada
- Potencia activa
- Potencia reactiva
- Factor de potencia

### Variables Ambientales (por molino)
- Velocidad del viento
- Dirección del viento

## 🗂️ Estructura del Proyecto

```
├── components/
│   ├── WindFarmOverview.tsx      # Vista general del parque
│   ├── TurbineGrid.tsx           # Grid de turbinas
│   ├── TurbineDetailDialog.tsx   # Detalles de turbina individual
│   ├── Heatmaps.tsx              # Análisis visuales (NUEVO)
│   ├── MqttConnection.tsx        # Gestión de conexión MQTT (NUEVO)
│   ├── ProductionCharts.tsx      # Gráficos de producción
│   ├── AlertsPanel.tsx           # Panel de alertas
│   └── ui/                       # Componentes ShadCN
├── services/
│   ├── mqttService.ts            # Servicio MQTT (NUEVO)
│   └── apiService.ts             # Servicio API REST (NUEVO)
├── hooks/
│   └── useWindFarmData.ts        # Hook personalizado (NUEVO)
├── types/
│   └── turbine.ts                # Tipos TypeScript
├── utils/
│   └── turbineData.ts            # Generación de datos mock
└── docs/
    └── INTEGRATION.md            # Guía de integración (NUEVO)
```

## 🔧 Cambios Recientes

### ✅ Eliminado
- ❌ Sección "Entorno" de los detalles de turbina individual
- ❌ Variables: Temperatura ambiente y Presión atmosférica (ya no se sensarán por molino)

### ✅ Agregado
- ✨ **Servicios de Integración**:
  - `mqttService.ts`: Conexión con broker EMQX
  - `apiService.ts`: Consultas a API REST para históricos
- ✨ **Hook Personalizado**: `useWindFarmData` para gestión completa de datos
- ✨ **Componente de Conexión**: Interfaz para configurar MQTT
- ✨ **8 Heatmaps Visuales**:
  1. Generación de Energía por Turbina
  2. Eficiencia Relativa (%)
  3. Factor de Potencia
  4. Temperatura Caja de Cambios
  5. Nivel de Vibraciones
  6. Disponibilidad (%)
  7. Velocidad del Viento
  8. Estado de Turbinas (SCADA)

### ✅ Modificado
- 📝 `types/turbine.ts`: Nuevos tipos para MQTT y API
- 📝 `WindFarmOverview.tsx`: Elimina temperatura y presión atmosférica
- 📝 `TurbineDetailDialog.tsx`: Elimina tab "Entorno", mantiene solo 3 tabs
- 📝 `App.tsx`: Nueva tab "Análisis" con heatmaps

## 🌐 Integración MQTT/EMQX

### Tópicos Suscritos

```
windfarm/turbines/{turbineId}/measurements  → Mediciones de cada molino
windfarm/alerts                              → Alertas del sistema
windfarm/stats                               → Estadísticas generales
```

### Ejemplo de Uso

```typescript
import { useWindFarmData } from './hooks/useWindFarmData';

function MyComponent() {
  const {
    turbines,
    alerts,
    isConnected,
    connect,
    disconnect,
  } = useWindFarmData({
    mqttBrokerUrl: 'ws://localhost:8083/mqtt',
    mqttUsername: 'admin',
    mqttPassword: 'password',
    autoConnect: true,
  });

  return <div>{/* Tu UI */}</div>;
}
```

## 🔌 API REST para Históricos

### Endpoints

```
GET /api/turbines/{turbineId}/history      → Histórico de turbina
GET /api/turbines/history                  → Histórico de todas
GET /api/alerts/history                    → Histórico de alertas
POST /api/alerts/{alertId}/acknowledge     → Reconocer alerta
POST /api/alerts/{alertId}/resolve         → Resolver alerta
```

## 📦 Instalación

```bash
# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm run dev

# Build para producción
npm run build
```

## 🐳 Docker EMQX (Opcional)

```bash
docker run -d --name emqx \
  -p 1883:1883 \
  -p 8083:8083 \
  -p 8084:8084 \
  -p 18083:18083 \
  emqx/emqx:latest
```

Acceso al dashboard: http://localhost:18083
- Usuario: admin
- Contraseña: public

## 📖 Documentación

- **Guía de Integración**: [docs/INTEGRATION.md](docs/INTEGRATION.md)
- **Tipos de Datos**: [types/turbine.ts](types/turbine.ts)
- **Servicios**: [services/](services/)

## 🎨 Heatmaps Disponibles

### Tab: Potencia
- **Generación de Energía**: Visualiza la potencia activa de cada turbina
- **Factor de Potencia**: Calidad de la energía generada

### Tab: Eficiencia
- **Eficiencia Relativa**: % de utilización respecto a capacidad
- **Disponibilidad**: Uptime de cada turbina

### Tab: Mecánicas
- **Temperatura Caja de Cambios**: Monitoreo térmico (colores invertidos)
- **Vibraciones**: Detección de anomalías mecánicas (colores invertidos)

### Tab: Operacionales
- **Velocidad del Viento**: Distribución del recurso eólico
- **Estado de Turbinas**: Visualización del estado SCADA

## 🎯 Próximos Pasos para Integración

1. **Configurar Backend MQTT**:
   - Implementar publicación de datos en tópicos
   - Configurar permisos y ACL en EMQX

2. **Implementar API REST**:
   - Crear endpoints para históricos
   - Conectar con base de datos (InfluxDB, TimescaleDB, etc.)

3. **Conectar Frontend**:
   - Actualizar URLs de broker y API
   - Probar flujo completo de datos

4. **Personalizar**:
   - Ajustar umbrales de alertas
   - Configurar colores de heatmaps
   - Añadir más métricas según necesidad

## 🛠️ Tecnologías

- **React 18** + **TypeScript**
- **Tailwind CSS v4.0**
- **ShadCN UI** - Componentes
- **Recharts** - Gráficos
- **Lucide React** - Iconos
- **MQTT.js** - Cliente MQTT (para integración)

## 📝 Notas Importantes

- Los datos actualmente son mock/simulados
- La conexión MQTT está preparada pero requiere implementación del backend
- Los servicios tienen datos de ejemplo para facilitar desarrollo
- Las variables de temperatura y presión atmosférica ya NO se sensarán por molino individual

## 🤝 Contribuir

Este proyecto está listo para integración con sistemas reales de SCADA/IoT. 

Para más información sobre integración, consultar [docs/INTEGRATION.md](docs/INTEGRATION.md)

## 📄 Licencia

Proyecto propietario - Todos los derechos reservados

---

**Última actualización**: Octubre 2025
**Versión**: 2.0 - Con integración MQTT/API y Heatmaps
