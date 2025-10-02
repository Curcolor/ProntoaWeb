"""
Rutas de API para el manejo de la salud de la aplicación.
Endpoints de monitoreo y estado de la aplicación.
"""

from flask import Blueprint, jsonify
from datetime import datetime

# Crear blueprint para rutas de salud
health_bp = Blueprint('health', __name__)


@health_bp.route('/health')
def health_check():
    """
    Endpoint de health check para verificar el estado de la aplicación.
    
    Returns:
        JSON: Estado de la aplicación y timestamp
    """
    return jsonify({
        'status': 'healthy',
        'message': 'API funcionando correctamente',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'ProntoaWeb API',
        'version': '1.0.0'
    })


@health_bp.route('/status')
def status():
    """
    Endpoint detallado de estado de la aplicación.
    
    Returns:
        JSON: Información detallada del estado del sistema
    """
    return jsonify({
        'application': {
            'name': 'ProntoaWeb',
            'status': 'running',
            'uptime': 'calculado dinámicamente en producción'
        },
        'api': {
            'version': 'v1',
            'endpoints_available': [
                '/api/health',
            ]
        },
        'timestamp': datetime.utcnow().isoformat()
    })
