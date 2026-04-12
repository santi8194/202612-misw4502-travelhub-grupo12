\set ON_ERROR_STOP on

-- Variables esperadas via psql -v:
-- authservice_password, booking_password, catalog_password, search_password

SELECT
  format(
    'CREATE ROLE authservice_app LOGIN PASSWORD %L',
    :'authservice_password'
  )
WHERE NOT EXISTS (
  SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = 'authservice_app'
)\gexec

SELECT format(
  'ALTER ROLE authservice_app WITH LOGIN PASSWORD %L',
  :'authservice_password'
)\gexec

SELECT
  format(
    'CREATE ROLE booking_app LOGIN PASSWORD %L',
    :'booking_password'
  )
WHERE NOT EXISTS (
  SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = 'booking_app'
)\gexec

SELECT format(
  'ALTER ROLE booking_app WITH LOGIN PASSWORD %L',
  :'booking_password'
)\gexec

SELECT
  format(
    'CREATE ROLE catalog_app LOGIN PASSWORD %L',
    :'catalog_password'
  )
WHERE NOT EXISTS (
  SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = 'catalog_app'
)\gexec

SELECT format(
  'ALTER ROLE catalog_app WITH LOGIN PASSWORD %L',
  :'catalog_password'
)\gexec

SELECT
  format(
    'CREATE ROLE search_app LOGIN PASSWORD %L',
    :'search_password'
  )
WHERE NOT EXISTS (
  SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = 'search_app'
)\gexec

SELECT format(
  'ALTER ROLE search_app WITH LOGIN PASSWORD %L',
  :'search_password'
)\gexec

SELECT 'CREATE DATABASE authservice_db OWNER authservice_app'
WHERE NOT EXISTS (
  SELECT 1 FROM pg_database WHERE datname = 'authservice_db'
)\gexec

SELECT 'CREATE DATABASE booking_db OWNER booking_app'
WHERE NOT EXISTS (
  SELECT 1 FROM pg_database WHERE datname = 'booking_db'
)\gexec

SELECT 'CREATE DATABASE catalog_db OWNER catalog_app'
WHERE NOT EXISTS (
  SELECT 1 FROM pg_database WHERE datname = 'catalog_db'
)\gexec

SELECT 'CREATE DATABASE search_db OWNER search_app'
WHERE NOT EXISTS (
  SELECT 1 FROM pg_database WHERE datname = 'search_db'
)\gexec

ALTER DATABASE authservice_db OWNER TO authservice_app;
REVOKE ALL ON DATABASE authservice_db FROM PUBLIC;
GRANT CONNECT ON DATABASE authservice_db TO authservice_app;

REVOKE ALL ON DATABASE booking_db FROM PUBLIC;
GRANT CONNECT ON DATABASE booking_db TO booking_app;

REVOKE ALL ON DATABASE catalog_db FROM PUBLIC;
GRANT CONNECT ON DATABASE catalog_db TO catalog_app;

REVOKE ALL ON DATABASE search_db FROM PUBLIC;
GRANT CONNECT ON DATABASE search_db TO search_app;

\connect authservice_db
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE, CREATE ON SCHEMA public TO authservice_app;
ALTER ROLE authservice_app IN DATABASE authservice_db SET search_path = public;

\connect booking_db
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE, CREATE ON SCHEMA public TO booking_app;
ALTER ROLE booking_app IN DATABASE booking_db SET search_path = public;

\connect catalog_db
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE, CREATE ON SCHEMA public TO catalog_app;
ALTER ROLE catalog_app IN DATABASE catalog_db SET search_path = public;

\connect search_db
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
CREATE SCHEMA IF NOT EXISTS search AUTHORIZATION search_app;
REVOKE ALL ON SCHEMA search FROM PUBLIC;
GRANT USAGE, CREATE ON SCHEMA search TO search_app;
ALTER ROLE search_app IN DATABASE search_db SET search_path = search, public;
