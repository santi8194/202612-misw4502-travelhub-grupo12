"""SQLite adapter implementing the HospedajeRepository port."""

from __future__ import annotations

import asyncio
import json
import sqlite3
from datetime import date, timedelta
from decimal import Decimal
from typing import List
from uuid import UUID

from app.application.ports import HospedajeRepository
from app.domain.entities import Coordenadas, Disponibilidad, Hospedaje
from app.domain.strategies import RankingStrategy


class SQLiteHospedajeRepository(HospedajeRepository):
    """Repository backed by a local SQLite database for docker-compose runs."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

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
        rows = await asyncio.to_thread(
            self._fetch_rows_sync,
            ciudad,
            estado_provincia,
            pais,
        )
        hospedajes = [self._row_to_entity(row) for row in rows]
        filtered = [
            hospedaje
            for hospedaje in hospedajes
            if self._has_required_availability(
                hospedaje=hospedaje,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                huespedes=huespedes,
            )
        ]

        if strategy.build_sql_sort().strip().lower() == "precio_base asc":
            filtered.sort(key=lambda hospedaje: hospedaje.precio_base)

        return filtered[:50]

    def _fetch_rows_sync(
        self,
        ciudad: str,
        estado_provincia: str,
        pais: str,
    ) -> list[sqlite3.Row]:
        connection = sqlite3.connect(self._db_path)
        connection.row_factory = sqlite3.Row
        try:
            if estado_provincia:
                return connection.execute(
                    """
                    SELECT *
                    FROM hospedajes
                    WHERE ciudad = ? AND pais = ? AND estado_provincia = ?
                    """,
                    (ciudad, pais, estado_provincia),
                ).fetchall()

            return connection.execute(
                """
                SELECT *
                FROM hospedajes
                WHERE ciudad = ? AND pais = ?
                """,
                (ciudad, pais),
            ).fetchall()
        finally:
            connection.close()

    @staticmethod
    def _has_required_availability(
        hospedaje: Hospedaje,
        fecha_inicio: date,
        fecha_fin: date,
        huespedes: int,
    ) -> bool:
        availability_by_date = {
            disponibilidad.fecha: disponibilidad.cupos
            for disponibilidad in hospedaje.disponibilidad
        }

        current = fecha_inicio
        while current <= fecha_fin:
            if availability_by_date.get(current, 0) < huespedes:
                return False
            current += timedelta(days=1)
        return True

    @staticmethod
    def _row_to_entity(row: sqlite3.Row) -> Hospedaje:
        coordenadas_raw = json.loads(row["coordenadas"])
        disponibilidad_raw = json.loads(row["disponibilidad"])
        amenidades_raw = json.loads(row["amenidades_destacadas"])

        return Hospedaje(
            id_propiedad=UUID(row["id_propiedad"]),
            id_categoria=UUID(row["id_categoria"]),
            propiedad_nombre=row["propiedad_nombre"],
            categoria_nombre=row["categoria_nombre"],
            imagen_principal_url=row["imagen_principal_url"],
            amenidades_destacadas=amenidades_raw,
            estrellas=int(row["estrellas"]),
            rating_promedio=float(row["rating_promedio"]),
            ciudad=row["ciudad"],
            estado_provincia=row["estado_provincia"] or "",
            pais=row["pais"],
            coordenadas=Coordenadas(
                lat=float(coordenadas_raw.get("lat", 0.0)),
                lon=float(coordenadas_raw.get("lon", 0.0)),
            ),
            capacidad_pax=int(row["capacidad_pax"]),
            precio_base=Decimal(str(row["precio_base"])),
            moneda=row["moneda"],
            es_reembolsable=bool(row["es_reembolsable"]),
            disponibilidad=[
                Disponibilidad(
                    fecha=date.fromisoformat(disponibilidad["fecha"]),
                    cupos=int(disponibilidad["cupos"]),
                )
                for disponibilidad in disponibilidad_raw
            ],
        )
