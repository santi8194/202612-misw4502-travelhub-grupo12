#!/bin/sh
set -eu

if [ -n "${DB_HOST:-}" ] && [ -n "${DB_PORT:-}" ] && [ -n "${DB_NAME:-}" ] && [ -n "${DB_USER:-}" ] && [ -n "${DB_PASSWORD:-}" ]; then
  echo "Waiting for authservice database to be ready..."
  sleep 10
  echo "Running authservice migrations..."
  python -m alembic upgrade head
else
  echo "DB_* not fully configured, using local SQLite for authservice."
fi

exec uvicorn main:app --host 0.0.0.0 --port 8000
