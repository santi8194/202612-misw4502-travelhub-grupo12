from __future__ import annotations

import os
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

PROJECT_ROOT = Path(__file__).resolve().parents[1]

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None


def _env(*keys: str) -> str | None:
    for key in keys:
        value = os.getenv(key)
        if value:
            return value
    return None


def build_database_url() -> str:
    db_host = _env("PARTNER_DB_HOST", "DB_HOST")
    db_port = _env("PARTNER_DB_PORT", "DB_PORT") or "5432"
    db_name = _env("PARTNER_DB_NAME", "DB_NAME")
    db_user = _env("PARTNER_DB_USER", "DB_USER")
    db_password = _env("PARTNER_DB_PASSWORD", "DB_PASSWORD")

    if all([db_host, db_name, db_user, db_password]):
        return f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    data_dir = PROJECT_ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    return f"sqlite:///{(data_dir / 'partner_management.db').as_posix()}"


def run_migrations_offline() -> None:
    context.configure(
        url=build_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
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
