# ProntoaWEB - Sistema de Gestión de Pedidos con IA

Sistema completo de gestión de pedidos para negocios locales con integración de WhatsApp Business API, Agente IA con GPT-4, y dashboard en tiempo real.

![Status](https://img.shields.io/badge/Status-Production%20Ready-success)
![Python](https://img.shields.io/badge/Python-3.13-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)

---

## Tabla de Contenidos

- [Características](#-características)
- [Stack Tecnológico](#-stack-tecnológico)
- [Instalación Rápida](#-instalación-rápida)
- [Uso](#-uso)
- [Documentación](#-documentación-completa)

---

## Características

### Agente IA con GPT-4
- Procesamiento de lenguaje natural para pedidos por WhatsApp
- Extracción automática de productos, cantidades y direcciones
- Creación automática de pedidos desde conversaciones

### Integración WhatsApp Business
- Recepción de mensajes via webhook
- Envío de confirmaciones automáticas
- Plantillas personalizables

### Dashboard en Tiempo Real
- Kanban board con drag & drop funcional
- Gestión visual de pedidos
- Métricas en vivo
- Auto-refresh cada 30 segundos

### Analytics y KPIs
- Tasa de automatización (98.5%)
- ROI (89%)
- Gráficos interactivos con Chart.js
- Exportación a CSV

### Sistema de Autenticación
- Flask-Login con sesiones seguras
- Bcrypt para passwords
- Protección de rutas

---

## Stack Tecnológico

### Backend
- Flask 3.0 + Python 3.13
- PostgreSQL 15 + SQLAlchemy 2.0
- Flask-Login + Bcrypt
- Marshmallow + WTForms

### AI & Integrations
- OpenAI GPT-4
- WhatsApp Business API / Twilio
- Stripe Payments

### Real-time
- Flask-SocketIO 5.3

### Frontend
- JavaScript ES6+ Vanilla
- Chart.js 4.x
- Bootstrap 5 + CSS3

### DevOps
- Docker + Docker Compose
- PostgreSQL 15-alpine

---

## Instalación Rápida

### Un Solo Comando - Todo Automático ✨

```bash
# Clonar repositorio
git clone https://github.com/Curcolor/ProntoaWeb.git
cd ProntoaWeb

# Iniciar con Docker (TODO automático)
docker-compose up --build
```

**Login:**
- Email: `admin@prontoa.com`
- Password: `admin123`

---

### Instalación Manual (Opcional)

```bash
# Crear virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables
cp .env.example .env
# Editar .env con tus API keys

# Iniciar servicios
docker-compose up -d db

# Poblar base de datos
python app/scripts/seed_database.py

# Seed database (primera vez)
python app/scripts/seed_database.py

# Iniciar Flask
python run.py
```

### Acceder

```
http://localhost:5000

Credenciales de prueba:
Email: admin@prontoa.com
Password: admin123
```

---

##  Uso

### Dashboard
- Ver pedidos en Kanban board
- Drag & drop para cambiar estados
- Click para ver detalles completos
- Métricas en tiempo real

### KPIs
- Analytics operacionales
- Impacto financiero
- Gráficos de tendencias
- Exportar reportes CSV

### Perfil
- Ver información de usuario
- Métricas personales
- Editar configuraciones

### Configuraciones
- Horarios del negocio
- Configurar delivery
- Plantillas de WhatsApp
- Cambiar contraseña

---

## Documentación
- [**API_EXAMPLES.md**](API_EXAMPLES.md) - Ejemplos de uso de todas las APIs

---

## Roadmap

###  Completado (80%)
- [x] Backend con Flask y PostgreSQL
- [x] Autenticación completa
- [x] API REST (25+ endpoints)
- [x] Integración WhatsApp Business
- [x] Agente IA con GPT-4
- [x] Dashboard con Kanban funcional
- [x] KPIs y Analytics
- [x] Frontend conectado a APIs
- [x] Docker Compose setup
- [x] Documentación completa

###  Pendiente (20%)
- [ ] Notificaciones real-time (SocketIO)
- [ ] Generación de reportes PDF/Excel
- [ ] Integración completa Stripe