#!/bin/sh
set -eu

if [ -n "${DB_HOST:-}" ] && [ -n "${DB_PORT:-}" ] && [ -n "${DB_NAME:-}" ] && [ -n "${DB_USER:-}" ] && [ -n "${DB_PASSWORD:-}" ]; then
  echo "Waiting for booking database to be ready..."
  sleep 10
  echo "Running booking migrations..."
  python -m alembic -c /src/Booking/alembic.ini upgrade head
else
  echo "DB_* not fully configured, skipping booking migrations."
fi

exec uvicorn Booking.asgi:app --host 0.0.0.0 --port 8000
