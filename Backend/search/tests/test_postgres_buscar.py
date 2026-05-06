"""Pruebas unitarias para el método buscar de PostgresHospedajeRepository.

Se mockea asyncpg.Pool para probar la construcción de la query y el mapeo de
resultados sin necesidad de una base de datos real.
"""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from typing import Any, List
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest

from app.domain.entities import Coordenadas, Disponibilidad, Hospedaje
from app.domain.strategies import PriceFirstStrategy
from app.infrastructure.postgres_repository import PostgresHospedajeRepository


# ── Helpers ────────────────────────────────────────────────────────────────────


class FakeRecord(dict):
    """Mock de asyncpg.Record que permite acceso por clave y .get()."""

    def get(self, key: str, default: Any = None) -> Any:
        return dict.get(self, key, default)


def _make_fake_record(**overrides: Any) -> FakeRecord:
    """Construye un registro simulado de asyncpg.Record."""
    id_propiedad = uuid4()
    id_categoria = uuid4()
    base = {
        "id_propiedad": id_propiedad,
        "id_categoria": id_categoria,
        "propiedad_nombre": "Hotel Test",
        "categoria_nombre": "Hotel",
        "imagen_principal_url": "https://cdn.example.com/img.jpg",
        "amenidades_destacadas": json.dumps(["WiFi", "Piscina"]),
        "estrellas": 4,
        "rating_promedio": Decimal("4.5"),
        "ciudad": "Cartagena",
        "estado_provincia": "Bolívar",
        "pais": "Colombia",
        "coordenadas": json.dumps({"lat": 10.39, "lon": -75.53}),
        "capacidad_pax": 4,
        "precio_base": Decimal("350000"),
        "moneda": "COP",
        "es_reembolsable": True,
        "disponibilidad": json.dumps([
            {"fecha": "2026-03-15", "cupos": 5},
            {"fecha": "2026-03-16", "cupos": 3},
        ]),
    }
    base.update(overrides)
    return FakeRecord(base)


def _fake_pool(*rows: FakeRecord):
    """Construye un mock de asyncpg.Pool que retorna las filas dadas."""
    from unittest.mock import MagicMock
    pool = MagicMock()
    conn = MagicMock()
    # fetch es async
    conn.fetch = AsyncMock(return_value=list(rows))
    # conn debe soportar async with: __aenter__ retorna conn, __aexit__ retorna False
    conn.__aenter__ = AsyncMock(return_value=conn)
    conn.__aexit__ = AsyncMock(return_value=False)
    # pool.acquire() retorna conn (no una coroutine)
    pool.acquire = MagicMock(return_value=conn)
    return pool


# ── Clase de tests: buscar ─────────────────────────────────────────────────────


class TestBuscar:
    """Verifica buscar() del PostgresHospedajeRepository."""

    @pytest.mark.asyncio
    async def test_buscar_retorna_hospedajes(self):
        """Cuando hay filas coincidentes, retorna entidades Hospedaje."""
        pool = _fake_pool(_make_fake_record())
        repo = PostgresHospedajeRepository(pool=pool)
        strategy = PriceFirstStrategy()

        resultados = await repo.buscar(
            ciudad="Cartagena",
            estado_provincia="",
            pais="Colombia",
            fecha_inicio=date(2026, 3, 15),
            fecha_fin=date(2026, 3, 15),
            huespedes=2,
            strategy=strategy,
        )

        assert len(resultados) == 1
        assert isinstance(resultados[0], Hospedaje)
        assert resultados[0].propiedad_nombre == "Hotel Test"

    @pytest.mark.asyncio
    async def test_buscar_retorna_vacio(self):
        """Cuando no hay filas coincidentes, retorna lista vacía."""
        pool = _fake_pool()
        repo = PostgresHospedajeRepository(pool=pool)
        strategy = PriceFirstStrategy()

        resultados = await repo.buscar(
            ciudad="Inexistente",
            estado_provincia="",
            pais="PaisX",
            fecha_inicio=date(2026, 3, 15),
            fecha_fin=date(2026, 3, 15),
            huespedes=1,
            strategy=strategy,
        )

        assert resultados == []

    @pytest.mark.asyncio
    async def test_buscar_pasa_estado_provincia(self):
        """Si se proporciona estado_provincia, debe filtrar por ese campo."""
        pool = _fake_pool(_make_fake_record())
        repo = PostgresHospedajeRepository(pool=pool)
        strategy = PriceFirstStrategy()

        await repo.buscar(
            ciudad="Cartagena",
            estado_provincia="Bolívar",
            pais="Colombia",
            fecha_inicio=date(2026, 3, 15),
            fecha_fin=date(2026, 3, 15),
            huespedes=1,
            strategy=strategy,
        )

        conn = pool.acquire.return_value.__aenter__.return_value
        query = conn.fetch.call_args[0][0]
        assert "estado_provincia" in query

    @pytest.mark.asyncio
    async def test_buscar_incluye_limit_50(self):
        """La query debe incluir LIMIT 50."""
        pool = _fake_pool(_make_fake_record())
        repo = PostgresHospedajeRepository(pool=pool)
        strategy = PriceFirstStrategy()

        await repo.buscar(
            ciudad="Cartagena",
            estado_provincia="",
            pais="Colombia",
            fecha_inicio=date(2026, 3, 15),
            fecha_fin=date(2026, 3, 15),
            huespedes=1,
            strategy=strategy,
        )

        conn = pool.acquire.return_value.__aenter__.return_value
        query = conn.fetch.call_args[0][0]
        assert "LIMIT 50" in query

    @pytest.mark.asyncio
    async def test_buscar_incluye_order_by(self):
        """La query debe incluir ORDER BY cuando la estrategia lo requiere."""
        pool = _fake_pool(_make_fake_record())
        repo = PostgresHospedajeRepository(pool=pool)
        strategy = PriceFirstStrategy()

        await repo.buscar(
            ciudad="Cartagena",
            estado_provincia="",
            pais="Colombia",
            fecha_inicio=date(2026, 3, 15),
            fecha_fin=date(2026, 3, 15),
            huespedes=1,
            strategy=strategy,
        )

        conn = pool.acquire.return_value.__aenter__.return_value
        query = conn.fetch.call_args[0][0]
        assert "ORDER BY" in query
        assert "precio_base ASC" in query

    @pytest.mark.asyncio
    async def test_buscar_multiple_results(self):
        """Debe retornar múltiples entidades si hay múltiples filas."""
        pool = _fake_pool(
            _make_fake_record(propiedad_nombre="Hotel A"),
            _make_fake_record(propiedad_nombre="Hotel B"),
        )
        repo = PostgresHospedajeRepository(pool=pool)
        strategy = PriceFirstStrategy()

        resultados = await repo.buscar(
            ciudad="Cartagena",
            estado_provincia="",
            pais="Colombia",
            fecha_inicio=date(2026, 3, 15),
            fecha_fin=date(2026, 3, 15),
            huespedes=1,
            strategy=strategy,
        )

        assert len(resultados) == 2
        nombres = [r.propiedad_nombre for r in resultados]
        assert "Hotel A" in nombres
        assert "Hotel B" in nombres
