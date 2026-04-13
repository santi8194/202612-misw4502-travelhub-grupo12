#!/bin/sh
set -eu

if [ -n "${DB_HOST:-}" ] && [ -n "${DB_PORT:-}" ] && [ -n "${DB_NAME:-}" ] && [ -n "${DB_USER:-}" ] && [ -n "${DB_PASSWORD:-}" ]; then
  echo "Waiting for search database to be ready..."
  sleep 10
  echo "Running search SQL migrations..."
  python -m app.infrastructure.db_schema
else
  echo "DB_* not fully configured, skipping search migrations."
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
