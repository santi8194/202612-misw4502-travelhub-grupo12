#!/usr/bin/env python3
"""Pobla las fuentes de datos locales con hospedajes de prueba.

Uso
---
1. Levantar la infraestructura:  ``docker compose up -d``
2. Esperar ~10 s a que los contenedores estén listos.
3. Ejecutar este script:         ``python scripts/seed_data.py``

El script siempre ejecuta:
  - Crea el esquema ``search`` si no existe.
  - Crea e inserta 8 hospedajes colombianos en **search.hospedajes**.
  - Crea e inserta destinos únicos en **search.destinos** para autocompletado.

Si OpenSearch está disponible (contenedor descomentado en docker-compose):
  - Crea el índice ``hospedajes`` con el mapping ``nested`` correcto.
  - Inserta los mismos documentos en OpenSearch.
  En caso contrario, muestra una advertencia y continúa.
"""

from __future__ import annotations

import asyncio
import json
import random
import urllib3
import uuid
from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4, uuid5, NAMESPACE_DNS
import asyncpg

# ── Suprimir advertencias de certificados SSL en desarrollo ───────────────────
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ── Configuración ─────────────────────────────────────────────────────────────

OS_HOST = "https://localhost:9200"
OS_USER = "admin"
OS_PASS = "MyStr0ng!Pass#2026"
INDEX = "hospedajes"
PG_URL = None  # Se construye dinámicamente desde app.config.settings

# ── Mapping del índice OpenSearch ─────────────────────────────────────────────

MAPPING = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
    },
    "mappings": {
        "properties": {
            "id_propiedad": {"type": "keyword"},
            "id_categoria": {"type": "keyword"},
            "propiedad_nombre": {"type": "text"},
            "categoria_nombre": {"type": "keyword"},
            "imagen_principal_url": {"type": "keyword", "index": False},
            "amenidades_destacadas": {"type": "keyword"},
            "estrellas": {"type": "integer"},
            "rating_promedio": {"type": "float"},
            "ciudad": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "estado_provincia": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword"}},
            },
            "pais": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "coordenadas": {"type": "geo_point"},
            "capacidad_pax": {"type": "integer"},
            "precio_base": {"type": "float"},
            "moneda": {"type": "keyword"},
            "es_reembolsable": {"type": "boolean"},
            "disponibilidad": {
                "type": "nested",
                "properties": {
                    "fecha": {"type": "date", "format": "yyyy-MM-dd"},
                    "cupos": {"type": "integer"},
                },
            },
        }
    },
}

# ── Datos de prueba ───────────────────────────────────────────────────────────

PROPERTIES = [
    {
        "nombre": "Hotel Boutique Las Palmas",
        "categoria": "Hotel",
        "ciudad": "Cartagena",
        "estado_provincia": "Bolívar",
        "pais": "Colombia",
        "lat": 10.3910,
        "lon": -75.5346,
        "estrellas": 5,
        "rating": 4.8,
        "precio": 450000,
        "capacidad": 4,
        "amenidades": ["Piscina", "WiFi", "Spa", "Restaurante", "Gym"],
        "imagen": "https://cdn.travelhub.example/hotel-boutique-las-palmas.jpg",
    },
    {
        "nombre": "Hostal El Viajero",
        "categoria": "Hostal",
        "ciudad": "Bogotá",
        "estado_provincia": "Cundinamarca",
        "pais": "Colombia",
        "lat": 4.6097,
        "lon": -74.0817,
        "estrellas": 3,
        "rating": 4.2,
        "precio": 85000,
        "capacidad": 2,
        "amenidades": ["WiFi", "Cocina compartida", "Lavandería"],
        "imagen": "https://cdn.travelhub.example/hostal-el-viajero.jpg",
    },
    {
        "nombre": "Cabaña Montaña Mágica",
        "categoria": "Cabaña",
        "ciudad": "Medellín",
        "estado_provincia": "Antioquia",
        "pais": "Colombia",
        "lat": 4.6380,
        "lon": -75.5680,
        "estrellas": 4,
        "rating": 4.9,
        "precio": 220000,
        "capacidad": 6,
        "amenidades": ["Chimenea", "BBQ", "Jardín", "WiFi"],
        "imagen": "https://cdn.travelhub.example/cabana-montana-magica.jpg",
    },
    {
        "nombre": "Resort Playa Dorada",
        "categoria": "Resort",
        "ciudad": "Medellín",
        "estado_provincia": "Antioquia",
        "pais": "Colombia",
        "lat": 11.2408,
        "lon": -74.1990,
        "estrellas": 5,
        "rating": 4.6,
        "precio": 680000,
        "capacidad": 8,
        "amenidades": ["Playa privada", "All-inclusive", "Piscina", "Spa", "WiFi"],
        "imagen": "https://cdn.travelhub.example/resort-playa-dorada.jpg",
    },
    {
        "nombre": "Apartamento Centro Histórico",
        "categoria": "Apartamento",
        "ciudad": "Medellín",
        "estado_provincia": "Antioquia",
        "pais": "Colombia",
        "lat": 10.4236,
        "lon": -75.5490,
        "estrellas": 4,
        "rating": 4.5,
        "precio": 320000,
        "capacidad": 5,
        "amenidades": ["WiFi", "Cocina", "Aire acondicionado", "Balcón"],
        "imagen": "https://cdn.travelhub.example/apto-centro-historico.jpg",
    },
    {
        "nombre": "Eco Lodge Tayrona",
        "categoria": "Lodge",
        "ciudad": "Medellín",
        "estado_provincia": "Antioquia",
        "pais": "Colombia",
        "lat": 11.3189,
        "lon": -74.0854,
        "estrellas": 3,
        "rating": 4.7,
        "precio": 180000,
        "capacidad": 3,
        "amenidades": ["Eco-friendly", "Senderismo", "Playa", "Hamacas"],
        "imagen": "https://cdn.travelhub.example/eco-lodge-tayrona.jpg",
    },
    {
        "nombre": "Hotel Lleras Premium",
        "categoria": "Hotel",
        "ciudad": "Medellín",
        "estado_provincia": "Antioquia",
        "pais": "Colombia",
        "lat": 6.2084,
        "lon": -75.5672,
        "estrellas": 4,
        "rating": 4.4,
        "precio": 290000,
        "capacidad": 3,
        "amenidades": ["Rooftop bar", "WiFi", "Gym", "Restaurante"],
        "imagen": "https://cdn.travelhub.example/hotel-lleras-premium.jpg",
    },
    {
        "nombre": "Finca Cafetera La Esperanza",
        "categoria": "Finca",
        "ciudad": "Medellín",
        "estado_provincia": "Antioquia",
        "pais": "Colombia",
        "lat": 5.0689,
        "lon": -75.5174,
        "estrellas": 4,
        "rating": 4.8,
        "precio": 195000,
        "capacidad": 10,
        "amenidades": ["Tour de café", "Piscina", "Naturaleza", "WiFi", "BBQ"],
        "imagen": "https://cdn.travelhub.example/finca-cafetera.jpg",
    },
]


