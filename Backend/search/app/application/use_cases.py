"""Application use cases for the search service."""

from __future__ import annotations

from app.application.dtos import (
    CoordenadasDTO,
    HospedajeResponse,
    SearchRequest,
    SearchResponse,
)
from app.application.ports import HospedajeRepository
from app.domain.entities import Hospedaje
from app.domain.strategies import RankingStrategy


class BuscarHospedaje:
    """Use case: search accommodations by destination, dates and guests.

    Orchestrates the call to the repository and maps domain entities
    to response DTOs.
    """

    def __init__(
        self,
        repository: HospedajeRepository,
        strategy: RankingStrategy,
    ) -> None:
        self._repository = repository
        self._strategy = strategy

    async def ejecutar(self, request: SearchRequest) -> SearchResponse:
        """
        Ejecuta la búsqueda y retorna los resultados formateados en un DTO.
        """

        hospedajes = await self._repository.buscar(
            ciudad=request.ciudad,
            estado_provincia=request.estado_provincia,
            pais=request.pais,
            fecha_inicio=request.fecha_inicio,
            fecha_fin=request.fecha_fin,
            huespedes=request.huespedes,
            strategy=self._strategy,
        )

        resultados = [self._to_response(h) for h in hospedajes]

        return SearchResponse(
            resultados=resultados,
            total=len(resultados),
        )

    # ── Private helpers ──────────────────────────────────────────────────

    @staticmethod
    def _to_response(h: Hospedaje) -> HospedajeResponse:
        return HospedajeResponse(
            id_propiedad=h.id_propiedad,
            id_categoria=h.id_categoria,
            propiedad_nombre=h.propiedad_nombre,
            categoria_nombre=h.categoria_nombre,
            imagen_principal_url=h.imagen_principal_url,
            amenidades_destacadas=h.amenidades_destacadas,
            estrellas=h.estrellas,
            rating_promedio=h.rating_promedio,
            ciudad=h.ciudad,
            estado_provincia=h.estado_provincia,
            pais=h.pais,
            coordenadas=CoordenadasDTO(
                lat=h.coordenadas.lat,
                lon=h.coordenadas.lon,
            ),
            capacidad_pax=h.capacidad_pax,
            precio_base=h.precio_base,
            moneda=h.moneda,
            es_reembolsable=h.es_reembolsable,
        )
