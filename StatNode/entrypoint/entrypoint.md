
# Funcionamiento entrypoint:

1. Inicia la API de Flask en ambos nodos. Esto es importante para que la réplica pueda ser monitoreada si se convierte en el nodo principal.

2. Si el rol es replica, entra en un bucle que usa curl para hacer una petición HTTP al endpoint /health del servicio statnode (el nombre del contenedor principal).

3. Si la petición falla (el nodo primario no responde), el bucle se rompe y la réplica procede a ejecutar main.py para empezar a procesar los mensajes de MQTT.

4. Si el rol es primary, el script salta el bucle y ejecuta main.py directamente.