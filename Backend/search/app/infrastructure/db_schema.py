"""Helpers para aplicar migraciones SQL versionadas del servicio search."""

from __future__ import annotations

import asyncio
from pathlib import Path

import asyncpg

from app.config import settings

MIGRATIONS_DIR = Path(__file__).resolve().parents[2] / "db" / "migrations"


def _migration_files() -> list[Path]:
    return sorted(path for path in MIGRATIONS_DIR.glob("*.sql") if path.is_file())


async def _ensure_migration_table(conn: asyncpg.Connection) -> None:
    await conn.execute("CREATE SCHEMA IF NOT EXISTS search;")
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS search.schema_migrations (
            version TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """
    )


async def run_migrations(pool: asyncpg.Pool) -> None:
    """Aplica una sola vez cada archivo SQL versionado en ``db/migrations``."""

    async with pool.acquire() as conn:
        await _ensure_migration_table(conn)
        rows = await conn.fetch("SELECT version FROM search.schema_migrations;")
        applied_versions = {row["version"] for row in rows}

        for migration_path in _migration_files():
            version = migration_path.stem.split("_", 1)[0]
            if version in applied_versions:
                continue

            sql = migration_path.read_text(encoding="utf-8")
            async with conn.transaction():
                await conn.execute(sql)
                await conn.execute(
                    """
                    INSERT INTO search.schema_migrations (version, filename)
                    VALUES ($1, $2)
                    """,
                    version,
                    migration_path.name,
                )


async def ensure_schema(pool: asyncpg.Pool) -> None:
    """Compatibilidad temporal para flujos que aún invocan el nombre anterior."""

    await run_migrations(pool)


async def migrate_database_from_env() -> None:
    pool = await asyncpg.create_pool(settings.database_url)
    try:
        await run_migrations(pool)
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(migrate_database_from_env())
