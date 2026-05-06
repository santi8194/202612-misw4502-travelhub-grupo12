"""Pruebas unitarias para el repositorio de destinos SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from app.config import Settings
from app.infrastructure.db_schema import ensure_local_sqlite_database
from app.infrastructure.sqlite_destination_repository import SQLiteDestinationRepository


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    """Crea una base SQLite con datos seed para probar el repositorio de destinos."""
    path = tmp_path / "dest_test.db"
    settings = Settings(sqlite_path=str(path))
    monkeypatch.setattr("app.infrastructure.db_schema.settings", settings)
    ensure_local_sqlite_database()
    return str(path)


class TestAutocomplete:
    """Verifica el autocompletado de destinos con SQLite."""

    @pytest.mark.asyncio
    async def test_retorna_destinos_coincidentes(self, db_path):
        """Un prefijo que coincida con una ciudad debe retornar los destinos correspondientes."""
        repo = SQLiteDestinationRepository(db_path=db_path)
        resultados = await repo.autocomplete("car")
        assert len(resultados) >= 1
        assert any(r["ciudad"].lower() == "cartagena" for r in resultados)

    @pytest.mark.asyncio
    async def test_retorna_vacio_sin_coincidencias(self, db_path):
        """Un prefijo sin coincidencias debe retornar lista vacía."""
        repo = SQLiteDestinationRepository(db_path=db_path)
        resultados = await repo.autocomplete("xyz")
        assert resultados == []

    @pytest.mark.asyncio
    async def test_es_case_insensitive(self, db_path):
        """La búsqueda debe ser insensible a mayúsculas/minúsculas."""
        repo = SQLiteDestinationRepository(db_path=db_path)
        resultados_upper = await repo.autocomplete("CAR")
        resultados_lower = await repo.autocomplete("car")
        assert resultados_upper == resultados_lower

    @pytest.mark.asyncio
    async def test_limita_a_10_resultados(self, db_path):
        """No debe retornar más de 10 resultados."""
        repo = SQLiteDestinationRepository(db_path=db_path)
        resultados = await repo.autocomplete("a")
        assert len(resultados) <= 10

    @pytest.mark.asyncio
    async def test_cada_resultado_tiene_estructura_correcta(self, db_path):
        """Cada resultado debe tener ciudad, estado_provincia y pais."""
        repo = SQLiteDestinationRepository(db_path=db_path)
        resultados = await repo.autocomplete("car")
        for r in resultados:
            assert "ciudad" in r
            assert "estado_provincia" in r
            assert "pais" in r

    @pytest.mark.asyncio
    async def test_prefijo_vacio_retorna_resultados(self, db_path):
        """Un prefijo vacío debe retornar todos los destinos (hasta el límite)."""
        repo = SQLiteDestinationRepository(db_path=db_path)
        resultados = await repo.autocomplete("")
        assert isinstance(resultados, list)
        assert len(resultados) <= 10
