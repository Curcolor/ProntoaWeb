# ProntoaWeb

Aplicación web Flask para automatización de WhatsApp Business con arquitectura modular y separación clara entre interfaz web y API REST.

## Características

- 🚀 **Flask 3.0** con patrón Factory
- 🗄️ **SQLAlchemy** para base de datos
- 🎨 **Bootstrap 5** para interfaz responsive
- 🔧 **Arquitectura modular** con blueprints
- 📱 **API REST** separada de la interfaz web
- 🛡️ **Manejo de errores** personalizado

## Estructura del Proyecto

```
ProntoaWEB/
├── app/
│   ├── __init__.py              # Factory de la aplicación Flask
│   ├── config.py                # Configuraciones por entorno
│   ├── extensions.py            # Extensiones básicas y BD
│   ├── data/
│   │   ├── models/             # Modelos de SQLAlchemy
│   │   └── schemas/            # Esquemas de validación
│   ├── interfaces/
│   │   ├── static/             # CSS, JS, imágenes
│   │   └── templates/          # Templates Jinja2
│   ├── routes/
│   │   ├── viewpages_routes.py # Rutas de interfaz web
│   │   └── api/                # Endpoints REST API
│   └── services/               # Lógica de negocio
├── docs/                       # Documentación del proyecto
├── instance/                   # Base de datos SQLite
├── run.py                      # Punto de entrada
└── requirements.txt            # Dependencias
```

## Instalación

1. **Clonar repositorio**
```bash
git clone <repository-url>
cd ProntoaWEB
```

2. **Crear entorno virtual**
```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows
source .venv/bin/activate      # Linux/Mac
```

3. **Instalar dependencias**
```bash
pip install Flask Flask-SQLAlchemy Flask-Migrate
```

4. **Configurar variables de entorno** (opcional)
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. **Ejecutar aplicación**
```bash
python run.py
```

## Uso

- **Interfaz Web**: http://127.0.0.1:5000
- **API REST**: http://127.0.0.1:5000/api/health
- **Documentación**: Ver carpeta `docs/`

## API Endpoints

- `GET /api/health` - Estado de la API
- `GET /api/orders` - Listar órdenes
- `POST /api/orders` - Crear orden
- `GET /api/users` - Listar usuarios

## Desarrollo

El proyecto utiliza una arquitectura modular que separa claramente:

- **Interfaz Web** (`app/interfaces/`): Templates y recursos estáticos
- **API REST** (`app/routes/api/`): Endpoints JSON para integraciones
- **Base de Datos** (`app/data/`): Modelos y esquemas
- **Servicios** (`app/services/`): Lógica de negocio

## Licencia

MIT License

Sistema inteligente de automatización de pedidos vía WhatsApp para negocios locales en Barranquilla.

## 🚀 Características

- **Agente IA Inteligente**: Respuestas automáticas 24/7
- **Tablero Kanban**: Gestión visual de pedidos
- **API REST**: Endpoints modulares y escalables
- **Interfaz Responsiva**: Diseño moderno y adaptativo
- **Arquitectura Modular**: Separación clara entre frontend y backend

## 📁 Estructura del Proyecto

```
ProntoaWEB/
├── app/                          # Aplicación principal
│   ├── __init__.py              # Factory function de Flask
│   ├── config.py                # Configuraciones por entorno
│   ├── extensions.py            # Extensiones y configuraciones de Flask
│   ├── interfaces/              # Capa de presentación
│   │   ├── static/             # Archivos estáticos
│   │   │   ├── css/
│   │   │   │   ├── styles.css  # CSS base
│   │   │   │   └── index.css   # CSS específico para landing
│   │   │   ├── js/
│   │   │   │   ├── main.js     # JavaScript base
│   │   │   │   └── index.js    # JS específico para landing
│   │   │   └── imgs/           # Imágenes
│   │   └── templates/          # Templates Jinja2
│   │       ├── layout/
│   │       │   └── base.html   # Template base
│   │       ├── errors/         # Páginas de error
│   │       │   ├── 404.html
│   │       │   ├── 403.html
│   │       │   └── 500.html
│   │       └── index.html      # Landing page
│   ├── routes/                 # Rutas y controladores
│   │   ├── __init__.py
│   │   ├── viewpages_routes.py # Rutas de páginas web
│   │   └── api/                # API REST
│   │       ├── __init__.py
│   │       ├── health_routes.py
│   │       ├── orders_routes.py
│   │       └── users_routes.py
│   ├── services/               # Lógica de negocio
│   │   └── __init__.py
│   └── data/                   # Modelos y esquemas
│       ├── models/
│       │   └── __init__.py
│       └── schemas/
│           └── __init__.py
├── docs/                       # Documentación
├── run.py                      # Punto de entrada
├── requirements.txt            # Dependencias
├── .env.example               # Variables de entorno de ejemplo
└── README.md
```

