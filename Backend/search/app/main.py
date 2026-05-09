"""FastAPI entrypoint for the search micro-service."""

from __future__ import annotations

import threading
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers.search import router
from app.infrastructure.rabbitmq_consumer import RabbitMQConsumer
from app.infrastructure.event_handlers import handle_event


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize the repositories required by the service."""
    os_client = None
    pg_pool = None

    if settings.use_postgres_database:
        import asyncpg

        from app.infrastructure.postgres_destination_repository import (
            PostgresDestinationRepository,
        )

        pg_pool = await asyncpg.create_pool(settings.database_url)
        app.state.pg_pool = pg_pool
        app.state.dest_repository = PostgresDestinationRepository(pool=pg_pool)

        if settings.repository_type == "postgres":
            from app.infrastructure.postgres_repository import (
                PostgresHospedajeRepository,
            )

            app.state.repository = PostgresHospedajeRepository(pool=pg_pool)
        else:
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
    else:
        from app.infrastructure.db_schema import ensure_local_sqlite_database
        from app.infrastructure.sqlite_destination_repository import (
            SQLiteDestinationRepository,
        )
        from app.infrastructure.sqlite_repository import SQLiteHospedajeRepository

        ensure_local_sqlite_database()
        sqlite_path = str(settings.sqlite_database_path)
        app.state.dest_repository = SQLiteDestinationRepository(db_path=sqlite_path)

        if settings.repository_type == "postgres":
            app.state.repository = SQLiteHospedajeRepository(db_path=sqlite_path)
        else:
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
    
    if settings.enable_events:
        def event_handler_wrapper(data, routing_key):
            handle_event(data, routing_key, pg_pool)
        
        consumer = RabbitMQConsumer(event_handler_wrapper)
        consumer_thread = threading.Thread(target=consumer.start, daemon=True)
        consumer_thread.start()
        app.state.rabbitmq_consumer = consumer
        print("[SEARCH] RabbitMQ consumer iniciado en thread daemon")

    yield

    if os_client:
        await os_client.close()
    if pg_pool:
        await pg_pool.close()
    if settings.enable_events and hasattr(app.state, 'rabbitmq_consumer'):
        app.state.rabbitmq_consumer.stop()


app = FastAPI(
    title="TravelHub Search Service",
    version="0.1.0",
    description="Microservicio de busqueda de hospedajes para TravelHub.",
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
