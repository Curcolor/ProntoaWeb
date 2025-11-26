# Reiniciar el contenedor de Flask
docker-compose restart web  


# Detener, reconstruir y levantar
docker-compose down
docker-compose build
docker-compose up -d


# base de datos PostgreSQL
psql -U prontoa_user -d prontoa_db
\dt 
