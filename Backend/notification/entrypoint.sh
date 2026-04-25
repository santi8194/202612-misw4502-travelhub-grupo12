#!/bin/sh
set -eu

if [ -n "${NOTIFICATION_DB_HOST:-${DB_HOST:-}}" ] && [ -n "${NOTIFICATION_DB_PORT:-${DB_PORT:-}}" ] && [ -n "${NOTIFICATION_DB_NAME:-${DB_NAME:-}}" ] && [ -n "${NOTIFICATION_DB_USER:-${DB_USER:-}}" ] && [ -n "${NOTIFICATION_DB_PASSWORD:-${DB_PASSWORD:-}}" ]; then
  echo "Waiting for notification database to be ready..."
  sleep 10
else
  echo "NOTIFICATION_DB_* not fully configured, using local SQLite for notification."
fi

echo "Running notification migrations..."
python -m alembic -c /app/alembic.ini upgrade head

exec uvicorn main:app --host 0.0.0.0 --port 8000
