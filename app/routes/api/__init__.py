"""
Blueprint de API REST.
Centraliza todos los endpoints de la API.
"""
from app.routes.api.auth_routes import auth_api_bp
from app.routes.api.orders_routes import orders_api_bp
from app.routes.api.kpis_routes import kpis_api_bp
from app.routes.api.whatsapp_routes import whatsapp_api_bp

# Lista de todos los blueprints de API
api_blueprints = [
    auth_api_bp,
    orders_api_bp,
    kpis_api_bp,
    whatsapp_api_bp
]

__all__ = [
    'auth_api_bp',
    'orders_api_bp',
    'kpis_api_bp',
    'whatsapp_api_bp',
    'api_blueprints'
]
