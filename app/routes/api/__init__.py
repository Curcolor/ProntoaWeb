"""
Blueprint principal para la API REST.
Centraliza todos los sub-blueprints de la API.
"""

from flask import Blueprint

# Crear blueprint principal para la API
api_bp = Blueprint('api', __name__)

# Importar y registrar sub-blueprints automáticamente
from .health_routes import health_bp

# Lista de sub-blueprints de la API
api_blueprints = [
    health_bp,
    # Aquí se agregarán más sub-blueprints en el futuro
    # orders_bp,
    # users_bp,
    # etc.
]

# Registrar todos los sub-blueprints
for blueprint in api_blueprints:
    api_bp.register_blueprint(blueprint)