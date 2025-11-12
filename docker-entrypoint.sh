#!/bin/bash
set -e

echo "🚀 Iniciando ProntoaWEB..."

# Esperar a que PostgreSQL esté listo
echo "⏳ Esperando a PostgreSQL..."
while ! pg_isready -h db -p 5432 -U prontoa_user > /dev/null 2>&1; do
    sleep 1
done
echo "✅ PostgreSQL está listo"

# Verificar si las tablas ya existen
TABLE_EXISTS=$(PGPASSWORD=prontoa_pass psql -h db -U prontoa_user -d prontoa_db -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_name='users';")

if [ "$TABLE_EXISTS" = "0" ]; then
    echo "📊 Base de datos vacía, ejecutando seed..."
    python -m app.scripts.seed_database
    echo "✅ Base de datos inicializada con datos de prueba"
else
    echo "ℹ️  Base de datos ya inicializada, omitiendo seed"
fi

# Iniciar la aplicación Flask
echo "🌐 Iniciando servidor Flask en puerto 5000..."
exec python run.py