# ── Helpers de generación de datos ────────────────────────────────────────────


def _generate_availability(base_date: date, days: int = 60) -> list[dict]:
    """Genera disponibilidad diaria a partir de *base_date* por *days* días."""
    availability = []
    for i in range(days):
        cupos = random.choice([0, 0, 1, 2, 3, 4, 5, 6, 8, 10])
        availability.append(
            {
                "fecha": (base_date + timedelta(days=i)).isoformat(),
                "cupos": cupos,
            }
        )
    return availability


def _build_document(prop: dict) -> dict:
    """Construye un documento de hospedaje a partir de una definición de propiedad."""
    today = date.today()
    return {
        "id_propiedad": str(uuid4()),
        "id_categoria": str(uuid4()),
        "propiedad_nombre": prop["nombre"],
        "categoria_nombre": prop["categoria"],
        "imagen_principal_url": prop["imagen"],
        "amenidades_destacadas": prop["amenidades"],
        "estrellas": prop["estrellas"],
        "rating_promedio": prop["rating"],
        "ciudad": prop["ciudad"],
        "estado_provincia": prop["estado_provincia"],
        "pais": prop["pais"],
        "coordenadas": {"lat": prop["lat"], "lon": prop["lon"]},
        "capacidad_pax": prop["capacidad"],
        "precio_base": prop["precio"],
        "moneda": "COP",
        "es_reembolsable": random.choice([True, False]),
        "disponibilidad": _generate_availability(today),
    }


# ── Funciones de seed por motor ───────────────────────────────────────────────


def _seed_opensearch(docs: list[dict]) -> None:
    """Pobla el índice de OpenSearch.

    Esta función es opcional: solo se ejecuta si OpenSearch está disponible.
    El cliente se crea aquí dentro para evitar fallos al importar el módulo
    cuando OpenSearch no está corriendo.
    """
    from opensearchpy import OpenSearch

    os_client = OpenSearch(
        hosts=[OS_HOST],
        http_auth=(OS_USER, OS_PASS),
        use_ssl=True,
        verify_certs=False,
        ssl_show_warn=False,
    )

    print(f"\n🔵  Poblando OpenSearch...")

    # Eliminar índice existente si hay uno
    if os_client.indices.exists(index=INDEX):
        print(f"   🗑  Eliminando índice existente '{INDEX}'...")
        os_client.indices.delete(index=INDEX)

    # Crear índice con mapping nested
    print(f"   📦  Creando índice '{INDEX}' con mapping nested...")
    os_client.indices.create(index=INDEX, body=MAPPING)

    # Indexar documentos
    print(f"   📝  Indexando {len(docs)} hospedajes...")
    for doc in docs:
        resp = os_client.index(index=INDEX, body=doc, refresh=True)
        print(f"      ✅  {doc['propiedad_nombre']} ({doc['ciudad']}) → {resp['_id']}")

    count = os_client.count(index=INDEX)["count"]
    print(f"   🎉  {count} documentos indexados en '{INDEX}'.")


