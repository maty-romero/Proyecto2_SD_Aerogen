from flask import Flask
from flask_restx import Api
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'x-api-key',
        'description': 'API Key en formato: kid.raw_key'
    }
}

api = Api(
    app,
    version='5.0',
    title='WindFarm StatNode API',
    description='API REST para consultar datos del parque eólico',
    doc='/api-docs',
    prefix='/api/v5',
    authorizations=authorizations,
    security='apikey',
    mask=False,
    mask_swagger=False
)

# from StatNode.API.routes import farms, turbines, alerts, general
from StatNode.API.routes import farms, turbines, general

# Inicializar clientes de base de datos
from StatNode.API.utils.db_instance import init_db_clients
init_db_clients()

# Las rutas se registran automáticamente al importarse gracias a los decoradores @farms_ns.route()