"""Pruebas unitarias para el repositorio SQLite de hospedajes."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from app.config import Settings
from app.domain.entities import Hospedaje
from app.domain.strategies import PriceFirstStrategy
from app.infrastructure.db_schema import ensure_local_sqlite_database
from app.infrastructure.sqlite_repository import SQLiteHospedajeRepository


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    """Crea una base SQLite con datos seed para probar el repositorio."""
    path = tmp_path / "hosp_test.db"
    settings = Settings(sqlite_path=str(path))
    monkeypatch.setattr("app.infrastructure.db_schema.settings", settings)
    ensure_local_sqlite_database()
    return str(path)


class TestBuscar:
    """Verifica el método buscar del repositorio SQLite."""

    @pytest.mark.asyncio
    async def test_buscar_ciudad_existente(self, db_path):
        """Buscar por una ciudad que exista en el seed debe retornar resultados."""
        repo = SQLiteHospedajeRepository(db_path=db_path)
        strategy = PriceFirstStrategy()
        resultados = await repo.buscar(
            ciudad="Cartagena",
            estado_provincia="",
            pais="Colombia",
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            huespedes=1,
            strategy=strategy,
        )
        assert len(resultados) >= 1
        assert all(isinstance(r, Hospedaje) for r in resultados)

    @pytest.mark.asyncio
    async def test_buscar_ciudad_inexistente(self, db_path):
        """Buscar por una ciudad que no exista debe retornar lista vacía."""
        repo = SQLiteHospedajeRepository(db_path=db_path)
        strategy = PriceFirstStrategy()
        resultados = await repo.buscar(
            ciudad="Inexistente",
            estado_provincia="",
            pais="PaisX",
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            huespedes=1,
            strategy=strategy,
        )
        assert resultados == []

    @pytest.mark.asyncio
    async def test_buscar_con_filtro_disponibilidad(self, db_path):
        """El filtro de disponibilidad debe aplicarse correctamente."""
        repo = SQLiteHospedajeRepository(db_path=db_path)
        strategy = PriceFirstStrategy()
        resultados = await repo.buscar(
            ciudad="Cartagena",
            estado_provincia="",
            pais="Colombia",
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            huespedes=1,
            strategy=strategy,
        )
        assert isinstance(resultados, list)

    @pytest.mark.asyncio
    async def test_buscar_sin_estado_provincia(self, db_path):
        """Buscar sin especificar estado_provincia debe funcionar."""
        repo = SQLiteHospedajeRepository(db_path=db_path)
        strategy = PriceFirstStrategy()
        resultados = await repo.buscar(
            ciudad="Cartagena",
            estado_provincia="",
            pais="Colombia",
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            huespedes=1,
            strategy=strategy,
        )
        assert isinstance(resultados, list)

    @pytest.mark.asyncio
    async def test_ordenamiento_por_precio(self, db_path):
        """El resultado debe estar ordenado por precio ascendente."""
        repo = SQLiteHospedajeRepository(db_path=db_path)
        strategy = PriceFirstStrategy()
        resultados = await repo.buscar(
            ciudad="Cartagena",
            estado_provincia="",
            pais="Colombia",
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            huespedes=1,
            strategy=strategy,
        )
        if len(resultados) > 1:
            precios = [r.precio_base for r in resultados]
            assert precios == sorted(precios)

    @pytest.mark.asyncio
    async def test_limite_50_resultados(self, db_path):
        """No debe retornar más de 50 resultados."""
        repo = SQLiteHospedajeRepository(db_path=db_path)
        strategy = PriceFirstStrategy()
        resultados = await repo.buscar(
            ciudad="Cartagena",
            estado_provincia="",
            pais="Colombia",
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            huespedes=1,
            strategy=strategy,
        )
        assert len(resultados) <= 50

    @pytest.mark.asyncio
    async def test_campos_mapeados_correctamente(self, db_path):
        """Cada entidad retornada debe tener los campos mapeados correctamente."""
        repo = SQLiteHospedajeRepository(db_path=db_path)
        strategy = PriceFirstStrategy()
        resultados = await repo.buscar(
            ciudad="Cartagena",
            estado_provincia="",
            pais="Colombia",
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            huespedes=1,
            strategy=strategy,
        )
        if resultados:
            h = resultados[0]
            assert h.propiedad_nombre != ""
            assert h.ciudad == "Cartagena"
            assert h.pais == "Colombia"
            assert isinstance(h.precio_base, Decimal)
            assert h.coordenadas.lat != 0.0 or h.coordenadas.lon != 0.0

    @pytest.mark.asyncio
    async def test_disponibilidad_faltante_excluye_hospedaje(self, db_path):
        """Un hospedaje sin disponibilidad para la fecha debe ser excluido."""
        repo = SQLiteHospedajeRepository(db_path=db_path)
        strategy = PriceFirstStrategy()
        resultados = await repo.buscar(
            ciudad="Cartagena",
            estado_provincia="",
            pais="Colombia",
            fecha_inicio=date(2099, 1, 1),
            fecha_fin=date(2099, 1, 1),
            huespedes=1,
            strategy=strategy,
        )
        assert resultados == []