async def _seed_postgres_async(docs: list[dict]) -> None:
    """Inserta hospedajes y destinos en PostgreSQL de forma asíncrona.

    Reutiliza ensure_schema() para crear el esquema y las tablas si no existen,
    garantizando que el DDL tenga una única fuente de verdad.
    """
    import sys
    import os
    # Permitir importar desde el paquete app cuando se ejecuta el script directamente
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from app.infrastructure.db_schema import ensure_schema
    from app.config import settings

    print("\n🐘  Poblando PostgreSQL...")
    try:
        # Forzar localhost ya que este script usualmente se corre fuera de Docker
        settings.db_host = "localhost"
        pool = await asyncpg.create_pool(settings.database_url)
    except Exception as e:
        print(f"   ⚠️  No se pudo conectar a PostgreSQL: {e}")
        return

    # Crear esquema y tablas reutilizando la misma lógica que usa la aplicación
    await ensure_schema(pool)
    print("   ✅  Esquema 'search', tablas e índices listos.")

    # Limpiar datos previos para un seed limpio
    async with pool.acquire() as conn:
        await conn.execute("TRUNCATE TABLE search.hospedajes;")
        await conn.execute("TRUNCATE TABLE search.destinos;")

    # Insertar hospedajes
    print(f"   📝  Insertando {len(docs)} hospedajes en search.hospedajes...")
    count_hospedajes = 0
    async with pool.acquire() as conn:
        for doc in docs:
            await conn.execute("""
                INSERT INTO search.hospedajes (
                    id_propiedad, id_categoria, propiedad_nombre, categoria_nombre,
                    imagen_principal_url, amenidades_destacadas, estrellas, rating_promedio,
                    ciudad, estado_provincia, pais, coordenadas, capacidad_pax,
                    precio_base, moneda, es_reembolsable, disponibilidad
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17
                )
            """,
                uuid.UUID(doc["id_propiedad"]),
                uuid.UUID(doc["id_categoria"]),
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
            count_hospedajes += 1

    print(f"   ✅  {count_hospedajes} hospedajes insertados en search.hospedajes.")

    # Insertar destinos únicos en search.destinos
    # Se extraen combinaciones únicas (ciudad, estado_provincia, pais) de PROPERTIES
    print("   📝  Insertando destinos únicos en search.destinos...")
    seen: set[tuple[str, str, str]] = set()
    count_destinos = 0

    async with pool.acquire() as conn:
        for prop in PROPERTIES:
            ciudad = prop["ciudad"]
            estado_provincia = prop.get("estado_provincia", "")
            pais = prop["pais"]
            ciudad_lower = ciudad.lower()
            key_tuple = (ciudad_lower, estado_provincia, pais)

            if key_tuple in seen:
                continue
            seen.add(key_tuple)

            # ID determinista para mantener estabilidad entre ejecuciones del seed
            dest_id = uuid5(NAMESPACE_DNS, f"{ciudad}|{estado_provincia}|{pais}")

            await conn.execute("""
                INSERT INTO search.destinos (id_destino, ciudad, ciudad_lower, estado_provincia, pais)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT DO NOTHING
            """,
                dest_id,
                ciudad,
                ciudad_lower,
                estado_provincia,
                pais,
            )
            count_destinos += 1

    print(f"   ✅  {count_destinos} destinos únicos insertados en search.destinos.")

    await pool.close()


def _seed_postgres(docs: list[dict]) -> None:
    """Wrapper síncrono para la inserción asíncrona en PostgreSQL."""
    asyncio.run(_seed_postgres_async(docs))


# ── Main ──────────────────────────────────────────────────────────────────────


def main() -> None:
    """Ejecuta el proceso de seed en todos los motores disponibles."""

    # 1. Generar los documentos de prueba
    print(f"📝  Generando {len(PROPERTIES)} hospedajes de prueba...")
    docs = [_build_document(prop) for prop in PROPERTIES]
    for doc in docs:
        print(f"   ✅  {doc['propiedad_nombre']} ({doc['ciudad']})")

    # 2. Intentar seed en OpenSearch (opcional: solo si el contenedor está corriendo)
    try:
        _seed_opensearch(docs)
    except Exception as e:
        print(f"\n⚠️  OpenSearch no está disponible, omitiendo: {e}")
        print("   Para activarlo, descomenta los servicios en docker-compose.yml")

    # 3. Seed PostgreSQL (siempre — hospedajes y destinos)
    _seed_postgres(docs)

    print("\n🎉  Seed completado.")


if __name__ == "__main__":
    main()
