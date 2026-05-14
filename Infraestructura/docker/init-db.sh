#!/bin/bash
set -e

# Crear todas las bases de datos
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE catalog_db;
    CREATE DATABASE pms_db;
    CREATE DATABASE search_db;
    CREATE DATABASE booking_db;
    CREATE DATABASE payment_db;
    CREATE DATABASE auth_db;
    CREATE DATABASE partner_db;
EOSQL

# Crear el esquema 'search' específicamente dentro de search_db
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "search_db" <<-EOSQL
    CREATE SCHEMA IF NOT EXISTS search;
EOSQL
