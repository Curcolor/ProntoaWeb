"""
Extensiones de Flask para la aplicación.
Solo las extensiones necesarias y futura inicialización de base de datos.
"""

from flask import Flask
from flask_wtf.csrf import CSRFProtect

# Inicializar CSRF Protection
csrf = CSRFProtect()


def init_extensions(app: Flask) -> None:
    """Inicializa todas las extensiones de Flask."""
    # Inicializar CSRF Protection
    csrf.init_app(app)
    
    # Configurar variables básicas para templates
    init_template_context(app)


def init_template_context(app: Flask) -> None:
    """Configura variables básicas para templates."""
    
    @app.context_processor
    def inject_global_vars():
        """Variables globales básicas para todos los templates."""
        from datetime import datetime
        return {
            'app_name': 'ProntoaWeb',
            'current_year': datetime.now().year
        }
