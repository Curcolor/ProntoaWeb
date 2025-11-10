# 🐳 Configuración Docker - ProntoaWeb

## Índice
- [Requisitos](#requisitos)
- [Instalación Rápida](#instalación-rápida)
- [Configuración Detallada](#configuración-detallada)
- [Variables de Entorno](#variables-de-entorno)
- [Comandos Útiles](#comandos-útiles)
- [Troubleshooting](#troubleshooting)

---

## Requisitos

- **Docker**: versión 20.10 o superior
- **Docker Compose**: versión 2.0 o superior
- **Git**: para clonar el repositorio
- **Cuenta Perplexity AI**: para obtener API key (https://www.perplexity.ai/settings/api)
- **WhatsApp Business API**: credenciales de Meta Developer

### Verificar Instalación
```bash
docker --version          # Docker version 20.10+
docker-compose --version  # Docker Compose version 2.0+
```

---

## Instalación Rápida

### 1. Clonar Repositorio
```bash
git clone https://github.com/Curcolor/ProntoaWeb.git
cd ProntoaWeb
```

### 2. Configurar Variables de Entorno
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar con tu editor preferido
nano .env
# o
code .env
```

**Configuración mínima requerida:**
```bash
# Flask
SECRET_KEY=tu-clave-secreta-segura-aqui

# Database (ya configurada por Docker Compose)
DATABASE_URL=postgresql://prontoa_user:prontoa_pass@db:5432/prontoa_db

# WhatsApp API (obtener en Meta Developer Console)
WHATSAPP_PHONE_ID=tu_phone_id
WHATSAPP_TOKEN=tu_token
WHATSAPP_VERIFY_TOKEN=tu_verify_token

# Perplexity AI (REQUERIDO - obtener en https://www.perplexity.ai/settings/api)
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
PERPLEXITY_MODEL=llama-3.1-sonar-small-128k-online
```

### 3. Iniciar Servicios
```bash
docker-compose up --build
```

✅ La aplicación estará disponible en: **http://localhost:5000**

**Login de prueba:**
- Email: `admin@prontoa.com`
- Password: `admin123`

---

## Configuración Detallada

### Arquitectura Docker

El proyecto usa **Docker Compose** con 2 servicios:

```
┌─────────────────────────────────────────┐
│          Docker Compose                 │
├─────────────────────────────────────────┤
│                                         │
│  ┌───────────────┐  ┌────────────────┐ │
│  │   web         │  │      db        │ │
│  │ Flask App     │──│   PostgreSQL   │ │
│  │ Port: 5000    │  │   Port: 5432   │ │
│  └───────────────┘  └────────────────┘ │
│         │                    │          │
│    Code Volume         Data Volume     │
└─────────────────────────────────────────┘
```

### Servicio: `db` (PostgreSQL)

**Imagen**: `postgres:15-alpine`

**Configuración:**
- Base de datos: `prontoa_db`
- Usuario: `prontoa_user`
- Password: `prontoa_pass`
- Puerto expuesto: `5432`
- Volumen persistente: `postgres_data`

**Health Check:**
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U prontoa_user -d prontoa_db"]
  interval: 5s
  timeout: 5s
  retries: 5
```

### Servicio: `web` (Flask App)

**Build**: Dockerfile personalizado (Python 3.11-slim)

**Puertos:**
- `5000:5000` - HTTP Flask server

**Variables de Entorno Automáticas:**
```yaml
environment:
  - FLASK_CONFIG=development
  - FLASK_DEBUG=True
  - FLASK_HOST=0.0.0.0
  - FLASK_PORT=5000
  - DATABASE_URL=postgresql://prontoa_user:prontoa_pass@db:5432/prontoa_db
  - SECRET_KEY=dev-secret-key-change-in-production
```

**Variables desde .env:**
```yaml
  # WhatsApp API
  - WHATSAPP_PHONE_ID=${WHATSAPP_PHONE_ID}
  - WHATSAPP_TOKEN=${WHATSAPP_TOKEN}
  - WHATSAPP_VERIFY_TOKEN=${WHATSAPP_VERIFY_TOKEN}
  
  # Perplexity AI
  - PERPLEXITY_API_KEY=${PERPLEXITY_API_KEY}
  - PERPLEXITY_MODEL=${PERPLEXITY_MODEL:-llama-3.1-sonar-small-128k-online}
```

**Volúmenes:**
```yaml
volumes:
  - .:/app                    # Hot reload en desarrollo
  - /app/__pycache__         # Evitar conflictos de caché
```

**Dependencias:**
```yaml
depends_on:
  db:
    condition: service_healthy  # Espera a que PostgreSQL esté listo
```

---

## Variables de Entorno

### Flask Configuration

| Variable | Descripción | Ejemplo | Requerido |
|----------|-------------|---------|-----------|
| `FLASK_CONFIG` | Entorno de ejecución | `development`, `production` | ✅ |
| `FLASK_DEBUG` | Modo debug | `True`, `False` | ✅ |
| `FLASK_HOST` | Host del servidor | `0.0.0.0` | ✅ |
| `FLASK_PORT` | Puerto del servidor | `5000` | ✅ |
| `SECRET_KEY` | Clave para sesiones | Cadena aleatoria larga | ✅ |

### Database

| Variable | Descripción | Ejemplo | Requerido |
|----------|-------------|---------|-----------|
| `DATABASE_URL` | URL de PostgreSQL | `postgresql://user:pass@host:5432/db` | ✅ |

**Nota**: En Docker Compose, usar `db` como hostname (nombre del servicio).

### WhatsApp API

| Variable | Descripción | Obtener en | Requerido |
|----------|-------------|------------|-----------|
| `WHATSAPP_PHONE_ID` | ID del número de WhatsApp | Meta Developer Console | ✅ |
| `WHATSAPP_TOKEN` | Token de acceso | Meta Developer Console | ✅ |
| `WHATSAPP_VERIFY_TOKEN` | Token de verificación | Crear manualmente | ✅ |

**Configurar webhook en Meta:**
1. Ir a: https://developers.facebook.com/apps
2. Seleccionar tu app → WhatsApp → Configuration
3. Callback URL: `https://tu-dominio.com/api/whatsapp/webhook`
4. Verify Token: mismo valor de `WHATSAPP_VERIFY_TOKEN`

### Perplexity AI

| Variable | Descripción | Default | Requerido |
|----------|-------------|---------|-----------|
| `PERPLEXITY_API_KEY` | API key de Perplexity | - | ✅ |
| `PERPLEXITY_MODEL` | Modelo a usar | `llama-3.1-sonar-small-128k-online` | ⚠️ Opcional |

**Obtener API Key:**
1. Crear cuenta en: https://www.perplexity.ai
2. Ir a Settings → API
3. Generar nueva API key
4. Copiar key que empieza con `pplx-`

**Modelos disponibles:**

| Modelo | Velocidad | Costo | Búsqueda Web | Uso Recomendado |
|--------|-----------|-------|--------------|-----------------|
| `llama-3.1-sonar-small-128k-online` | ⚡⚡⚡ Rápido | 💰 Bajo | ✅ | **Producción** (pedidos) |
| `llama-3.1-sonar-large-128k-online` | ⚡⚡ Medio | 💰💰 Medio | ✅ | Análisis complejos |
| `llama-3.1-sonar-huge-128k-online` | ⚡ Lento | 💰💰💰 Alto | ✅ | Tareas críticas |

**Costos aproximados** (Enero 2024):
- Small: ~$1 USD por 1M tokens (~10,000 pedidos)
- Large: ~$2 USD por 1M tokens
- Huge: ~$3 USD por 1M tokens

**Comparación con OpenAI:**
- Perplexity Small: **67% más barato** que GPT-4
- Perplexity Large: ~40% más barato que GPT-4
- Ventaja adicional: búsqueda web integrada

---

## Comandos Útiles

### Iniciar Servicios

```bash
# Primera vez (build + start)
docker-compose up --build

# Modo detached (background)
docker-compose up -d

# Solo base de datos
docker-compose up -d db

# Ver logs en tiempo real
docker-compose logs -f web
```

### Detener Servicios

```bash
# Detener sin eliminar
docker-compose stop

# Detener y eliminar contenedores
docker-compose down

# Eliminar todo (contenedores + volúmenes + imágenes)
docker-compose down -v --rmi all
```

### Debugging

```bash
# Ver logs de un servicio
docker-compose logs web
docker-compose logs db

# Logs en tiempo real
docker-compose logs -f web

# Acceder a shell del contenedor
docker-compose exec web bash
docker-compose exec db psql -U prontoa_user -d prontoa_db

# Verificar estado de servicios
docker-compose ps

# Ver uso de recursos
docker stats
```

### Base de Datos

```bash
# Conectar a PostgreSQL
docker-compose exec db psql -U prontoa_user -d prontoa_db

# Backup de base de datos
docker-compose exec db pg_dump -U prontoa_user prontoa_db > backup.sql

# Restaurar backup
docker-compose exec -T db psql -U prontoa_user -d prontoa_db < backup.sql

# Reiniciar solo la base de datos
docker-compose restart db
```

### Desarrollo

```bash
# Rebuild después de cambiar Dockerfile
docker-compose up --build

# Reinstalar dependencias Python
docker-compose exec web pip install -r requirements.txt

# Ejecutar seed de datos
docker-compose exec web python app/scripts/seed_database.py

# Ejecutar Flask shell
docker-compose exec web flask shell
```

---

## Troubleshooting

### ❌ Error: "Port 5000 is already allocated"

**Problema**: Otro servicio está usando el puerto 5000.

**Solución 1**: Cambiar puerto en `docker-compose.yml`:
```yaml
web:
  ports:
    - "8000:5000"  # Usar puerto 8000 externamente
```

**Solución 2**: Detener servicio conflictivo:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

---

### ❌ Error: "Database connection failed"

**Problema**: PostgreSQL no está listo.

**Solución 1**: Esperar unos segundos (health check activándose).

**Solución 2**: Verificar logs:
```bash
docker-compose logs db
```

**Solución 3**: Reiniciar servicio:
```bash
docker-compose restart db
```

---

### ❌ Error: "PERPLEXITY_API_KEY not found"

**Problema**: Variable de entorno no configurada.

**Solución**:
1. Verificar que `.env` existe: `ls -la .env`
2. Verificar contenido: `cat .env | grep PERPLEXITY`
3. Reiniciar contenedores: `docker-compose restart web`

---

### ❌ Error: "Permission denied" en volúmenes

**Problema**: Conflicto de permisos entre host y contenedor.

**Solución Linux/Mac**:
```bash
# Dar permisos al directorio
sudo chown -R $USER:$USER .

# O ejecutar Docker con tu usuario
docker-compose up
```

**Solución Windows**: Verificar que Docker Desktop tiene acceso a la carpeta.

---

### ❌ Error: "Image not found" al hacer build

**Problema**: Dockerfile o contexto de build incorrecto.

**Solución**:
```bash
# Limpiar caché y rebuild
docker-compose build --no-cache web
docker-compose up web
```

---

### ❌ WhatsApp webhook retorna 401/403

**Problema**: Credenciales incorrectas o expiradas.

**Verificar**:
1. `WHATSAPP_TOKEN` es válido en Meta Developer Console
2. `WHATSAPP_VERIFY_TOKEN` coincide en ambos lados
3. Token no ha expirado (renovar si es temporal)

**Solución**:
```bash
# Actualizar .env con nuevas credenciales
nano .env

# Reiniciar servicio web
docker-compose restart web
```

---

### ❌ Perplexity API retorna 401 Unauthorized

**Problema**: API key incorrecta o expirada.

**Verificar**:
1. Ir a: https://www.perplexity.ai/settings/api
2. Verificar que la key está activa
3. Verificar límite de uso no excedido

**Solución**:
```bash
# Regenerar key si es necesario
# Actualizar en .env
PERPLEXITY_API_KEY=pplx-nueva-key-aqui

# Reiniciar
docker-compose restart web
```

---

### ❌ Contenedor web reinicia constantemente

**Problema**: Error en código Python o dependencias faltantes.

**Debugging**:
```bash
# Ver logs completos
docker-compose logs web

# Entrar al contenedor
docker-compose exec web bash

# Verificar instalación
pip list

# Ejecutar Flask manualmente
python run.py
```

---

### 🧹 Reset Completo

Si todo falla, reset total:

```bash
# 1. Detener y eliminar todo
docker-compose down -v

# 2. Limpiar imágenes
docker system prune -a --volumes

# 3. Rebuild desde cero
docker-compose up --build
```

---

## Producción

### Cambios Recomendados para Producción

**1. Variables de Entorno**

```bash
# .env (producción)
FLASK_CONFIG=production
FLASK_DEBUG=False
SECRET_KEY=<clave-larga-aleatoria-segura>

# Usar PostgreSQL externo (no Docker)
DATABASE_URL=postgresql://user:pass@prod-db-host:5432/db

# Perplexity con modelo más preciso (opcional)
PERPLEXITY_MODEL=llama-3.1-sonar-large-128k-online
```

**2. docker-compose.yml**

```yaml
web:
  restart: always  # Auto-restart en producción
  environment:
    - FLASK_CONFIG=production
    - FLASK_DEBUG=False
  # Eliminar volumen de código (no hot reload)
  # volumes:
  #   - .:/app
```

**3. Seguridad**

```bash
# Generar SECRET_KEY segura
python -c "import secrets; print(secrets.token_hex(32))"

# Usar secretos de Docker (Docker Swarm)
echo "tu-secret-key" | docker secret create flask_secret_key -
```

**4. Nginx Reverse Proxy**

Agregar servicio nginx en `docker-compose.yml`:

```yaml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
    - ./ssl:/etc/nginx/ssl
  depends_on:
    - web
```

**5. SSL/TLS**

```bash
# Usar Let's Encrypt con Certbot
docker run -it --rm \
  -v /etc/letsencrypt:/etc/letsencrypt \
  certbot/certbot certonly --webroot
```

---

## Recursos Adicionales

- **Docker Docs**: https://docs.docker.com
- **Docker Compose**: https://docs.docker.com/compose
- **Perplexity API**: https://docs.perplexity.ai
- **WhatsApp Business API**: https://developers.facebook.com/docs/whatsapp
- **PostgreSQL**: https://www.postgresql.org/docs

---

**¿Problemas?** Abre un issue en: https://github.com/Curcolor/ProntoaWeb/issues
