#!/bin/sh
set -eu

if [ -n "${PMS_DB_HOST:-${DB_HOST:-}}" ] && [ -n "${PMS_DB_PORT:-${DB_PORT:-}}" ] && [ -n "${PMS_DB_NAME:-${DB_NAME:-}}" ] && [ -n "${PMS_DB_USER:-${DB_USER:-}}" ] && [ -n "${PMS_DB_PASSWORD:-${DB_PASSWORD:-}}" ]; then
  echo "Waiting for pms-integration database to be ready..."
  sleep 10
else
  echo "PMS_DB_* not fully configured, using local SQLite for pms-integration."
fi

echo "Running pms-integration migrations..."
python -m alembic -c /app/alembic.ini upgrade head

exec uvicorn main:app --host 0.0.0.0 --port 8001
