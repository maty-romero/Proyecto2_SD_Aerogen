from flask_restx import Resource, Namespace
from StatNode.API.models.schemas import turbine_connection_model
from StatNode.API.utils.emqx_client import emqx_client
from StatNode.Auth.verify_key import require_api_key
from StatNode.API.server import api

turbines_ns = Namespace('turbines', description='Operaciones de turbinas')
api.add_namespace(turbines_ns)

@turbines_ns.route('/<string:farm_id>/<string:turbine_id>')
@turbines_ns.param('farm_id', 'ID del parque')
@turbines_ns.param('turbine_id', 'ID de la turbina dentro del parque')
class TurbineDetail(Resource):
    @turbines_ns.doc('get_turbine_detail', security='apikey')
    @turbines_ns.marshal_with(turbine_connection_model)
    @turbines_ns.response(200, 'Success')
    @turbines_ns.response(401, 'API key required')
    @turbines_ns.response(404, 'Turbine not found')
    @turbines_ns.response(503, 'EMQX broker unavailable')
    @require_api_key()
    def get(self, farm_id, turbine_id):
        """
        Obtener información de conexión de una turbina específica
        
        Consulta el broker EMQX para verificar si la turbina está conectada
        y retorna información sobre su estado de conexión.
        """
        # Consultar broker EMQX
        client_info = emqx_client.get_client_by_farm_and_id(farm_id, turbine_id)
        
        if client_info is None:
            turbines_ns.abort(404, f'Turbina T{turbine_id} del parque {farm_id} no encontrada o no conectada')
        
        # Formatear información
        turbine_data = emqx_client.format_turbine_info(client_info)
        
        return turbine_data, 200