"""
Centralización de blueprints del sistema ProntoaWEB.
Importa y organiza todos los blueprints disponibles.
"""

from .viewpages_routes import viewpages_bp

# Lista de todos los blueprints disponibles
blueprints = [
    viewpages_bp  # API con prefijo
]

__all__ = ['blueprints']

