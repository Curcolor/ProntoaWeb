#!/bin/bash
set -e

echo "🚀 Iniciando ProntoaWEB..."

# Permitir comandos personalizados desde docker-compose (default: python run.py)
if [ $# -eq 0 ]; then
    set -- python run.py
fi

DB_URL=${DATABASE_URL:-postgresql://prontoa_user:prontoa_pass@db:5432/prontoa_db}

wait_for_db=${WAIT_FOR_DB:-true}
if [ "$wait_for_db" != "false" ]; then
    echo "⏳ Esperando a PostgreSQL..."
    until pg_isready -d "$DB_URL" >/dev/null 2>&1; do
        sleep 1
    done
    echo "✅ PostgreSQL está listo"
fi

if [ "${SKIP_DB_SEED:-false}" != "true" ]; then
    TABLE_EXISTS=$(psql "$DB_URL" -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_name='users';" || echo "0")
    if [ "$TABLE_EXISTS" = "0" ]; then
        echo "📊 Base de datos vacía, ejecutando seed..."
        python -m app.scripts.seed_database
        echo "✅ Base de datos inicializada con datos de prueba"
    else
        echo "ℹ️ Base de datos ya inicializada, omitiendo seed"
    fi
fi

echo "🚀 Ejecutando comando: $*"
exec "$@"
