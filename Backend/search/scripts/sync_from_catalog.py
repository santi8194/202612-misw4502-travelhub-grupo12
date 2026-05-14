#!/usr/bin/env python3
"""Sincroniza search_db con los datos actuales de catalog_db.

Uso
---
Ejecutar dentro del contenedor de search (después del seed de catalog):

    docker exec travelhub-search-orl python scripts/sync_from_catalog.py
    docker exec travelhub-search-orl python scripts/sync_from_catalog.py --purge

El flag ``--purge`` limpia las tablas search.hospedajes y search.destinos antes
de insertar, garantizando un estado limpio.

Sin ``--purge`` la inserción es idempotente: usa ON CONFLICT DO UPDATE para
hospedajes y ON CONFLICT DO NOTHING para destinos.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import sys
from pathlib import Path
from uuid import NAMESPACE_DNS, uuid5

import asyncpg

# Agregar el directorio raíz del proyecto al path para importar los módulos de search
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# ── Configuración de conexiones ───────────────────────────────────────────────

# Base de datos de catalog (solo lectura)
CATALOG_DB_HOST = os.getenv("CATALOG_DB_HOST", os.getenv("DB_HOST", "192.168.0.178"))
CATALOG_DB_PORT = int(os.getenv("CATALOG_DB_PORT", "5432"))
CATALOG_DB_NAME = os.getenv("CATALOG_DB_NAME", "catalog_db")
CATALOG_DB_USER = os.getenv("CATALOG_DB_USER", os.getenv("DB_USER", "postgres"))
CATALOG_DB_PASSWORD = os.getenv("CATALOG_DB_PASSWORD", os.getenv("DB_PASSWORD", "postgres"))

# Base de datos de search (lectura/escritura)
SEARCH_DB_HOST = os.getenv("DB_HOST", "192.168.0.178")
SEARCH_DB_PORT = int(os.getenv("DB_PORT", "5432"))
SEARCH_DB_NAME = os.getenv("DB_NAME", "search_db")
SEARCH_DB_USER = os.getenv("DB_USER", "postgres")
SEARCH_DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")


# ── Queries de lectura contra catalog_db ─────────────────────────────────────

QUERY_CATALOG = """
SELECT
    p.id_propiedad,
    p.nombre         AS propiedad_nombre,
    p.estrellas,
    p.ciudad,
    p.estado_provincia,
    p.pais,
    p.latitud,
    p.longitud,
    c.id_categoria,
    c.nombre_comercial        AS categoria_nombre,
    c.precio_base_monto,
    c.precio_base_moneda,
    c.capacidad_pax,
    c.dias_anticipacion
FROM propiedades p
JOIN categorias_habitacion c ON c.id_propiedad = p.id_propiedad
ORDER BY p.nombre, c.nombre_comercial;
"""

QUERY_AMENIDADES_POR_CATEGORIA = """
SELECT ca.id_categoria, a.nombre
FROM categoria_amenidad ca
JOIN amenidades a ON a.id_amenidad = ca.id_amenidad
ORDER BY ca.id_categoria;
"""

QUERY_INVENTARIO_POR_CATEGORIA = """
SELECT id_categoria, fecha, cupos_disponibles
FROM inventario
ORDER BY id_categoria, fecha;
"""

QUERY_PRIMERA_IMAGEN_POR_CATEGORIA = """
SELECT DISTINCT ON (id_categoria)
    id_categoria,
    url_full
