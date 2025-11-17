from flask import jsonify
from StatNode.API.server import app


@app.route('/')
def index():
    """Root endpoint - Información general de la API"""
    return jsonify({
        'service': 'WindFarm StatNode API',
        'version': '5.0',
        'status': 'running',
        'documentation': '/api-docs',
        'endpoints': {
            'swagger': 'GET /api-docs',
            'health': 'GET /health',
            'farms_turbines': 'GET /api/v5/farms/{farm_id}/turbines',
            'turbine_history': 'GET /api/v5/farms/{farm_id}/turbines/{turbine_id}/history',
            'turbine_detail': 'GET /api/v5/turbines/{farm_id}/{turbine_id}',
            # 'alerts': 'GET /api/v5/alerts',
            # 'turbine_alerts': 'GET /api/v5/alerts/turbine/{turbine_id}'
        }
    })


@app.route('/health')
def health():
    """Health check endpoint para failover"""
    return jsonify({"status": "ok"}), 200


try:
    from StatNode.Auth.verify_key import require_api_key
    
    @app.route("/protected")
    @require_api_key()
    def protected():
        """
        Endpoint protegido con API Key
        
        Requiere header: x-api-key: <kid>.<raw_key>
        """
        return jsonify({
            "message": "Acceso concedido",
        }), 200
except ImportError:
    print("[WARNING] require_api_key no disponible")