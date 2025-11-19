from flask_restx import Resource, Namespace
from StatNode.API.models.schemas import  alert_history_model
from StatNode.API.server import api
from StatNode.API.utils.db_instance import get_db_client
from flask import request

alerts_ns = Namespace('alerts', description='Operaciones de alertas')
api.add_namespace(alerts_ns)

def serialize_alert(doc):
    if '_id' in doc and doc['_id'] is not None:
        doc['id'] = str(doc['_id'])
        doc.pop('_id')
    return doc

@alerts_ns.route('/farm/<int:farm_id>')
@alerts_ns.param('farm_id', 'ID del parque')
class AlertsByFarm(Resource):
    @alerts_ns.marshal_with(alert_history_model)
    @alerts_ns.param('limit', 'Límite de registros', _in='query', type=int, default=1000)
    @alerts_ns.response(200, 'Success')
    @alerts_ns.response(404, 'Data not found')
    @alerts_ns.response(503, 'Database unavailable')
    def get(self, farm_id):
        """Obtener todas las alertas de una granja"""
        limit = int(request.args.get('limit', 1000))
        db = get_db_client()
        results = db.get_alerts_by_farm(farm_id, limit=limit)
        return {
            "farm_id": farm_id,
            "count": len(results),
            'turbine_id': "All",
            "alerts": results
        }, 200


@alerts_ns.route('/farm/<int:farm_id>/turbine/<int:turbine_id>')
@alerts_ns.param('farm_id', 'ID del parque')
@alerts_ns.param('turbine_id', 'ID de la turbina')
class AlertsByFarmTurbine(Resource):
    @alerts_ns.marshal_with(alert_history_model)
    @alerts_ns.param('limit', 'Límite de registros', _in='query', type=int, default=1000)
    @alerts_ns.response(200, 'Success')
    @alerts_ns.response(404, 'Data not found')
    @alerts_ns.response(503, 'Database unavailable')
    def get(self, farm_id, turbine_id):
        """Obtener alertas de una turbina específica en una granja"""
        limit = int(request.args.get('limit', 1000))
        db = get_db_client()
        results = db.get_alerts_by_farm_and_turbine(farm_id, turbine_id, limit=limit)
        return {
            "farm_id": farm_id,
            "count": len(results),
            'turbine_id': str(turbine_id),
            "alerts": results
        }, 200
    

@alerts_ns.route('/farm/<int:farm_id>/severity/<string:severity>')
@alerts_ns.param('farm_id', 'ID del parque')
@alerts_ns.param('severity', 'Nivel de severidad (critical, warning, info)')
class AlertsByFarmSeverity(Resource):
    @alerts_ns.marshal_with(alert_history_model)
    @alerts_ns.param('limit', 'Límite de registros', _in='query', type=int, default=1000)
    @alerts_ns.response(200, 'Success')
    @alerts_ns.response(404, 'Data not found')
    @alerts_ns.response(503, 'Database unavailable')
    def get(self, farm_id, severity):
        """Obtener alertas de una granja por severidad"""
        limit = int(request.args.get('limit', 1000))
        db = get_db_client()
        results = db.get_alerts_by_farm_and_severity(farm_id, severity, limit=limit)
        return {
            "farm_id": farm_id,
            "count": len(results),
            'turbine_id': "All",
            "alerts": results
        }, 200