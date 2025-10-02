import os
from flask import Flask, render_template
from app.config import config
from app.extensions import init_extensions


def create_app(config_name=None):
    # Determinar la configuración a utilizar
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    # Crear aplicación Flask
    app = Flask(__name__, 
                template_folder='interfaces/templates',
                static_folder='interfaces/static')
    
    # Cargar configuración
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Inicializar extensiones
    init_extensions(app)
    
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
    
    # Mostrar rutas registradas en la consola (útil para debug)
    # Solo mostrar si no es un restart del servidor
    if app.config['DEBUG'] and not os.environ.get('WERKZEUG_RUN_MAIN'):
        print("Rutas registradas:")
        for rule in app.url_map.iter_rules():
            print(f"  {rule.endpoint}: {rule.rule}")
    
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