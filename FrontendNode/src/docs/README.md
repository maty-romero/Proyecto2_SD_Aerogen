# Documentación del Sistema de Monitoreo de Parque Eólico

Bienvenido a la documentación del sistema de monitoreo de parques eólicos. Esta documentación proporciona toda la información necesaria para comprender, integrar y probar el sistema.

## 📚 Estructura de la Documentación

La documentación se organiza en los siguientes archivos:

- **[README.md](./README.md)**: (Este archivo) Proporciona una descripción general de la documentación.
- **[INTEGRATION.md](./INTEGRATION.md)**: La guía completa para la integración con el sistema. Cubre todos los aspectos de la comunicación a través de MQTT y la API REST, incluyendo los formatos de datos y los tópicos.
- **[DATA_MODEL.md](./DATA_MODEL.md)**: Describe en detalle el modelo de datos, incluyendo los formatos plano y estructurado, el mapeo entre ellos y las estructuras de datos utilizadas en los gráficos.
- **[SIMULATORS.md](./SIMULATORS.md)**: Contiene el código fuente y las instrucciones para ejecutar los simuladores de backend en Python y Node.js, que generan datos de prueba realistas.

## 🎯 Guía por Caso de Uso

- **Para integrar un sistema SCADA/PLC**: Comience con [INTEGRATION.md](./INTEGRATION.md) para entender cómo enviar datos al sistema.
- **Para desarrolladores de frontend**: [DATA_MODEL.md](./DATA_MODEL.md) y [INTEGRATION.md](./INTEGRATION.md) son esenciales para comprender cómo fluyen los datos y cómo se estructuran.
- **Para testers y QA**: [SIMULATORS.md](./SIMULATORS.md) proporciona las herramientas para generar datos de prueba. [INTEGRATION.md](./INTEGRATION.md) ofrece el contexto sobre qué esperar.

## 🚀 Inicio Rápido

Para poner en marcha un entorno de prueba completo:

1.  **Iniciar el broker MQTT (EMQX)**:
    ```bash
    docker run -d --name emqx -p 1883:1883 -p 8083:8083 -p 18083:18083 emqx/emqx:latest
    ```

2.  **Ejecutar un simulador**:
    Vaya a la sección de [SIMULATORS.md](./SIMULATORS.md) y siga las instrucciones para ejecutar el simulador de Python o Node.js.

3.  **Iniciar la aplicación de frontend**:
    En el directorio raíz del frontend, ejecute:
    ```bash
    npm run dev
    ```

4.  **Conectar el frontend al broker**:
    Abra la aplicación en su navegador (normalmente `http://localhost:5173`) y utilice la interfaz de conexión de MQTT para conectarse a `ws://localhost:8083/mqtt`.

Después de estos pasos, debería ver los datos de las turbinas fluyendo en tiempo real en la interfaz de usuario.