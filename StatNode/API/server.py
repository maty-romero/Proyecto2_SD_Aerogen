from flask import Flask, request, jsonify, g
from StatNode.Auth.verify_key import *


app = Flask(__name__)

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

@app.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint simple para verificar que el servicio está vivo.
    """
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    # Ejecuta en el puerto 5000 por defecto
    app.run()

