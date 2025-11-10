"""
Centralización de blueprints del sistema ProntoaWEB.
Importa y organiza todos los blueprints disponibles.
"""

from .viewpages_routes import viewpages_bp
from .api import api_blueprints

# Lista de todos los blueprints disponibles
blueprints = [
    viewpages_bp,
    *api_blueprints  # Expandir todos los blueprints de API
]

__all__ = ['blueprints']

