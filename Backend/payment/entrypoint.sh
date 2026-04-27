#!/bin/sh
set -eu

if [ -n "${PAYMENT_DB_HOST:-${DB_HOST:-}}" ] && [ -n "${PAYMENT_DB_PORT:-${DB_PORT:-}}" ] && [ -n "${PAYMENT_DB_NAME:-${DB_NAME:-}}" ] && [ -n "${PAYMENT_DB_USER:-${DB_USER:-}}" ] && [ -n "${PAYMENT_DB_PASSWORD:-${DB_PASSWORD:-}}" ]; then
  echo "Waiting for payment database to be ready..."
  sleep 10
else
  echo "PAYMENT_DB_* not fully configured, using local SQLite for payment."
fi

echo "Running payment migrations..."
python -m alembic -c /app/alembic.ini upgrade head

exec uvicorn main:app --host 0.0.0.0 --port 8002
