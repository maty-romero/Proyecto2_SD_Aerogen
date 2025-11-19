from flask_restx import fields
from StatNode.API.server import api

turbine_model = api.model('Turbine', {
    'turbine_id': fields.String(required=True, description='ID de la turbina'),
    'turbine_name': fields.String(required=True, description='Nombre de la turbina'),
    'status': fields.String(required=True, description='Estado operacional'),
    'active_power_kw': fields.Float(description='Potencia activa en kW'),
    'wind_speed_mps': fields.Float(description='Velocidad del viento en m/s'),
    'timestamp': fields.String(description='Última actualización')
})

turbines_list_model = api.model('TurbinesList', {
    'farm_id': fields.String(required=True, description='ID del parque'),
    'count': fields.Integer(required=True,  description='Número de turbinas'),
    'turbines': fields.List(fields.Nested(turbine_model))
})

turbine_connection_model = api.model('TurbineConnection', {
    'turbine_id': fields.String(description='ID del cliente MQTT'),
    'connected': fields.Boolean(description='Estado de conexión'),
    'ip_address': fields.String(description='IP reportada'),
    'connected_at': fields.String(description='Timestamp de conexión'),
})

turbines_list_model_connection = api.model('TurbinesListConnection', {
    'farm_id': fields.String(required=True, description='ID del parque'),
    'count': fields.Integer(required=True,  description='Número de turbinas'),
    'turbines': fields.List(fields.Nested(turbine_connection_model),description='Lista de turbinas conectadas al broker'
    )
})

farm_history_model = api.model('FarmHistory', {
    'farm_id': fields.Integer(description='ID del parque'),
    'from': fields.String(description='Fecha inicio'),
    'to': fields.String(description='Fecha fin'),
    'count': fields.Integer(description='Número de registros'),
    'data': fields.List(fields.Raw, description='Datos históricos')
})

alert_model = api.model('Alert', {
    'id': fields.String(attribute='_id', description='ID de la alerta'),
    'message': fields.String(required=True, description='Mensaje'),
    'turbine_id': fields.Integer(description='ID de la turbina'),
    'turbine_name': fields.String(description='Nombre de la turbina'),
    'severity': fields.String(description='Severidad', enum=['critical', 'warning', 'info']),
    'timestamp': fields.String(description='Timestamp'),
    'farm_id': fields.Integer(description='ID del parque'),
    'farm_name': fields.String(description='Nombre del parque'),
    'alert_type': fields.String(description='Tipo de alerta'),
    'bearing_temperature_c': fields.Float(description='Temperatura de rodamiento'),
    'timestamp_str': fields.String(description='Timestamp legible')
})

alert_history_model = api.model('FarmHistory', {
    'farm_id': fields.Integer(description='ID del parque'),
    'count': fields.Integer(description='Número de registros'),
    'turbine_id': fields.String(description='ID de la turbina'),
    'alerts': fields.List(fields.Nested(alert_model), description='Datos históricos')
})