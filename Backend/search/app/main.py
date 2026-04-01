"""FastAPI application entry-point for the search service."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import date
from typing import AsyncIterator

from fastapi import Depends, FastAPI, HTTPException, Query
from opensearchpy import AsyncOpenSearch
from redis.asyncio import Redis as AsyncRedis

from app.application.dtos import DestinationResponse, SearchRequest, SearchResponse
from app.application.ports import DestinationRepository
from app.application.use_cases import BuscarHospedaje
from app.config import settings
from app.domain.strategies import PriceFirstStrategy
from app.infrastructure.opensearch_repository import OpenSearchHospedajeRepository
from app.infrastructure.postgres_repository import PostgresHospedajeRepository
from app.infrastructure.redis_destination_repository import RedisDestinationRepository
import asyncpg



# ── Lifespan ─────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Create shared clients on startup; close gracefully on shutdown."""
    os_client = AsyncOpenSearch(
        hosts=[settings.opensearch_endpoint],
        http_auth=(settings.opensearch_user, settings.opensearch_password),
        use_ssl=settings.opensearch_endpoint.startswith("https"),
        verify_certs=settings.opensearch_verify_certs,
        ssl_show_warn=False,
    )
    redis_client = AsyncRedis.from_url(settings.redis_url, decode_responses=True)

    app.state.os_client = os_client
    app.state.redis_client = redis_client
    app.state.dest_repository = RedisDestinationRepository(client=redis_client)

    if settings.repository_type == "postgres":
        pg_pool = await asyncpg.create_pool(settings.postgres_url)
        app.state.pg_pool = pg_pool
        app.state.repository = PostgresHospedajeRepository(pool=pg_pool)
    else:
        app.state.repository = OpenSearchHospedajeRepository(
            client=os_client,
            index_name=settings.opensearch_index,
        )

    yield

    await os_client.close()
    await redis_client.aclose()
    if getattr(app.state, "pg_pool", None):
        await app.state.pg_pool.close()


# ── App factory ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="TravelHub Search Service",
    version="0.1.0",
    description="Microservicio de búsqueda de hospedajes para TravelHub.",
    lifespan=lifespan,
)


# ── Dependencies ─────────────────────────────────────────────────────────────


def get_use_case() -> BuscarHospedaje:
    """
    Provee una instancia del caso de uso BuscarHospedaje totalmente configurada.
    """
    if not hasattr(app.state, "repository") or app.state.repository is None:
        raise HTTPException(
            status_code=503,
            detail="El servicio no está listo: el repositorio no ha sido inicializado",
        )
    return BuscarHospedaje(
        repository=app.state.repository,
        strategy=PriceFirstStrategy(),
    )


def get_destination_repo() -> DestinationRepository:
    """
    Provee el repositorio de destinos respaldado por Redis.
    """
    if not hasattr(app.state, "dest_repository") or app.state.dest_repository is None:
        raise HTTPException(
            status_code=503,
            detail="El servicio no está listo: Redis no ha sido inicializado",
        )
    return app.state.dest_repository


def validate_search_params(
    ciudad: str = Query(..., min_length=1, description="City name"),
    estado_provincia: str = Query("", description="State or province"),
    pais: str = Query(..., min_length=1, description="Country name"),
    fecha_inicio: date = Query(..., description="Check-in date (YYYY-MM-DD)"),
    fecha_fin: date = Query(..., description="Check-out date (YYYY-MM-DD)"),
    huespedes: int = Query(..., ge=1, description="Number of guests"),
) -> SearchRequest:
    """
    Parsea y valida los parámetros de búsqueda.

    La validación de reglas de negocio se delega completamente a :class:`SearchRequest`.
    Cualquier ``ValueError`` lanzado por el DTO se traduce a un HTTP 422.
    """
    try:
        return SearchRequest(
            ciudad=ciudad,
            estado_provincia=estado_provincia,
            pais=pais,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            huespedes=huespedes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


# ── Endpoints ────────────────────────────────────────────────────────────────


@app.get("/health", tags=["Ops"])
async def health() -> dict:
    return {"status": "ok", "service": "search"}


@app.get(
    "/api/v1/search",
    response_model=SearchResponse,
    tags=["Search"],
    summary="Search accommodations",
)
async def search(
    request: SearchRequest = Depends(validate_search_params),
    use_case: BuscarHospedaje = Depends(get_use_case),
) -> SearchResponse:
    """
    Busca hospedajes mediante destino, fechas y cantidad de huéspedes.
    """
    return await use_case.ejecutar(request)


@app.get(
    "/api/v1/search/destinations",
    response_model=DestinationResponse,
    tags=["Search"],
    summary="Autocomplete destinations",
)
async def autocomplete_destinations(
    q: str = Query(..., min_length=3, description="Prefijo de búsqueda (mín. 3 caracteres)"),
    repo: DestinationRepository = Depends(get_destination_repo),
) -> DestinationResponse:
    """
    Sugiere destinos (ciudad, provincia, país) cuyo nombre de ciudad comienza con el prefijo indicado.
    """
    results = await repo.autocomplete(q)
    return DestinationResponse(results=results)
