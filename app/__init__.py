import os
from flask import Flask, render_template
from app.config import config
from app.extensions import init_extensions, db


def create_app(config_name):
    # Determinar la configuración a utilizar
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    # Crear aplicación Flask
    app = Flask(__name__, 
                template_folder='interfaces/templates',
                static_folder='interfaces/static')
    
    # Cargar configuración
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Configurar SECRET_KEY para sesiones -- recordar mandarlo a .env en producción
    app.secret_key = os.environ.get('SECRET_KEY')

    # Inicializar extensiones
    init_extensions(app)
    
    # Crear tablas de base de datos en el contexto de la app
    with app.app_context():
        # Importar modelos para que SQLAlchemy los registre
        from app.data import models
        
        # Crear todas las tablas si no existen
        db.create_all()
    
    # Importar y registrar blueprints de manera modular
    from app.routes import blueprints
    for blueprint_info in blueprints:
        if isinstance(blueprint_info, tuple):
            # Blueprint con configuración adicional (como url_prefix)
            blueprint, options = blueprint_info
            app.register_blueprint(blueprint, **options)
        else:
            # Blueprint simple
            app.register_blueprint(blueprint_info)
    
    # Registrar manejadores de errores personalizados
    register_error_handlers(app)
    
    # Registrar procesador de contexto para mensajes flash
    @app.context_processor
    def inject_flash_categories():
        """Inyecta categorías de flash messages."""
        return {
            'get_flashed_messages': lambda: app.jinja_env.globals['get_flashed_messages']()
        }
    
    # Mostrar rutas registradas en la consola (útil para debug)
    # Solo mostrar si no es un restart del servidor
    if app.config['DEBUG'] and not os.environ.get('WERKZEUG_RUN_MAIN'):
        print("\n" + "="*60)
        print("🚀 PRONTOA WEB - Rutas Registradas")
        print("="*60)
        
        # Agrupar rutas por blueprint
        routes_by_blueprint = {}
        for rule in app.url_map.iter_rules():
            blueprint = rule.endpoint.split('.')[0] if '.' in rule.endpoint else 'app'
            if blueprint not in routes_by_blueprint:
                routes_by_blueprint[blueprint] = []
            routes_by_blueprint[blueprint].append(f"  {rule.rule:40} {str([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']]):20} -> {rule.endpoint}")
        
        for blueprint, routes in sorted(routes_by_blueprint.items()):
            print(f"\n📦 {blueprint.upper()}")
            print("-" * 60)
            for route in sorted(routes):
                print(route)
        
        print("\n" + "="*60 + "\n")
    
    return app


def register_error_handlers(app):
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403
