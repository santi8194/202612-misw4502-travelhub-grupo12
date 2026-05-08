"""Configuración de entorno Alembic para el microservicio search."""

from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Añadir el directorio padre (search) al path para importar app
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.config import settings

# Configuración de Alembic
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata de SQLAlchemy (vacío porque search no usa ORM models)
target_metadata = None


def build_database_url() -> str:
    """Construye la URL de la base de datos desde las variables de entorno.
    
    Usa la misma lógica que app.config.settings para mantener consistencia.
    """
    if settings.use_postgres_database:
        return settings.database_url
    
    # Fallback a SQLite para desarrollo local
    return f"sqlite:///{settings.sqlite_database_path.as_posix()}"


def run_migrations_offline() -> None:
    """Ejecuta migraciones en modo 'offline'.
    
    Configura el contexto con solo una URL y no conecta realmente a la BD.
    """
    url = build_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecuta migraciones en modo 'online'.
    
    Crea una conexión real a la base de datos y ejecuta las migraciones.
    """
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = build_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
