import os
from dotenv import load_dotenv
from app import create_app

# Cargar variables de entorno desde archivo .env si existe
load_dotenv()

# Crear la aplicación Flask
app = create_app(os.environ.get('FLASK_CONFIG'))
if __name__ == '__main__':
    # Ejecutar la aplicación
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )