from flask import Flask, request, jsonify, g
from StatNode.Auth.verify_key import *
import requests
import paho.mqtt.client as mqtt
from datetime import datetime
import json


app = Flask(__name__)

# URL base de la API del broker EMQX
BROKER_API_URL = 'http://localhost:18083/api/v5'
API_KEY = 'your_api_key'  # API key para autenticar las peticiones al Broker

# Configuración de MQTT
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_KEEP_ALIVE_INTERVAL = 60

# Contraseña común para todas las turbinas
COMMON_PASSWORD = 'turbine_password'

# Tópicos de interés
TURBINE_ALERT_TOPIC = "farms/{farm_id}/alerts/turbines/{turbine_id}"
WEATHER_ALERT_TOPIC = "farms/{farm_id}/alerts/weather"
CLEAN_TELEMETRY_TOPIC = "farms/{farm_id}/turbines/{turbine_id}/clean_telemetry"

# Encabezados para autenticación
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

@app.route('/')
def hello_geek():
    return '<h1>Hello from Flask & Docker</h2>'

# Endpoint Testing protegido con API Key para obtener alertas 
"""
Para probar en Postman:
1. Crear una nueva request GET a http://localhost:5000/protected
2. En la pestaña Headers, añadir un header -> Authorization > Auth Type API Key:
   Key: x-api-key
   Value: RAW_API_KEY_GENERADA --> Ver Docs 
   Add to: Header
"""

@app.route("/protected", methods=['GET'])
@require_api_key()
def get_alerts():
    # ejemplo: retornar alerts ficticias
    return jsonify({"message": "You have accessed a protected endpoint!",
        "alerts": [
            {"id": 1, "message": "High wind speed detected", "turbine": "T-001"},
            {"id": 2, "message": "Temperature threshold exceeded", "turbine": "T-002"}
        ]
    })
        
# Función para hacer solicitudes a la API del Broker EMQX
def make_request(endpoint):
    url = f"{BROKER_API_URL}/{endpoint}"
    response = requests.get(url, headers=headers)
    return response.json()

# Función de retorno de mensaje (callback MQTT)
def on_message(client, userdata, msg):
    """
    Callback que maneja los mensajes de los tópicos suscritos.
    """
    print(f"Mensaje recibido en el tópico {msg.topic}: {msg.payload.decode()}")
    # Procesar el mensaje recibido (alertas o telemetría) y guardar en la base de datos
    alert_data = {
        "topic": msg.topic,
        "message": msg.payload.decode(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    #se puede guradar en la BD
    print(f"Alerta procesada: {alert_data}")

# Crear cliente MQTT para turbina específica
def create_mqtt_client(farm_id, turbine_id):
    client_id = f"F-{farm_id}-T{turbine_id}"  # Formato de client_id único
    mqtt_client = mqtt.Client(client_id=client_id)
    mqtt_client.username_pw_set(client_id, COMMON_PASSWORD)  # Autenticación usando client_id
    mqtt_client.on_message = on_message
    return mqtt_client


# Conectar y suscribir a los tópicos de alerta
def connect_and_subscribe(farm_id, turbine_id):
    mqtt_client = create_mqtt_client(farm_id, turbine_id)
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEP_ALIVE_INTERVAL)

    # Suscripción a los tópicos de alerta de turbina y climatológicas
    turbine_alert_topic = TURBINE_ALERT_TOPIC.format(farm_id=farm_id, turbine_id=turbine_id)
    weather_alert_topic = WEATHER_ALERT_TOPIC.format(farm_id=farm_id)

    mqtt_client.subscribe(turbine_alert_topic)
    mqtt_client.subscribe(weather_alert_topic)
    print(f"Suscrito a los tópicos: {turbine_alert_topic}, {weather_alert_topic}")

    # Iniciar el loop MQTT para recibir mensajes
    mqtt_client.loop_start()

    return mqtt_client


# Endpoint para obtener la información de una turbina específica
@app.route('/api/v1/turbines/<int:turbine_id>', methods=['GET'])
def get_turbine_info(turbine_id):
    """
    Endpoint para obtener información sobre una turbina específica.
    """
    try:
        turbine_info = make_request(f'turbines/{turbine_id}')
        return jsonify(turbine_info), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Endpoint para obtener las alertas históricas de las turbinas 
@app.route('/api/v1/farms/<int:farm_id>/turbines/alerts', methods=['GET'])
def get_turbine_alerts_in_farm(farm_id):
    """
    Endpoint que devuelve las alertas históricas de todas las turbinas
    """
    try:
        turbines = make_request(f'farms/{farm_id}/turbines')
        alerts = []
        for turbine in turbines.get('turbines', []):
            turbine_alerts = make_request(f'turbines/{turbine}/alerts')
            alerts.extend(turbine_alerts)

        # Aquí también se podrían filtrar y organizar las alertas según las reglas que se apliquen
        return jsonify({"alerts": alerts}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
if __name__ == '__main__':
    # Ejecuta en el puerto 5000 por defecto
    app.run(debug=True)

