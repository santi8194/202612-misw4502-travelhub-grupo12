#!/usr/bin/env python3
"""Seed the local OpenSearch index with fake accommodation data.

Usage
-----
1. Start OpenSearch:  ``docker compose up -d``
2. Wait ~30 s for the cluster to become green.
3. Run this script:   ``python scripts/seed_data.py``

The script will:
  - Create the ``hospedajes`` index with the correct nested mapping.
  - Bulk-index a set of realistic fake properties.
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
import redis as redis_lib
import asyncpg

from opensearchpy import OpenSearch

# ── Suppress insecure-request warnings for local dev ─────────────────────────
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ── Configuration ────────────────────────────────────────────────────────────

OS_HOST = "https://localhost:9200"
OS_USER = "admin"
OS_PASS = "MyStr0ng!Pass#2026"
INDEX = "hospedajes"
REDIS_URL = "redis://localhost:6379/0"
PG_URL = "postgresql://travelhub:travelhub@localhost:5432/travelhub"
try:
    from app.infrastructure.redis_keys import DEST_INDEX_KEY, DEST_DATA_KEY
except ImportError:
    # Fallback when running the script standalone outside the app package
    DEST_INDEX_KEY = "search:destinations:index"
    DEST_DATA_KEY = "search:destinations:data"

# ── OpenSearch client (sync, for scripting) ──────────────────────────────────

client = OpenSearch(
    hosts=[OS_HOST],
    http_auth=(OS_USER, OS_PASS),
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False,
)

redis_client = redis_lib.Redis.from_url(REDIS_URL, decode_responses=True)

# ── Index mapping ────────────────────────────────────────────────────────────

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

# ── Fake data ────────────────────────────────────────────────────────────────

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
        "ciudad": "Salento",
        "estado_provincia": "Quindío",
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
        "ciudad": "Santa Marta",
        "estado_provincia": "Magdalena",
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
        "ciudad": "Cartagena",
        "estado_provincia": "Bolívar",
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
        "ciudad": "Santa Marta",
        "estado_provincia": "Magdalena",
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
        "ciudad": "Manizales",
        "estado_provincia": "Caldas",
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


def _generate_availability(base_date: date, days: int = 60) -> list[dict]:
    """Generate daily availability starting from *base_date*."""
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
    """Build an OpenSearch document from a property definition."""
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


def _seed_redis_destinations() -> None:
    """Extract unique destinations from PROPERTIES and insert into Redis.

    Each unique (ciudad, estado_provincia, pais) tuple gets a single entry.
    Uses uuid5 for deterministic, stable IDs per destination.
    """
    print("🔴  Poblando Redis con destinos únicos...")
    redis_client.delete(DEST_INDEX_KEY, DEST_DATA_KEY)

    seen: set[tuple[str, str, str]] = set()
    pipe = redis_client.pipeline()
    count = 0

    for prop in PROPERTIES:
        ciudad = prop["ciudad"]
        estado_provincia = prop.get("estado_provincia", "")
        pais = prop["pais"]
        key_tuple = (ciudad, estado_provincia, pais)

        if key_tuple in seen:
            continue
        seen.add(key_tuple)

        # ID determinista basado en la combinación única
        dest_id = str(uuid5(NAMESPACE_DNS, f"{ciudad}|{estado_provincia}|{pais}"))
        ciudad_lower = ciudad.lower()

        # A. Sorted Set — índice lexicográfico (score=0 para orden lexicográfico)
        pipe.zadd(DEST_INDEX_KEY, {f"{ciudad_lower}:{dest_id}": 0})

        # B. Hash — payload completo como JSON
        payload = json.dumps({
            "ciudad": ciudad,
            "estado_provincia": estado_provincia,
            "pais": pais,
        })
        pipe.hset(DEST_DATA_KEY, dest_id, payload)
        count += 1

    pipe.execute()
    print(f"   ✅  {count} destinos únicos insertados en Redis.")

async def _seed_postgres_async(docs: list[dict]) -> None:
    print("\n🐘  Poblando PostgreSQL con hospedajes...")
    try:
        conn = await asyncpg.connect(PG_URL)
    except Exception as e:
        print(f"   ⚠️  No se pudo conectar a PostgreSQL: {e}")
        return

    # Ensure table exists
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS hospedajes (
            id_propiedad UUID PRIMARY KEY,
            id_categoria UUID,
            propiedad_nombre TEXT,
            categoria_nombre TEXT,
            imagen_principal_url TEXT,
            amenidades_destacadas JSONB,
            estrellas INTEGER,
            rating_promedio NUMERIC,
            ciudad TEXT,
            estado_provincia TEXT,
            pais TEXT,
            coordenadas JSONB,
            capacidad_pax INTEGER,
            precio_base NUMERIC,
            moneda TEXT,
            es_reembolsable BOOLEAN,
            disponibilidad JSONB
        );
    """)

    await conn.execute("TRUNCATE TABLE hospedajes;")

    count = 0
    for doc in docs:
        await conn.execute("""
            INSERT INTO hospedajes (
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
        count += 1
    
    await conn.close()
    print(f"   ✅  {count} hospedajes insertados en PostgreSQL.")

def _seed_postgres(docs: list[dict]) -> None:
    asyncio.run(_seed_postgres_async(docs))


# ── Main ─────────────────────────────────────────────────────────────────────


def main() -> None:
    # 1. Delete index if it already exists
    if client.indices.exists(index=INDEX):
        print(f"🗑  Deleting existing index '{INDEX}'...")
        client.indices.delete(index=INDEX)

    # 2. Create index with nested mapping
    print(f"📦  Creating index '{INDEX}' with nested mapping...")
    client.indices.create(index=INDEX, body=MAPPING)

    # 3. Index documents
    print(f"📝  Indexing {len(PROPERTIES)} accommodations...")
    docs_inserted = []
    for prop in PROPERTIES:
        doc = _build_document(prop)
        resp = client.index(index=INDEX, body=doc, refresh=True)
        docs_inserted.append(doc)
        print(f"   ✅  {prop['nombre']} ({prop['ciudad']}) → {resp['_id']}")

    # 3b. Seed Redis with unique destinations
    _seed_redis_destinations()
    
    # 3c. Seed PostgreSQL
    _seed_postgres(docs_inserted)

    # 4. Verify
    count = client.count(index=INDEX)["count"]
    print(f"\n🎉  Done! {count} documents indexed in '{INDEX}'.")

    # 5. Show sample query
    print("\n" + "=" * 60)
    print("🔍  Sample query: Cartagena, 2 guests, next 3 days")
    print("=" * 60)
    today = date.today()
    sample_query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"ciudad.keyword": "Cartagena"}},
                    {"term": {"pais.keyword": "Colombia"}},
                ]
                + [
                    {
                        "nested": {
                            "path": "disponibilidad",
                            "query": {
                                "bool": {
                                    "must": [
                                        {
                                            "term": {
                                                "disponibilidad.fecha": (
                                                    today + timedelta(days=d)
                                                ).isoformat()
                                            }
                                        },
                                        {
                                            "range": {
                                                "disponibilidad.cupos": {"gte": 2}
                                            }
                                        },
                                    ]
                                }
                            },
                        }
                    }
                    for d in range(3)
                ]
            }
        },
        "sort": [{"precio_base": {"order": "asc"}}],
    }

    result = client.search(index=INDEX, body=sample_query)
    hits = result["hits"]["hits"]
    print(f"\n   Found {len(hits)} results:\n")
    for hit in hits:
        src = hit["_source"]
        print(
            f"   🏨  {src['propiedad_nombre']} | "
            f"${src['precio_base']:,.0f} {src['moneda']} | "
            f"⭐ {src['rating_promedio']} | "
            f"{src['ciudad']}, {src['pais']}"
        )

    if not hits:
        print("   (No results – availability is random, try again or edit seed data)")


if __name__ == "__main__":
    main()
