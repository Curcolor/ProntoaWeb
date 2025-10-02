"""
Extensiones de Flask para la aplicación.
Solo las extensiones necesarias y inicialización de base de datos.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Inicialización de extensiones
db = SQLAlchemy()

def init_extensions(app: Flask) -> None:
    # Inicializar base de datos
    db.init_app(app)
    
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
