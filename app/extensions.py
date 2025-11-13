"""
Extensiones de Flask para la aplicación.
Centraliza la inicialización de todas las extensiones.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_marshmallow import Marshmallow

# Inicializar extensiones
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
cors = CORS()
socketio = SocketIO()
ma = Marshmallow()


def init_extensions(app: Flask) -> None:
    """Inicializa todas las extensiones Flask."""
    
    # Database
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Authentication
    login_manager.init_app(app)
    login_manager.login_view = 'viewpages.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    # Password hashing
    bcrypt.init_app(app)
    
    # CORS
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # SocketIO for real-time notifications
    socketio.init_app(
        app, 
        cors_allowed_origins="*",
        message_queue=app.config.get('SOCKETIO_MESSAGE_QUEUE'),
        async_mode='eventlet'
    )
    
    # Marshmallow for serialization
    ma.init_app(app)
    
    # Configurar user loader para Flask-Login
    from app.data.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Configurar variables básicas para templates
    init_template_context(app)


def init_template_context(app: Flask) -> None:
    """Configura variables básicas para templates."""
    
    @app.context_processor
    def inject_global_vars():
        """Variables globales básicas para todos los templates."""
        from datetime import datetime, timezone
        from flask_login import current_user
        
        return {
            'app_name': 'ProntoaWeb',
            'current_year': datetime.now().year,
            'current_user': current_user
        }

