#!/bin/bash

# Usar el puerto definido en las variables de entorno, o 5000 por defecto
INTERNAL_PORT=${FLASK_INTERNAL_PORT:-5000}

# Iniciar la API de Flask en segundo plano
echo "Starting Flask API server on internal port $INTERNAL_PORT..."
python -m flask run --host=0.0.0.0 --port="$INTERNAL_PORT" &

# Esperar un momento para que la API se inicie
sleep 5

# Lógica de Failover
if [ "$STATNODE_ROLE" = "replica" ]; then
  echo "Running as a REPLICA. Monitoring primary node..."
  # El nodo primario siempre se llama 'statnode' y su puerto interno es 5000
  # según docker-compose.yml. No usamos la variable aquí para mantenerlo fijo.
  PRIMARY_NODE_URL="http://statnode:5000/health" 
  
  while true; do
    # Usamos curl para verificar la salud del nodo primario
    # Usamos nuestro script de Python en lugar de curl
    if python /app/StatNode/entrypoint/check_primary.py "$PRIMARY_NODE_URL"; then
      echo "Primary node is UP. Waiting..."
    else
      echo "Primary node is DOWN. Taking over..."
      # El primario cayó, la réplica inicia su trabajo
      break
    fi
    # Esperar antes de volver a verificar
    sleep 15
  done
fi

echo "Starting main MQTT processing logic..."
# Ejecutar el consumidor de MQTT (main.py)
python /app/StatNode/main.py
