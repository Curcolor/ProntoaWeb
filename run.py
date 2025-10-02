import os
from dotenv import load_dotenv
from app import create_app

# Cargar variables de entorno desde archivo .env si existe
load_dotenv()

# Crear la aplicación Flask
app = create_app()
if __name__ == '__main__':
    # Obtener configuración desde variables de entorno
    config_name = os.environ.get('FLASK_CONFIG')
    
    # Ejecutar la aplicación
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )