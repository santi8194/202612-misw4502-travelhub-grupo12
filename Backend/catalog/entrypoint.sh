#!/bin/sh
set -eu

if [ -n "${DB_HOST:-}" ] && [ -n "${DB_PORT:-}" ] && [ -n "${DB_NAME:-}" ] && [ -n "${DB_USER:-}" ] && [ -n "${DB_PASSWORD:-}" ]; then
  echo "Waiting for catalog database to be ready..."
  sleep 10
  echo "Running catalog migrations..."
  # El repositorio tiene más de una rama de migración activa; aplicar todas.
  python -m alembic -c /app/alembic.ini upgrade heads
else
  echo "DB_* not fully configured, skipping catalog migrations."
  echo "Seeding local catalog SQLite data..."
  python -m modules.catalog.infrastructure.local_seed
fi

exec uvicorn main:app --host 0.0.0.0 --port 8000
