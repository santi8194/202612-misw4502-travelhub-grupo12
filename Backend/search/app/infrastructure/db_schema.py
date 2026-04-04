"""Módulo de inicialización del esquema de base de datos.

Contiene la función ``ensure_schema`` que crea el esquema search y todas
sus tablas e índices si no existen. Es segura de ejecutar en cada arranque
de la aplicación gracias al uso de IF NOT EXISTS en todas las sentencias.
"""

from __future__ import annotations

import asyncpg


async def ensure_schema(pool: asyncpg.Pool) -> None:
    """Crea el esquema search y las tablas necesarias si no existen.

    Función idempotente: segura de ejecutar en cada arranque de la aplicación.
    Si el esquema y las tablas ya existen, todas las sentencias son no-ops.

    Parámetros
    ----------
    pool:
        Pool de conexiones asyncpg ya inicializado.
    """
    async with pool.acquire() as conn:
        # Crear esquema search si no existe
        await conn.execute("CREATE SCHEMA IF NOT EXISTS search;")

        # Crear tabla de hospedajes con todos sus campos
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS search.hospedajes (
                id_propiedad          UUID PRIMARY KEY,
                id_categoria          UUID,
                propiedad_nombre      TEXT,
                categoria_nombre      TEXT,
                imagen_principal_url  TEXT,
                amenidades_destacadas JSONB,
                estrellas             INTEGER,
                rating_promedio       NUMERIC,
                ciudad                TEXT,
                estado_provincia      TEXT,
                pais                  TEXT,
                coordenadas           JSONB,
                capacidad_pax         INTEGER,
                precio_base           NUMERIC,
                moneda                TEXT,
                es_reembolsable       BOOLEAN,
                disponibilidad        JSONB
            );
        """)

        # Crear tabla de destinos para autocompletado
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS search.destinos (
                id_destino       UUID PRIMARY KEY,
                ciudad           TEXT NOT NULL,
                ciudad_lower     TEXT NOT NULL,
                estado_provincia TEXT,
                pais             TEXT NOT NULL,
                CONSTRAINT unq_destino UNIQUE (ciudad_lower, estado_provincia, pais)
            );
        """)

        # Crear índice de prefijo para el autocompletado eficiente (LIKE 'car%')
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_destinos_ciudad_prefix
            ON search.destinos (ciudad_lower varchar_pattern_ops);
        """)
