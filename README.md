# Proyecto2_SD

### Sistema Monitoreo distribuido de aerogeneradores 

---

## Ejecución del Proyecto (con Docker)

Esta guía explica cómo levantar todo el backend del sistema utilizando Docker y Docker Compose. El entorno incluye el broker MQTT, la base de datos, el simulador de turbinas y el nodo de estadísticas.

### Prerrequisitos

*   Tener instalado [Docker](https://www.docker.com/get-started).
*   Tener instalado [Docker Compose](https://docs.docker.com/compose/install/).

### Pasos para la Ejecución

1.  **Clonar el repositorio** y asegurarse de estar en la raíz del proyecto, donde se encuentra el archivo `docker-compose.yml`.

2.  **Levantar todos los servicios** con un solo comando. Este comando construirá las imágenes de Docker para los servicios de Python y lanzará todos los contenedores en el orden correcto.

    ```bash
    docker-compose up --build
    ```

    Si prefieres ejecutarlo en segundo plano (sin ver los logs en la terminal), usa la opción `-d`:

    ```bash
    docker-compose up --build -d
    ```

### Servicios Iniciados

Este comando levantará 4 contenedores que trabajarán en conjunto:
-   **`emqx`**: El broker MQTT. El dashboard web estará disponible en `http://localhost:18083`.
-   **`mongo`**: La base de datos MongoDB para persistencia.
-   **`simulator`**: El simulador de turbinas (`TurbineTelemetry`) que genera y publica los datos.
-   **`statnode`**: El nodo de estadísticas que consume los datos, los guarda en `mongo` y publica métricas procesadas.

### Detener el Sistema

Para detener todos los contenedores, presiona `Ctrl+C` en la terminal donde se están ejecutando. Si los iniciaste en segundo plano, usa el siguiente comando:

```bash
docker-compose down
```
