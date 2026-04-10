"""Endpoints de búsqueda de hospedajes y autocompletado de destinos."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.application.dtos import DestinationResponse, SearchRequest, SearchResponse
from app.application.ports import DestinationRepository
from app.application.use_cases import BuscarHospedaje
from app.dependencies import get_destination_repo, get_use_case, validate_search_params

router = APIRouter()


@router.get("/health", tags=["Ops"])
async def health() -> dict:
    """Estado del servicio."""
    return {"status": "ok", "service": "search"}


@router.get(
    "/api/v1/search",
    response_model=SearchResponse,
    tags=["Search"],
    summary="Buscar hospedajes",
)
async def search(
    request: SearchRequest = Depends(validate_search_params),
    use_case: BuscarHospedaje = Depends(get_use_case),
) -> SearchResponse:
    """
    Busca hospedajes mediante destino, fechas y cantidad de huéspedes.
    El resultado es ordenado según la estrategia activa (por defecto: precio ascendente).
    """
    return await use_case.ejecutar(request)


@router.get(
    "/api/v1/search/destinations",
    response_model=DestinationResponse,
    tags=["Search"],
    summary="Autocompletado de destinos",
)
async def autocomplete_destinations(
    q: str = Query(..., min_length=3, description="Prefijo de búsqueda (mín. 3 caracteres)"),
    repo: DestinationRepository = Depends(get_destination_repo),
) -> DestinationResponse:
    """
    Sugiere destinos (ciudad, provincia, país) cuyo nombre de ciudad comienza
    con el prefijo indicado. Mínimo 3 caracteres.
    """
    results = await repo.autocomplete(q)
    return DestinationResponse(results=results)