## 🛠️ Tecnologías

### Backend
- **Flask 3.0+**: Framework web ligero y flexible
- **Python 3.13**: Lenguaje de programación
- **Jinja2**: Motor de templates

### Frontend
- **HTML5 + CSS3**: Estructura y estilos
- **Bootstrap 5**: Framework CSS responsivo
- **JavaScript ES6+**: Interactividad del lado cliente
- **Font Awesome**: Biblioteca de iconos

### Herramientas
- **Virtual Environment**: Entorno aislado de Python
- **Flask CLI**: Herramientas de línea de comandos
- **dotenv**: Gestión de variables de entorno

## ⚡ Instalación Rápida

### 1. Clonar el repositorio
```bash
git clone https://github.com/Curcolor/ProntoaWeb.git
cd ProntoaWeb
```

### 2. Crear entorno virtual
```bash
python -m venv .venv
```

### 3. Activar entorno virtual
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### 6. Ejecutar la aplicación
```bash
python run.py
```

La aplicación estará disponible en: http://127.0.0.1:5000

## 🌐 Endpoints de la API

### Health Check
- `GET /api/health` - Estado de la aplicación
- `GET /api/status` - Estado detallado del sistema

### Órdenes
- `GET /api/orders` - Listar todas las órdenes
- `GET /api/orders/<id>` - Obtener orden específica
- `POST /api/orders` - Crear nueva orden

### Usuarios
- `GET /api/users` - Listar usuarios
- `GET /api/users/<id>` - Obtener usuario específico
- `POST /api/users` - Crear nuevo usuario
- `PUT /api/users/<id>` - Actualizar usuario

## 🎨 Arquitectura

### Patrón MVC Modificado
- **Models** (`app/data/models/`): Definición de datos
- **Views** (`app/interfaces/templates/`): Presentación
- **Controllers** (`app/routes/`): Lógica de control

### Separación de Capas
- **Interfaz Web**: Landing page y aplicación web
- **API REST**: Servicios para aplicaciones externas
- **Servicios**: Lógica de negocio reutilizable
- **Datos**: Modelos y esquemas de validación

### Blueprints
- `viewpages_bp`: Páginas web (landing, dashboard, etc.)
- `api_bp`: API REST con sub-blueprints por recurso

## 🔧 Configuración

### Entornos Disponibles
- **Development**: Para desarrollo local
- **Production**: Para producción
- **Testing**: Para pruebas

### Variables de Entorno
```env
FLASK_CONFIG=development
FLASK_DEBUG=True
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
SECRET_KEY=your-secret-key-here
```

## 📱 Funcionalidades de la Landing Page

### Secciones Implementadas
1. **Hero Section**: Título principal y llamadas a la acción
2. **Problemas**: Desafíos que resuelve Prontoa
3. **Soluciones**: Características del sistema
4. **Demo**: Vista previa del dashboard
5. **Beneficios**: Métricas de mejora
6. **Precios**: Planes flexibles
7. **Footer**: Información de contacto

### Características Técnicas
- **Responsive Design**: Adaptable a todos los dispositivos
- **Smooth Scrolling**: Navegación fluida entre secciones
- **Animaciones CSS**: Efectos visuales al hacer scroll
- **Modales Dinámicos**: Formularios de contacto
- **SEO Optimizado**: Meta tags y estructura semántica

## 🚦 Comandos Útiles

### Desarrollo
```bash
# Ejecutar en modo desarrollo
python run.py

# Ejecutar con configuración específica
FLASK_CONFIG=production python run.py
```

### Testing (Futuro)
```bash
# Ejecutar tests
pytest

# Ejecutar tests con cobertura
pytest --cov=app
```

## 📈 Roadmap

### v1.1 (Próximamente)
- [ ] Sistema de autenticación
- [ ] Dashboard administrativo
- [ ] Integración con WhatsApp Business API

### v1.2 (Planificado)
- [ ] Base de datos PostgreSQL
- [ ] Sistema de notificaciones
- [ ] Analytics avanzado

### v1.3 (Futuro)
- [ ] Integración con sistemas de pago
- [ ] Aplicación móvil
- [ ] Multi-tenant

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 📞 Contacto

- **Email**: soporte@prontoa.com
- **WhatsApp**: +57 300 123 4567
- **Website**: https://prontoa.com

---

**Desarrollado con ❤️ para negocios locales en Barranquilla**
