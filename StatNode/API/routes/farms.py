from flask_restx import Resource, Namespace
from StatNode.API.models.schemas import turbines_list_model_connection, farm_history_model
from StatNode.API.utils.emqx_client import emqx_client
from StatNode.Auth.verify_key import require_api_key
from flask import request
import os

#Namespace
farms_ns = Namespace('farms', description='Operaciones de parques eólicos')

from StatNode.API.server import api
api.add_namespace(farms_ns)


@farms_ns.route('/<string:farm_id>/turbines')
@farms_ns.param('farm_id', 'ID del parque eólico')
class FarmTurbines(Resource):
    @farms_ns.doc('get_farm_turbines', security='apikey')
    @farms_ns.marshal_with(turbines_list_model_connection)
    @farms_ns.response(200, 'Success')
    @farms_ns.response(401, 'API key required')
    @farms_ns.response(404, 'Farm not found')
    @farms_ns.response(503, 'EMQX broker unavailable')
    @require_api_key()
    def get(self, farm_id):
        """
        Obtener todas las turbinas conectadas al broker en un parque
        
        Consulta el broker EMQX para obtener información en tiempo real
        de las turbinas conectadas de un parque específico.
        """
        # Obtener clientes conectados del broker EMQX
        farm_clients = emqx_client.get_clients_by_farm(farm_id)
        
        if farm_clients is None:
            farms_ns.abort(503, 'No se pudo conectar con el broker EMQX')
        
        # Formatear información de turbinas
        turbines = [
            emqx_client.format_turbine_info(client)
            for client in farm_clients
        ]
        
        return {
            'farm_id': farm_id,
            'count': len(turbines),
            'turbines': turbines
        }, 200


@farms_ns.route('/<int:farm_id>/turbines/<int:turbine_id>/history')
@farms_ns.param('farm_id', 'ID del parque eólico')
@farms_ns.param('turbine_id', 'ID de la turbina')
class TurbineHistory(Resource):
    @farms_ns.doc('get_turbine_history', security='apikey')
    @farms_ns.marshal_with(farm_history_model)
    @farms_ns.param('from', 'Fecha inicio (ISO 8601)', _in='query', required=False)
    @farms_ns.param('to', 'Fecha fin (ISO 8601)', _in='query', required=False)
    @farms_ns.param('limit', 'Límite de registros', _in='query', type=int, default=1000)
    @farms_ns.response(200, 'Success')
    @farms_ns.response(401, 'API key required')
    @farms_ns.response(404, 'Turbine not found')
    @farms_ns.response(503, 'Database unavailable')
    @require_api_key()
    def get(self, farm_id, turbine_id):
        """
        Obtener historial de telemetría de una turbina específica
        
        Consulta la base de datos para obtener datos históricos de telemetría
        de una turbina filtrados por rango de fechas.
        """
        from StatNode.API.utils.db_instance import get_db_client
        
        from_date = request.args.get('from', '2025-11-08T00:00:00Z')
        to_date = request.args.get('to', '2025-11-16T23:59:59Z')
        limit = int(request.args.get('limit', 1000))
        
        # Obtener cliente de base de datos
        db_client = get_db_client()
        
        if not db_client:
            farms_ns.abort(503, 'Base de datos no disponible')
        
        try:
            telemetry_data = db_client.get_turbine_telemetry_by_date_range(
                turbine_id=turbine_id,
                from_date=from_date,
                to_date=to_date,
                limit=limit
            )
            
            return {
                'farm_id': farm_id,
                'turbine_id': turbine_id,
                'from': from_date,
                'to': to_date,
                'count': len(telemetry_data),
                'data': telemetry_data
            }, 200
            
        except Exception as e:
            print(f"[API] Error al obtener historial: {e}")
            farms_ns.abort(503, f'Error al consultar la base de datos: {str(e)}')