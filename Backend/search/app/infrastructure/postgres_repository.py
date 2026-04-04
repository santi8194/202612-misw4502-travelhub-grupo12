"""PostgreSQL adapter implementing the HospedajeRepository port."""

from __future__ import annotations

import json
from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Dict, List

import asyncpg

from app.application.ports import HospedajeRepository
from app.domain.entities import Coordenadas, Disponibilidad, Hospedaje
from app.domain.strategies import RankingStrategy


class PostgresHospedajeRepository(HospedajeRepository):
    """Repository backed by a PostgreSQL database.

    Uses a single table `hospedajes` with JSONB fields for
    nested structures like availability and coordinates.
    """

    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

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
        """Busca hospedajes utilizando SQL y jsonb."""
        query_lines = [
            "SELECT * FROM search.hospedajes h WHERE h.ciudad = $1 AND h.pais = $2"
        ]
        params: List[Any] = [ciudad, pais]

        param_idx = 3
        if estado_provincia:
            query_lines.append(f"AND h.estado_provincia = ${param_idx}")
            params.append(estado_provincia)
            param_idx += 1

        required_dates = []
        current = fecha_inicio
        while current <= fecha_fin:
            required_dates.append(current)
            current += timedelta(days=1)

        query_lines.append(f"""
            AND NOT EXISTS (
                SELECT 1
                FROM unnest(${param_idx}::date[]) AS required_date
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM jsonb_array_elements(h.disponibilidad) AS d(val)
                    WHERE (d.val->>'fecha')::date = required_date
                      AND (d.val->>'cupos')::int >= ${param_idx + 1}
                )
            )
        """)
        params.extend([required_dates, huespedes])

        order_by_clause = strategy.build_sql_sort()
        if order_by_clause:
            query_lines.append(f"ORDER BY {order_by_clause}")
            
        query_lines.append("LIMIT 50")

        query = " ".join(query_lines)

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query, *params)

        return [self._row_to_entity(row) for row in rows]

    @staticmethod
    def _row_to_entity(row: asyncpg.Record) -> Hospedaje:
        
        # Parse JSON fields if they are strings (asyncpg might return string for jsonb if json encoder is not set up, or dict if set up. We handle both)
        coordenadas_raw = row["coordenadas"]
        if coordenadas_raw is None:
            coordenadas_raw = {}
        elif isinstance(coordenadas_raw, str):
            coordenadas_raw = json.loads(coordenadas_raw)
            
        disponibilidad_raw = row["disponibilidad"]
        if disponibilidad_raw is None:
            disponibilidad_raw = []
        elif isinstance(disponibilidad_raw, str):
            disponibilidad_raw = json.loads(disponibilidad_raw)

        amenidades_raw = row["amenidades_destacadas"]
        if amenidades_raw is None:
            amenidades_raw = []
        elif isinstance(amenidades_raw, str):
            amenidades_raw = json.loads(amenidades_raw)

        return Hospedaje(
            id_propiedad=row["id_propiedad"],
            id_categoria=row["id_categoria"],
            propiedad_nombre=row["propiedad_nombre"],
            categoria_nombre=row["categoria_nombre"],
            imagen_principal_url=row["imagen_principal_url"],
            amenidades_destacadas=amenidades_raw,
            estrellas=row.get("estrellas", 0),
            rating_promedio=float(row.get("rating_promedio", 0.0)),
            ciudad=row["ciudad"],
            estado_provincia=row.get("estado_provincia", ""),
            pais=row["pais"],
            coordenadas=Coordenadas(
                lat=float(coordenadas_raw.get("lat", 0.0)),
                lon=float(coordenadas_raw.get("lon", 0.0)),
            ),
            capacidad_pax=row.get("capacidad_pax", 1),
            precio_base=Decimal(str(row["precio_base"])),
            moneda=row.get("moneda", "COP"),
            es_reembolsable=row.get("es_reembolsable", False),
            disponibilidad=[
                Disponibilidad(
                    fecha=date.fromisoformat(d["fecha"]) if isinstance(d["fecha"], str) else d["fecha"],
                    cupos=int(d["cupos"]),
                )
                for d in disponibilidad_raw
            ],
        )
