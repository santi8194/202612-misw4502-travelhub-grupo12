"""OpenSearch adapter implementing the HospedajeRepository port."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Dict, List
from uuid import UUID

from opensearchpy import AsyncOpenSearch

from app.application.ports import HospedajeRepository
from app.domain.entities import Coordenadas, Disponibilidad, Hospedaje
from app.domain.strategies import RankingStrategy


class OpenSearchHospedajeRepository(HospedajeRepository):
    """Repository backed by an OpenSearch index.

    The query delegates **all** filtering of dates and availability
    to OpenSearch using nested queries, complying with the performance
    ASR that forbids doing this work in Python.
    """

    def __init__(self, client: AsyncOpenSearch, index_name: str) -> None:
        self._client = client
        self._index = index_name

    # ── Public interface ─────────────────────────────────────────────────

    async def buscar(
        self,
        ciudad: str,
        estado_provincia: str,
        pais: str,
        fecha_inicio: date,
        fecha_fin: date,
        huespedes: int,
        strategy: RankingStrategy,
    ) -> List[Hospedaje]:
        query = self._build_query(ciudad, estado_provincia, pais, fecha_inicio, fecha_fin, huespedes)
        sort = strategy.build_sort()

        body: Dict[str, Any] = {
            "query": query,
            "sort": sort,
            "size": 50,
        }

        response = await self._client.search(index=self._index, body=body)

        return [
            self._hit_to_entity(hit) for hit in response["hits"]["hits"]
        ]

    # ── Query builder ────────────────────────────────────────────────────

    @staticmethod
    def _build_query(
        ciudad: str,
        estado_provincia: str,
        pais: str,
        fecha_inicio: date,
        fecha_fin: date,
        huespedes: int,
    ) -> Dict[str, Any]:
        """
        Construye una consulta booleana (bool query) de OpenSearch con coincidencia
        de términos exactos y filtros de disponibilidad anidados.

        Usa consultas ``term`` sobre campos ``.keyword`` para coincidencias exactas
        (el frontend ahora envía valores precisos obtenidos del autocompletado).
        Por cada día en el rango [fecha_inicio, fecha_fin] añadimos un filtro anidado
        requiriendo que ``disponibilidad.fecha == day`` Y
        ``disponibilidad.cupos >= huespedes``.
        """

        must_clauses: List[Dict[str, Any]] = [
            {"term": {"ciudad.keyword": ciudad}},
            {"term": {"pais.keyword": pais}},
        ]

        if estado_provincia:
            must_clauses.append(
                {"term": {"estado_provincia.keyword": estado_provincia}}
            )

        current = fecha_inicio
        while current <= fecha_fin:
            must_clauses.append(
                {
                    "nested": {
                        "path": "disponibilidad",
                        "query": {
                            "bool": {
                                "must": [
                                    {
                                        "term": {
                                            "disponibilidad.fecha": current.isoformat()
                                        }
                                    },
                                    {
                                        "range": {
                                            "disponibilidad.cupos": {
                                                "gte": huespedes
                                            }
                                        }
                                    },
                                ]
                            }
                        },
                    }
                }
            )
            current += timedelta(days=1)

        return {"bool": {"must": must_clauses}}

    # ── Mapping helpers ──────────────────────────────────────────────────

    @staticmethod
    def _hit_to_entity(hit: Dict[str, Any]) -> Hospedaje:
        src = hit["_source"]

        coordenadas_raw = src.get("coordenadas", {})
        disponibilidad_raw = src.get("disponibilidad", [])

        return Hospedaje(
            id_propiedad=UUID(src["id_propiedad"]),
            id_categoria=UUID(src["id_categoria"]),
            propiedad_nombre=src["propiedad_nombre"],
            categoria_nombre=src["categoria_nombre"],
            imagen_principal_url=src["imagen_principal_url"],
            amenidades_destacadas=src.get("amenidades_destacadas", []),
            estrellas=src.get("estrellas", 0),
            rating_promedio=float(src.get("rating_promedio", 0.0)),
            ciudad=src["ciudad"],
            estado_provincia=src.get("estado_provincia", ""),
            pais=src["pais"],
            coordenadas=Coordenadas(
                lat=float(coordenadas_raw.get("lat", 0.0)),
                lon=float(coordenadas_raw.get("lon", 0.0)),
            ),
            capacidad_pax=src.get("capacidad_pax", 1),
            precio_base=Decimal(str(src["precio_base"])),
            moneda=src.get("moneda", "COP"),
            es_reembolsable=src.get("es_reembolsable", False),
            disponibilidad=[
                Disponibilidad(
                    fecha=date.fromisoformat(d["fecha"]),
                    cupos=int(d["cupos"]),
                )
                for d in disponibilidad_raw
            ],
        )