FROM media
ORDER BY id_categoria, orden ASC;
"""


# ── Helpers ───────────────────────────────────────────────────────────────────


def _build_destino_id(ciudad: str, estado: str, pais: str) -> str:
    """Genera UUID determinista para un destino."""
    return str(uuid5(NAMESPACE_DNS, f"{ciudad}|{estado}|{pais}"))


def _random_rating() -> float:
    """Genera un rating aleatorio entre 3.5 y 5.0 (sin reseñas reales aún)."""
    return round(random.uniform(3.5, 5.0), 1)


# ── Lectura de catalog ────────────────────────────────────────────────────────


async def _leer_catalog(pool: asyncpg.Pool) -> tuple[list, dict, dict, dict]:
    """
    Lee todos los datos necesarios de catalog_db.

    Retorna:
        - filas: registros propiedad+categoría
        - amenidades_map: {id_categoria -> [nombre, ...]}
        - inventario_map: {id_categoria -> [{"fecha": ..., "cupos": N}, ...]}
        - imagen_map: {id_categoria -> url_full}
    """
    async with pool.acquire() as conn:
        filas = await conn.fetch(QUERY_CATALOG)

        # Cargar amenidades agrupadas por categoría
        amenidades_rows = await conn.fetch(QUERY_AMENIDADES_POR_CATEGORIA)
        amenidades_map: dict[str, list[str]] = {}
        for row in amenidades_rows:
            cid = str(row["id_categoria"])
            amenidades_map.setdefault(cid, []).append(row["nombre"])

        # Cargar inventario agrupado por categoría
        inventario_rows = await conn.fetch(QUERY_INVENTARIO_POR_CATEGORIA)
        inventario_map: dict[str, list[dict]] = {}
        for row in inventario_rows:
            cid = str(row["id_categoria"])
            inventario_map.setdefault(cid, []).append(
                {"fecha": row["fecha"], "cupos": row["cupos_disponibles"]}
            )

        # Cargar primera imagen por categoría
        imagen_rows = await conn.fetch(QUERY_PRIMERA_IMAGEN_POR_CATEGORIA)
        imagen_map: dict[str, str] = {
            str(row["id_categoria"]): row["url_full"] for row in imagen_rows
        }

    return list(filas), amenidades_map, inventario_map, imagen_map


# ── Transformación ────────────────────────────────────────────────────────────


def _construir_documentos(
    filas: list,
    amenidades_map: dict,
    inventario_map: dict,
    imagen_map: dict,
) -> list[dict]:
    """
    Transforma las filas de catalog al formato de search.hospedajes.

    Genera un documento por cada fila (propiedad+categoría).
    """
    documentos = []
    for fila in filas:
        cid = str(fila["id_categoria"])
        pid = str(fila["id_propiedad"])

        disponibilidad = inventario_map.get(cid, [])
        amenidades = amenidades_map.get(cid, [])
        imagen = imagen_map.get(cid, "https://images.unsplash.com/photo-1566073771259-6a8506099945")

        # Derivar es_reembolsable: política con días de anticipación > 0 es reembolsable
        es_reembolsable = fila["dias_anticipacion"] > 0

        documentos.append({
            "id_propiedad": pid,
            "id_categoria": cid,
            "propiedad_nombre": fila["propiedad_nombre"],
            "categoria_nombre": fila["categoria_nombre"],
            "imagen_principal_url": imagen,
            "amenidades_destacadas": amenidades,
            "estrellas": fila["estrellas"],
            "rating_promedio": _random_rating(),
            "ciudad": fila["ciudad"],
            "estado_provincia": fila["estado_provincia"],
            "pais": fila["pais"],
            "coordenadas": {"lat": fila["latitud"], "lon": fila["longitud"]},
            "capacidad_pax": fila["capacidad_pax"],
            "precio_base": float(fila["precio_base_monto"]),
            "moneda": fila["precio_base_moneda"],
            "es_reembolsable": es_reembolsable,
            "disponibilidad": disponibilidad,
        })

    return documentos


def _extraer_destinos(documentos: list[dict]) -> list[dict]:
    """
    Extrae destinos únicos desde los documentos.

    Usa un set para deduplicar por (ciudad_lower, estado_provincia, pais)
    antes de construir la lista final.
    """
    vistos: set[tuple[str, str, str]] = set()
    destinos = []

    for doc in documentos:
        ciudad = doc["ciudad"]
        estado = doc["estado_provincia"] or ""
        pais = doc["pais"]
        ciudad_lower = ciudad.lower()
        clave = (ciudad_lower, estado, pais)

        if clave in vistos:
            continue
        vistos.add(clave)

        destinos.append({
            "id_destino": _build_destino_id(ciudad, estado, pais),
            "ciudad": ciudad,
            "ciudad_lower": ciudad_lower,
            "estado_provincia": estado,
            "pais": pais,
        })

    return destinos


# ── Escritura en search ───────────────────────────────────────────────────────


async def _purgar_search(pool: asyncpg.Pool) -> None:
    """Limpia las tablas de search antes de sincronizar."""
    async with pool.acquire() as conn:
        await conn.execute("TRUNCATE TABLE search.hospedajes;")
        await conn.execute("TRUNCATE TABLE search.destinos;")
    print("   🗑  Tablas search.hospedajes y search.destinos truncadas.")


async def _insertar_hospedajes(pool: asyncpg.Pool, documentos: list[dict]) -> int:
    """
    Inserta o actualiza los hospedajes en search.hospedajes.

    Usa ON CONFLICT (id_categoria) DO UPDATE para ser idempotente.
    """
    count = 0
    async with pool.acquire() as conn:
        for doc in documentos:
            await conn.execute(
                """
                INSERT INTO search.hospedajes (
                    id_propiedad, id_categoria, propiedad_nombre, categoria_nombre,
                    imagen_principal_url, amenidades_destacadas, estrellas, rating_promedio,
                    ciudad, estado_provincia, pais, coordenadas, capacidad_pax,
                    precio_base, moneda, es_reembolsable, disponibilidad
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17
                )
                ON CONFLICT (id_categoria) DO UPDATE SET
                    id_propiedad          = EXCLUDED.id_propiedad,
                    propiedad_nombre      = EXCLUDED.propiedad_nombre,
                    categoria_nombre      = EXCLUDED.categoria_nombre,
                    imagen_principal_url  = EXCLUDED.imagen_principal_url,
                    amenidades_destacadas = EXCLUDED.amenidades_destacadas,
                    estrellas             = EXCLUDED.estrellas,
                    ciudad                = EXCLUDED.ciudad,
                    estado_provincia      = EXCLUDED.estado_provincia,
                    pais                  = EXCLUDED.pais,
                    coordenadas           = EXCLUDED.coordenadas,
                    capacidad_pax         = EXCLUDED.capacidad_pax,
                    precio_base           = EXCLUDED.precio_base,
                    moneda                = EXCLUDED.moneda,
                    es_reembolsable       = EXCLUDED.es_reembolsable,
                    disponibilidad        = EXCLUDED.disponibilidad;
                """,
                doc["id_propiedad"],
                doc["id_categoria"],
                doc["propiedad_nombre"],
                doc["categoria_nombre"],
                doc["imagen_principal_url"],
                json.dumps(doc["amenidades_destacadas"]),
                doc["estrellas"],
                doc["rating_promedio"],
                doc["ciudad"],
                doc["estado_provincia"],
                doc["pais"],
                json.dumps(doc["coordenadas"]),
                doc["capacidad_pax"],
                doc["precio_base"],
                doc["moneda"],
                doc["es_reembolsable"],
                json.dumps(doc["disponibilidad"]),
            )
            count += 1
    return count


async def _insertar_destinos(pool: asyncpg.Pool, destinos: list[dict]) -> int:
    """
    Inserta destinos únicos en search.destinos.

    Usa ON CONFLICT DO NOTHING para evitar duplicados por (ciudad_lower, estado_provincia, pais).
    """
    count = 0
    async with pool.acquire() as conn:
        for destino in destinos:
            resultado = await conn.execute(
                """
                INSERT INTO search.destinos (id_destino, ciudad, ciudad_lower, estado_provincia, pais)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT DO NOTHING;
                """,
                destino["id_destino"],
                destino["ciudad"],
                destino["ciudad_lower"],
                destino["estado_provincia"],
                destino["pais"],
            )
            # asyncpg retorna "INSERT 0 N" — contar solo si se insertó
            if resultado == "INSERT 0 1":
                count += 1
    return count


# ── Asegurar migraciones de search ────────────────────────────────────────────


async def _asegurar_migraciones(pool: asyncpg.Pool) -> None:
    """Ejecuta las migraciones pendientes de search_db antes de insertar."""
    from app.infrastructure.db_schema import ensure_schema
    await ensure_schema(pool)
    print("   ✅  Migraciones de search_db aplicadas.")


# ── Main ──────────────────────────────────────────────────────────────────────


async def _main(purge: bool) -> None:
    """
    Orquesta la sincronización completa de catalog → search.

    Args:
        purge: Si es True, trunca las tablas de search antes de insertar.
    """
    print("\n🔗  Sincronizando catalog_db → search_db...\n")

    # Conectar a catalog_db
    catalog_url = (
        f"postgresql://{CATALOG_DB_USER}:{CATALOG_DB_PASSWORD}"
        f"@{CATALOG_DB_HOST}:{CATALOG_DB_PORT}/{CATALOG_DB_NAME}"
    )
    print(f"   📖  Conectando a catalog_db ({CATALOG_DB_HOST}/{CATALOG_DB_NAME})...")
    try:
        catalog_pool = await asyncpg.create_pool(catalog_url)
    except Exception as exc:
        print(f"   ❌  No se pudo conectar a catalog_db: {exc}")
        sys.exit(1)

    # Conectar a search_db
    search_url = (
        f"postgresql://{SEARCH_DB_USER}:{SEARCH_DB_PASSWORD}"
        f"@{SEARCH_DB_HOST}:{SEARCH_DB_PORT}/{SEARCH_DB_NAME}"
    )
    print(f"   📝  Conectando a search_db ({SEARCH_DB_HOST}/{SEARCH_DB_NAME})...")
    try:
        search_pool = await asyncpg.create_pool(search_url)
    except Exception as exc:
        print(f"   ❌  No se pudo conectar a search_db: {exc}")
        await catalog_pool.close()
        sys.exit(1)

    try:
        # Asegurar migraciones de search
        await _asegurar_migraciones(search_pool)

        # Leer datos de catalog
        print("\n🐘  Leyendo datos de catalog_db...")
        filas, amenidades_map, inventario_map, imagen_map = await _leer_catalog(catalog_pool)
        print(f"   ✅  {len(filas)} registros propiedad+categoría encontrados.")
        print(f"   ✅  {len(amenidades_map)} categorías con amenidades.")
        print(f"   ✅  {len(inventario_map)} categorías con inventario.")

        if not filas:
            print("\n⚠️  No hay datos en catalog_db. Ejecuta el seed de catalog primero:")
            print("     docker exec travelhub-catalog-orl python scripts/seed_full_catalog.py --purge")
            return

        # Transformar datos
        documentos = _construir_documentos(filas, amenidades_map, inventario_map, imagen_map)
        destinos = _extraer_destinos(documentos)
        print(f"\n🔄  Transformados: {len(documentos)} hospedajes, {len(destinos)} destinos únicos.")

        # Purgar si se solicitó
        if purge:
            print("\n🗑   Purgando tablas de search_db...")
            await _purgar_search(search_pool)

        # Insertar hospedajes
        print(f"\n📝  Insertando {len(documentos)} hospedajes en search.hospedajes...")
        count_hospedajes = await _insertar_hospedajes(search_pool, documentos)
        print(f"   ✅  {count_hospedajes} hospedajes sincronizados.")

        # Insertar destinos
        print(f"📝  Insertando destinos únicos en search.destinos...")
        count_destinos = await _insertar_destinos(search_pool, destinos)
        print(f"   ✅  {count_destinos} destinos nuevos insertados ({len(destinos) - count_destinos} ya existían).")

        print("\n🎉  Sincronización completada.\n")

    finally:
        await catalog_pool.close()
        await search_pool.close()


def main() -> None:
    """Punto de entrada del script."""
    parser = argparse.ArgumentParser(
        description="Sincroniza search_db con los datos actuales de catalog_db."
    )
    parser.add_argument(
        "--purge",
        action="store_true",
        help="Trunca search.hospedajes y search.destinos antes de insertar.",
    )
    args = parser.parse_args()
    asyncio.run(_main(purge=args.purge))


if __name__ == "__main__":
    main()
