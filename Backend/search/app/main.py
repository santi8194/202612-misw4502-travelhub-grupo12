"""FastAPI application entry-point for the search service."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import date
from typing import AsyncIterator

from fastapi import Depends, FastAPI, HTTPException, Query
from opensearchpy import AsyncOpenSearch
from redis.asyncio import Redis as AsyncRedis

from app.application.dtos import DestinationResponse, SearchRequest, SearchResponse
from app.application.use_cases import BuscarHospedaje
from app.config import settings
from app.domain.strategies import PriceFirstStrategy
from app.infrastructure.opensearch_repository import OpenSearchHospedajeRepository
from app.infrastructure.redis_destination_repository import RedisDestinationRepository

# ── Shared state ─────────────────────────────────────────────────────────────

_os_client: AsyncOpenSearch | None = None
_repository: OpenSearchHospedajeRepository | None = None
_redis_client: AsyncRedis | None = None
_dest_repository: RedisDestinationRepository | None = None


# ── Lifespan ─────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Create the OpenSearch async client on startup; close on shutdown."""
    global _os_client, _repository, _redis_client, _dest_repository  # noqa: PLW0603

    _os_client = AsyncOpenSearch(
        hosts=[settings.opensearch_endpoint],
        http_auth=(settings.opensearch_user, settings.opensearch_password),
        use_ssl=settings.opensearch_endpoint.startswith("https"),
        verify_certs=settings.opensearch_verify_certs,
        ssl_show_warn=False,
    )
    _repository = OpenSearchHospedajeRepository(
        client=_os_client,
        index_name=settings.opensearch_index,
    )
    
    _redis_client = AsyncRedis.from_url(settings.redis_url, decode_responses=True)
    _dest_repository = RedisDestinationRepository(client=_redis_client)

    yield

    if _os_client is not None:
        await _os_client.close()
    if _redis_client is not None:
        await _redis_client.aclose()


# ── App factory ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="TravelHub Search Service",
    version="0.1.0",
    description="Microservicio de búsqueda de hospedajes para TravelHub.",
    lifespan=lifespan,
)


# ── Dependencies ─────────────────────────────────────────────────────────────


def get_use_case() -> BuscarHospedaje:
    """Provide a fully-wired BuscarHospedaje use case."""
    if _repository is None:
        raise HTTPException(
            status_code=503,
            detail="El servicio no está listo: el repositorio no ha sido inicializado",
        )
    return BuscarHospedaje(
        repository=_repository,
        strategy=PriceFirstStrategy(),
    )


def get_destination_repo() -> RedisDestinationRepository:
    """Provide the Redis-backed destination repository."""
    if _dest_repository is None:
        raise HTTPException(
            status_code=503,
            detail="El servicio no está listo: Redis no ha sido inicializado",
        )
    return _dest_repository


def validate_search_params(
    ciudad: str = Query(..., min_length=1, description="City name"),
    estado_provincia: str = Query("", description="State or province"),
    pais: str = Query(..., min_length=1, description="Country name"),
    fecha_inicio: date = Query(..., description="Check-in date (YYYY-MM-DD)"),
    fecha_fin: date = Query(..., description="Check-out date (YYYY-MM-DD)"),
    huespedes: int = Query(..., ge=1, description="Number of guests"),
) -> SearchRequest:
    """Parse and validate search query parameters.

    Raises :class:`HTTPException` (422) if business rules are violated
    (e.g. invalid date range, range > 30 days).
    """
    if fecha_fin < fecha_inicio:
        raise HTTPException(
            status_code=422,
            detail="La fecha de fin debe ser mayor o igual a la fecha de inicio",
        )

    delta = (fecha_fin - fecha_inicio).days
    if delta > 30:
        raise HTTPException(
            status_code=422,
            detail=f"El rango de fechas no debe exceder los 30 días (se solicitaron {delta} días)",
        )

    return SearchRequest(
        ciudad=ciudad,
        estado_provincia=estado_provincia,
        pais=pais,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        huespedes=huespedes,
    )


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
    """Search accommodations by destination, dates and guest count."""
    return await use_case.ejecutar(request)


@app.get(
    "/api/v1/search/destinations",
    response_model=DestinationResponse,
    tags=["Search"],
    summary="Autocomplete destinations",
)
async def autocomplete_destinations(
    q: str = Query(..., min_length=3, description="Prefijo de búsqueda (mín. 3 caracteres)"),
    repo: RedisDestinationRepository = Depends(get_destination_repo),
) -> DestinationResponse:
    """Suggest destinations whose city name starts with the given prefix."""
    results = await repo.autocomplete(q)
    return DestinationResponse(results=results)
