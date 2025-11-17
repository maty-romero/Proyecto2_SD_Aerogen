from flask_restx import Resource, Namespace
from StatNode.API.models.schemas import alert_model
from StatNode.API.server import api

alerts_ns = Namespace('alerts', description='Operaciones de alertas')
api.add_namespace(alerts_ns)


@alerts_ns.route('/')
class AlertsList(Resource):
    @alerts_ns.doc('get_all_alerts')
    @alerts_ns.marshal_list_with(alert_model)
    def get(self):
        """Obtener todas las alertas del sistema"""
        return [
            {
                'id': 1,
                'message': 'High wind speed detected',
                'turbine': 'T-001',
                'severity': 'warning',
                'timestamp': '2025-11-16T10:00:00Z'
            }
        ], 200


@alerts_ns.route('/turbine/<string:turbine_id>')
@alerts_ns.param('turbine_id', 'ID de la turbina')
class TurbineAlerts(Resource):
    @alerts_ns.doc('get_turbine_alerts')
    @alerts_ns.marshal_list_with(alert_model)
    def get(self, turbine_id):
        """Obtener alertas de una turbina específica"""
        return [], 200