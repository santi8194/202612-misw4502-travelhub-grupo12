#!/bin/sh
set -eu

if [ -n "${PARTNER_DB_HOST:-${DB_HOST:-}}" ] && [ -n "${PARTNER_DB_PORT:-${DB_PORT:-}}" ] && [ -n "${PARTNER_DB_NAME:-${DB_NAME:-}}" ] && [ -n "${PARTNER_DB_USER:-${DB_USER:-}}" ] && [ -n "${PARTNER_DB_PASSWORD:-${DB_PASSWORD:-}}" ]; then
  echo "Waiting for partner-management database to be ready..."
  sleep 10
else
  echo "PARTNER_DB_* not fully configured, using local SQLite for partner-management."
fi

echo "Running partner-management migrations..."
python -m alembic -c /app/alembic.ini upgrade head

exec uvicorn main:app --host 0.0.0.0 --port 8000
