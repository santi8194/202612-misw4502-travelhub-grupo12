"""Punto de entrada FastAPI para el microservicio de búsqueda.

Solo contiene el lifespan (inicialización de infraestructura) y la factory
de la aplicación. Los endpoints están en `app/routers/search.py` y las
dependencias en `app/dependencies.py`.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis as AsyncRedis

from app.config import settings
from app.infrastructure.redis_destination_repository import RedisDestinationRepository
from app.routers.search import router

# ── Lifespan ─────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Crea los clientes compartidos al inicio y los cierra al finalizar.

    El cliente OpenSearch se crea únicamente cuando `repository_type == 'opensearch'`,
    evitando conexiones innecesarias al motor que no está activo.
    """
    # Redis — siempre necesario para autocompletado de destinos
    redis_client = AsyncRedis.from_url(settings.redis_url, decode_responses=True)
    app.state.redis_client = redis_client
    app.state.dest_repository = RedisDestinationRepository(client=redis_client)

    # Variable para cleanup condicional al shutdown
    os_client = None

    if settings.repository_type == "postgres":
        # Importación lazy: no carga asyncpg si se usa OpenSearch
        import asyncpg

        from app.infrastructure.postgres_repository import PostgresHospedajeRepository

        pg_pool = await asyncpg.create_pool(settings.postgres_url)
        app.state.pg_pool = pg_pool
        app.state.repository = PostgresHospedajeRepository(pool=pg_pool)
    else:
        # Importación lazy: no carga opensearch-py si se usa Postgres
        from opensearchpy import AsyncOpenSearch

        from app.infrastructure.opensearch_repository import (
            OpenSearchHospedajeRepository,
        )

        os_client = AsyncOpenSearch(
            hosts=[settings.opensearch_endpoint],
            http_auth=(settings.opensearch_user, settings.opensearch_password),
            use_ssl=settings.opensearch_endpoint.startswith("https"),
            verify_certs=settings.opensearch_verify_certs,
            ssl_show_warn=False,
        )
        app.state.os_client = os_client
        app.state.repository = OpenSearchHospedajeRepository(
            client=os_client,
            index_name=settings.opensearch_index,
        )

    yield

    # Cleanup ordenado al shutdown
    if os_client:
        await os_client.close()
    await redis_client.aclose()
    if getattr(app.state, "pg_pool", None):
        await app.state.pg_pool.close()


# ── App factory ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="TravelHub Search Service",
    version="0.1.0",
    description="Microservicio de búsqueda de hospedajes para TravelHub.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
