import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env
load_dotenv()

class Config:
    """Configuración base para la aplicación Flask."""
    
    # Directorio base del proyecto
    BASE_DIR = Path(__file__).parent.parent.absolute()
    
    # Configuración básica de Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuración de debug
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    
    # Configuración de host y puerto
    HOST = os.environ.get('FLASK_HOST', '127.0.0.1')
    PORT = int(os.environ.get('FLASK_PORT', 5000))
    
    # Configuración de base de datos
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{BASE_DIR}/instance/app.db'
    
    @staticmethod
    def init_app(app):
        """Inicialización adicional de la aplicación"""
        pass

class DevelopmentConfig(Config):
    """Configuración para entorno de desarrollo."""
    DEBUG = True

class ProductionConfig(Config):
    """Configuración para entorno de producción."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{Config.BASE_DIR}/instance/app.db'

class TestingConfig(Config):
    """Configuración para entorno de pruebas."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuraciones disponibles
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
