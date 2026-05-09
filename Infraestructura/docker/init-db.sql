-- Script para crear todas las bases de datos de TravelHub en un solo PostgreSQL
CREATE DATABASE catalog_db;
CREATE DATABASE pms_db;
CREATE DATABASE search_db;
CREATE DATABASE booking_db;
CREATE DATABASE payment_db;
CREATE DATABASE auth_db;
CREATE DATABASE partner_db;

-- Opcional: Crear un usuario único para todos los micros para simplificar desarrollo local
-- CREATE USER travelhub_user WITH PASSWORD 'travelhub_pass';
-- GRANT ALL PRIVILEGES ON DATABASE catalog_db TO travelhub_user;
-- ...
