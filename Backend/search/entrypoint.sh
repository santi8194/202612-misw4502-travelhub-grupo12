#!/bin/sh
set -eu

if [ -n "${DB_HOST:-}" ] && [ -n "${DB_PORT:-}" ] && [ -n "${DB_NAME:-}" ] && [ -n "${DB_USER:-}" ] && [ -n "${DB_PASSWORD:-}" ]; then
  echo "Waiting for search database to be ready..."
  sleep 10
else
  echo "DB_* not fully configured, initializing local SQLite for search."
fi

python -m app.infrastructure.db_schema

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
