# ProntoaWeb

Sistema web de automatización de pedidos vía WhatsApp para negocios locales en Barranquilla.

## Problemática

Los pequeños y medianos negocios en Barranquilla enfrentan desafíos críticos en la gestión de pedidos:

- **Gestión manual ineficiente**: Pérdida de pedidos por falta de organización
- **Atención limitada**: Solo durante horarios comerciales
- **Errores humanos**: Confusiones en precios, disponibilidad y detalles
- **Crecimiento limitado**: Incapacidad de escalar operaciones
- **Competencia desigual**: Desventaja frente a grandes cadenas digitalizadas

## Solución

ProntoaWeb automatiza la gestión de pedidos de WhatsApp mediante:

- **Agente IA**: Respuestas automáticas 24/7 con procesamiento de lenguaje natural
- **Dashboard Kanban**: Gestión visual del flujo de pedidos
- **Integración WhatsApp**: Conexión directa con WhatsApp Business API
- **Analytics**: Métricas de ventas y rendimiento en tiempo real
- **Automatización**: Confirmación automática de disponibilidad y precios

## Stack Tecnológico

- **Backend**: Flask 3.0 + Python 3.13
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript ES6+
- **Arquitectura**: Patrón Factory con Blueprints modulares
- **Plantillas**: Jinja2 con diseño responsivo

## Estructura del Proyecto

```
ProntoaWeb/
├── app/
│   ├── __init__.py              # Factory de aplicación Flask
│   ├── config.py                # Configuraciones por entorno
│   ├── extensions.py            # Extensiones Flask
│   ├── interfaces/              # Capa de presentación
│   │   ├── static/             # CSS, JS, imágenes
│   │   └── templates/          # Templates Jinja2
│   ├── routes/                 # Rutas y controladores
│   │   ├── viewpages_routes.py # Páginas web
│   │   └── api/                # API REST (futuro)
│   ├── services/               # Lógica de negocio
│   └── data/                   # Modelos y esquemas
├── docs/                       # Documentación y mockups
├── run.py                      # Punto de entrada
└── requirements.txt            # Dependencias
```

## Instalación Rápida

### Requisitos Previos
- Python 3.11+ 
- Git

### Pasos de Instalación

1. **Clonar repositorio**
```bash
git clone https://github.com/Curcolor/ProntoaWeb.git
cd ProntoaWeb
```

2. **Crear y activar entorno virtual**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Ejecutar aplicación**
```bash
python run.py
```

La aplicación estará disponible en: http://127.0.0.1:5000

## Configuración

### Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:

```env
FLASK_CONFIG=development
FLASK_DEBUG=True
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
```

### Entornos Disponibles
- `development`: Desarrollo local con debug activo
- `production`: Producción optimizada

## Docker

```bash
# Construcción y ejecución
docker-compose up -d

# Modo desarrollo
docker-compose -f docker-compose.dev.yml up
```

## Funcionalidades Actuales

### Landing Page ✅
- Hero section con propuesta de valor
- Sección de problemas y soluciones
- Vista previa del dashboard
- Formularios de contacto
- Diseño responsivo

### En Desarrollo 
- Dashboard administrativo
- Sistema de autenticación
- Integración WhatsApp Business API
- Base de datos PostgreSQL
- Panel de analytics

## Arquitectura

### Patrón de Diseño
- **Blueprint Pattern**: Organización de rutas por funcionalidad
- **MVC Modificado**: Separación clara de responsabilidades

### Flujo de Desarrollo
- **Metodología**: Scrum con sprints de 1-4 semanas
- **Versionado**: Git Flow con ramas feature/bugfix/hotfix
- **Commits**: Convención semántica (feat/fix/docs/style/refactor)

## Comandos Útiles

```bash
# Desarrollo
python run.py

# Producción
FLASK_CONFIG=production python run.py
```