# ProntoaWEB - Sistema de Gestión de Pedidos con IA

Sistema completo de gestión de pedidos para negocios locales con integración de WhatsApp Business API, Agente IA con Perplexity (Llama 3.1), y dashboard en tiempo real.

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

### Agente IA con Perplexity
- Procesamiento de lenguaje natural optimizado (respuestas cortas)
- Extracción automática de productos, cantidades y direcciones
- Creación automática de pedidos desde conversaciones
- Restricción estricta al contexto del negocio

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
- Perplexity AI (Llama 3.1 Sonar) - Respuestas cortas y enfocadas
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

### Usando las imágenes publicadas en GHCR (recomendado)

```bash
# Autenticarse en GitHub Container Registry (token con read:packages)
docker login ghcr.io -u curcolor --password-stdin <token>

# Descargar el stack completo
docker pull ghcr.io/curcolor/prontoaweb-web:latest
docker pull ghcr.io/curcolor/prontoaweb-bot:latest
docker pull ghcr.io/curcolor/prontoaweb-db:15-alpine

# Levantar todo con Docker Compose
docker compose up -d
```

> El archivo `docker-compose.yml` ya referencia estas imágenes, así que no necesitas construir nada en la máquina destino.

### Construcción local (opcional)

```bash
# Clonar repositorio
git clone https://github.com/Curcolor/ProntoaWeb.git
cd ProntoaWeb

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales (Perplexity, WhatsApp, Telegram, DB, etc.)

# Iniciar con Docker (compila imágenes locales)
docker compose up --build
```

**Login por defecto:** `admin@prontoa.com / admin123`

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
# Editar .env con tus credenciales:
# - PERPLEXITY_API_KEY (obtener en https://www.perplexity.ai/settings/api)
# - WHATSAPP_PHONE_ID, WHATSAPP_TOKEN, WHATSAPP_VERIFY_TOKEN
# - Opcional: PERPLEXITY_MODEL (default: llama-3.1-sonar-small-128k-online)

# Iniciar servicios auxiliares
docker compose up -d db

# Poblar base de datos (seeds)
python app/scripts/seed_database.py

# Ejecutar el bot de Telegram (polling)
python -m app.scripts.telegram_bot

# Iniciar Flask en modo dev
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

### Bot de Telegram
- Conversación 100% asistida por IA (Perplexity Sonar)
- Confirmación de pedidos y generación automática en el backend
- Notificaciones proactivas cuando el personal cambia el estado (`preparing`, `ready`, `sent`, `paid`)

### Notificaciones en tiempo real
- El servicio `TelegramService` envía mensajes predefinidos vía Bot API
- Se integra con `OrderService.update_order_status` y con los endpoints de trabajadores
- Konecta con `docker compose` o despliegues externos sin reconfigurar el bot

---

## 📦 Imágenes publicadas (GHCR)

| Servicio        | Imagen                                        | Descripción |
|-----------------|-----------------------------------------------|-------------|
| Web / API       | `ghcr.io/curcolor/prontoaweb-web:latest`      | Flask + IA + dashboard |
| Telegram Bot    | `ghcr.io/curcolor/prontoaweb-bot:latest`      | Misma build con comando `python -m app.scripts.telegram_bot` |
| Base de datos   | `ghcr.io/curcolor/prontoaweb-db:15-alpine`    | Imagen oficial de Postgres re-etiquetada |

**Comandos útiles**

```bash
# Reiniciar solo el contenedor web
docker compose restart web

# Detener, reconstruir y levantar todo
docker compose down
docker compose build
docker compose up -d

# Conectarse a PostgreSQL
docker compose exec db psql -U prontoa_user -d prontoa_db
\dt
```

---

## 📖 Documentación Completa

- [**🐳 Docker Setup**](docs/DOCKER_SETUP.md) - Guía completa de Docker con Perplexity AI
- [**🤖 Perplexity Setup**](docs/PERPLEXITY_SETUP.md) - Configuración de Perplexity AI
- [**📡 API Examples**](docs/Documentation/API_EXAMPLES.md) - Ejemplos de uso de todas las APIs

---

## Roadmap

###  Completado (80%)
- [x] Backend con Flask y PostgreSQL
- [x] Autenticación completa
- [x] API REST (25+ endpoints)
- [x] Integración WhatsApp Business
- [x] Agente IA con Perplexity (optimizado)
- [x] Dashboard con Kanban funcional
- [x] KPIs y Analytics
- [x] Frontend conectado a APIs
- [x] Docker Compose setup
- [x] Documentación completa

###  Pendiente (20%)
- [ ] Notificaciones real-time (SocketIO)
- [ ] Generación de reportes PDF/Excel
- [ ] Integración completa Stripe