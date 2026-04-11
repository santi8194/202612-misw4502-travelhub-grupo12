"""Dependencias de inyección para FastAPI.

Contiene las fábricas de dependencias usadas por los endpoints de búsqueda.
Al usar `Request` se evita el acoplamiento circular con `main.py`.
"""

from __future__ import annotations

from datetime import date

from fastapi import Depends, HTTPException, Query, Request

from app.application.dtos import SearchRequest
from app.application.ports import DestinationRepository
from app.application.use_cases import BuscarHospedaje
from app.domain.strategies import PriceFirstStrategy


def get_use_case(request: Request) -> BuscarHospedaje:
    """
    Provee una instancia del caso de uso BuscarHospedaje totalmente configurada.
    Accede al repositorio desde el estado de la aplicación inyectado en el lifespan.
    """
    repository = getattr(request.app.state, "repository", None)
    if repository is None:
        raise HTTPException(
            status_code=503,
            detail="El servicio no está listo: el repositorio no ha sido inicializado",
        )
    return BuscarHospedaje(
        repository=repository,
        strategy=PriceFirstStrategy(),
    )


def get_destination_repo(request: Request) -> DestinationRepository:
    """
    Provee el repositorio de destinos respaldado por PostgreSQL.
    Accede al repositorio desde el estado de la aplicación inyectado en el lifespan.
    """
    dest_repository = getattr(request.app.state, "dest_repository", None)
    if dest_repository is None:
        raise HTTPException(
            status_code=503,
            detail="El servicio no está listo: el repositorio de destinos no ha sido inicializado",
        )
    return dest_repository


def validate_search_params(
    ciudad: str = Query(..., min_length=1, description="Nombre de la ciudad"),
    estado_provincia: str = Query("", description="Estado o provincia (opcional)"),
    pais: str = Query(..., min_length=1, description="Nombre del país"),
    fecha_inicio: date = Query(..., description="Fecha de entrada (YYYY-MM-DD)"),
    fecha_fin: date = Query(..., description="Fecha de salida (YYYY-MM-DD)"),
    huespedes: int = Query(..., ge=1, description="Número de huéspedes (mín. 1)"),
) -> SearchRequest:
    """
    Parsea y valida los parámetros de búsqueda recibidos por query string.

    La validación de reglas de negocio se delega a :class:`SearchRequest`.
    Cualquier ``ValueError`` lanzado por el DTO se traduce a HTTP 422.
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
