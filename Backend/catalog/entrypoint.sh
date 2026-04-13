#!/bin/sh
set -eu

if [ -n "${DB_HOST:-}" ] && [ -n "${DB_PORT:-}" ] && [ -n "${DB_NAME:-}" ] && [ -n "${DB_USER:-}" ] && [ -n "${DB_PASSWORD:-}" ]; then
  echo "Waiting for catalog database to be ready..."
  sleep 10
  echo "Running catalog migrations..."
  python -m alembic -c /app/alembic.ini upgrade head
else
  echo "DB_* not fully configured, skipping catalog migrations."
fi

exec uvicorn main:app --host 0.0.0.0 --port 80
