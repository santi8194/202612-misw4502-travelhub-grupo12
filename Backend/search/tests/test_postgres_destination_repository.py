"""Pruebas unitarias para el repositorio de destinos en PostgreSQL.

Se prueba la lógica del adaptador sin necesidad de una base de datos real,
usando mocks de asyncpg.Pool y asyncpg.Connection.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.infrastructure.postgres_destination_repository import PostgresDestinationRepository


# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_pool_mock(fetch_return: list[dict]) -> MagicMock:
    """Crea un mock de asyncpg.Pool con conn.fetch() configurado.

    Simula el context manager ``async with pool.acquire() as conn``.
    """
    # Mock de la conexión con el método fetch configurado
    conn_mock = AsyncMock()
    conn_mock.fetch = AsyncMock(return_value=fetch_return)

    # Mock del context manager que retorna la conexión
    acquire_cm = MagicMock()
    acquire_cm.__aenter__ = AsyncMock(return_value=conn_mock)
    acquire_cm.__aexit__ = AsyncMock(return_value=False)

    # Mock del pool que retorna el context manager al llamar acquire()
    pool_mock = MagicMock()
    pool_mock.acquire = MagicMock(return_value=acquire_cm)

    return pool_mock, conn_mock


# ── Tests ─────────────────────────────────────────────────────────────────────


class TestPostgresDestinationRepository:
    """Verifica el comportamiento del repositorio de destinos sobre PostgreSQL."""

    @pytest.mark.asyncio
    async def test_autocomplete_retorna_resultados(self):
        """Debe retornar una lista de diccionarios con ciudad, estado_provincia y pais."""
        # Filas simuladas tal como las retornaría asyncpg
        filas_simuladas = [
            {"ciudad": "Cartagena", "estado_provincia": "Bolívar", "pais": "Colombia"},
            {"ciudad": "Cali", "estado_provincia": "Valle del Cauca", "pais": "Colombia"},
        ]
        pool_mock, _ = _make_pool_mock(filas_simuladas)
        repo = PostgresDestinationRepository(pool=pool_mock)

        resultados = await repo.autocomplete("car")

        assert len(resultados) == 2
        assert resultados[0]["ciudad"] == "Cartagena"
        assert resultados[0]["estado_provincia"] == "Bolívar"
        assert resultados[0]["pais"] == "Colombia"
        assert resultados[1]["ciudad"] == "Cali"

    @pytest.mark.asyncio
    async def test_autocomplete_sin_resultados(self):
        """Debe retornar lista vacía cuando no hay coincidencias en la base de datos."""
        pool_mock, _ = _make_pool_mock([])
        repo = PostgresDestinationRepository(pool=pool_mock)

        resultados = await repo.autocomplete("xyz")

        assert resultados == []

    @pytest.mark.asyncio
    async def test_autocomplete_convierte_prefix_a_minusculas(self):
        """El prefijo debe convertirse a minúsculas antes de ejecutar la consulta SQL."""
        pool_mock, conn_mock = _make_pool_mock([])
        repo = PostgresDestinationRepository(pool=pool_mock)

        await repo.autocomplete("CAR")

        # Verificar que se llamó con el prefijo en minúsculas
        conn_mock.fetch.assert_called_once()
        args = conn_mock.fetch.call_args
        # El segundo argumento posicional es el parámetro $1 (prefix_lower)
        assert args[0][1] == "car"

    @pytest.mark.asyncio
    async def test_autocomplete_limita_a_10_resultados(self):
        """La consulta SQL debe incluir LIMIT 10 para no retornar resultados excesivos."""
        pool_mock, conn_mock = _make_pool_mock([])
        repo = PostgresDestinationRepository(pool=pool_mock)

        await repo.autocomplete("bog")

        # Verificar que la query enviada contiene LIMIT 10
        args = conn_mock.fetch.call_args
        query_enviada: str = args[0][0]
        assert "LIMIT 10" in query_enviada

    @pytest.mark.asyncio
    async def test_autocomplete_retorna_solo_campos_esperados(self):
        """El diccionario retornado debe contener exactamente ciudad, estado_provincia y pais."""
        filas_simuladas = [
            {"ciudad": "Medellín", "estado_provincia": "Antioquia", "pais": "Colombia"},
        ]
        pool_mock, _ = _make_pool_mock(filas_simuladas)
        repo = PostgresDestinationRepository(pool=pool_mock)

        resultados = await repo.autocomplete("med")

        assert len(resultados) == 1
        assert set(resultados[0].keys()) == {"ciudad", "estado_provincia", "pais"}
