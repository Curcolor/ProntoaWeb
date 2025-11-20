import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

# Cargar variables de entorno del archivo .env
load_dotenv()

class Config:
    """Configuración base para la aplicación Flask."""
    
    # Directorio base del proyecto
    BASE_DIR = Path(__file__).parent.parent.absolute()
    
    # Secret key para sesiones y CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuración de base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://prontoa_user:prontoa_pass@localhost:5432/prontoa_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'echo': False,
        'echo_pool': False
    }
    
    # Configuración de debug
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Configuración de host y puerto
    HOST = os.environ.get('FLASK_HOST', '127.0.0.1')
    PORT = int(os.environ.get('FLASK_PORT', 5000))
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # Token no expira
    WTF_CSRF_SSL_STRICT = False  # Permitir en desarrollo sin HTTPS
    
    # CORS configuration
    _cors_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:5000,http://127.0.0.1:5000')
    CORS_ORIGINS = [origin.strip() for origin in _cors_origins.split(',') if origin.strip()]
        
    # WhatsApp Business API
    WHATSAPP_API_KEY = os.environ.get('WHATSAPP_API_KEY')
    WHATSAPP_PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
    WHATSAPP_VERIFY_TOKEN = os.environ.get('WHATSAPP_VERIFY_TOKEN', 'prontoa-verify-token')
    
    # Perplexity AI for AI Agent (compatible con OpenAI API)
    PERPLEXITY_API_KEY = os.environ.get('PERPLEXITY_API_KEY')
    PERPLEXITY_MODEL = os.environ.get('PERPLEXITY_MODEL', 'sonar')

    # Telegram Bot API (integración provisional)
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    TELEGRAM_WEBHOOK_SECRET = os.environ.get('TELEGRAM_WEBHOOK_SECRET', 'prontoa-telegram-webhook')
    
    # Pagination
    ITEMS_PER_PAGE = 25
    
    # Upload folder
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size
    
    @staticmethod
    def init_app(app):
        """Inicialización adicional de la aplicación"""
        # Crear carpeta de uploads si no existe
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class DevelopmentConfig(Config):
    """Configuración para entorno de desarrollo."""
    DEBUG = True
    SQLALCHEMY_ECHO = False  # No mostrar consultas SQL en desarrollo

class ProductionConfig(Config):
    """Configuración para entorno de producción."""
    DEBUG = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log de errores en producción
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug:
            file_handler = RotatingFileHandler(
                'logs/prontoa.log', 
                maxBytes=10240000, 
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('ProntoaWeb startup')

class TestingConfig(Config):
    """Configuración para pruebas."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuraciones disponibles
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

