"""Pruebas unitarias para el caso de uso BuscarHospedaje."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.dtos import SearchRequest, SearchResponse
from app.application.use_cases import BuscarHospedaje
from app.domain.entities import Coordenadas, Disponibilidad, Hospedaje
from app.domain.strategies import PriceFirstStrategy


# ── Fixtures ─────────────────────────────────────────────────────────────────


def _hospedaje_named(nombre: str) -> Hospedaje:
    """Create a Hospedaje with a custom propiedad_nombre for multi-result tests."""
    return Hospedaje(
        id_propiedad=uuid4(),
        id_categoria=uuid4(),
        propiedad_nombre=nombre,
        categoria_nombre="Hotel",
        imagen_principal_url="https://cdn.example.com/img.jpg",
        amenidades_destacadas=["WiFi"],
        estrellas=4,
        rating_promedio=4.5,
        ciudad="Cartagena",
        estado_provincia="Bolívar",
        pais="Colombia",
        coordenadas=Coordenadas(lat=10.39, lon=-75.53),
        capacidad_pax=4,
        precio_base=Decimal("350000"),
        moneda="COP",
        es_reembolsable=True,
        disponibilidad=[Disponibilidad(fecha=date(2026, 3, 15), cupos=5)],
    )


# ── Tests ────────────────────────────────────────────────────────────────────


class TestBuscarHospedaje:
    @pytest.mark.asyncio
    async def test_ejecutar_returns_results(self, sample_hospedaje, sample_search_request):
        repo = AsyncMock()
        repo.buscar.return_value = [sample_hospedaje]
        strategy = PriceFirstStrategy()

        use_case = BuscarHospedaje(repository=repo, strategy=strategy)

        result = await use_case.ejecutar(sample_search_request)

        assert isinstance(result, SearchResponse)
        assert result.total == 1
        assert result.resultados[0].propiedad_nombre == "Hotel Test"
        assert result.resultados[0].ciudad == "Cartagena"

    @pytest.mark.asyncio
    async def test_ejecutar_empty_results(self, sample_search_request):
        repo = AsyncMock()
        repo.buscar.return_value = []
        strategy = PriceFirstStrategy()

        use_case = BuscarHospedaje(repository=repo, strategy=strategy)

        result = await use_case.ejecutar(sample_search_request)

        assert result.total == 0
        assert result.resultados == []

    @pytest.mark.asyncio
    async def test_strategy_passed_to_repository(self, sample_search_request):
        repo = AsyncMock()
        repo.buscar.return_value = []
        strategy = PriceFirstStrategy()

        use_case = BuscarHospedaje(repository=repo, strategy=strategy)

        await use_case.ejecutar(sample_search_request)

        repo.buscar.assert_called_once_with(
            ciudad="Cartagena",
            estado_provincia="Bolívar",
            pais="Colombia",
            fecha_inicio=date(2026, 3, 15),
            fecha_fin=date(2026, 3, 17),
            huespedes=2,
            strategy=strategy,
        )

    @pytest.mark.asyncio
    async def test_response_excludes_disponibilidad(self, sample_hospedaje, sample_search_request):
        repo = AsyncMock()
        repo.buscar.return_value = [sample_hospedaje]
        strategy = PriceFirstStrategy()

        use_case = BuscarHospedaje(repository=repo, strategy=strategy)

        result = await use_case.ejecutar(sample_search_request)

        response_dict = result.resultados[0].model_dump()
        assert "disponibilidad" not in response_dict

    @pytest.mark.asyncio
    async def test_multiple_results(self, sample_search_request):
        hospedajes = [
            _hospedaje_named("Hotel A"),
            _hospedaje_named("Hotel B"),
            _hospedaje_named("Hotel C"),
        ]
        repo = AsyncMock()
        repo.buscar.return_value = hospedajes
        strategy = PriceFirstStrategy()

        use_case = BuscarHospedaje(repository=repo, strategy=strategy)

        result = await use_case.ejecutar(sample_search_request)

        assert result.total == 3
        names = [r.propiedad_nombre for r in result.resultados]
        assert names == ["Hotel A", "Hotel B", "Hotel C"]

    @pytest.mark.asyncio
    async def test_coordenadas_mapped_correctly(self, sample_hospedaje, sample_search_request):
        repo = AsyncMock()
        repo.buscar.return_value = [sample_hospedaje]
        strategy = PriceFirstStrategy()

        use_case = BuscarHospedaje(repository=repo, strategy=strategy)

        result = await use_case.ejecutar(sample_search_request)

        coords = result.resultados[0].coordenadas
        assert coords.lat == 10.39
        assert coords.lon == -75.53


class TestSearchRequest:
    def test_valid_request(self, sample_search_request):
        assert sample_search_request.ciudad == "Cartagena"

    def test_fecha_fin_before_fecha_inicio_raises(self):
        with pytest.raises(ValueError, match="fecha_fin must be >= fecha_inicio"):
            SearchRequest(
                ciudad="Bogotá",
                pais="Colombia",
                estado_provincia="",
                fecha_inicio=date(2026, 3, 20),
                fecha_fin=date(2026, 3, 15),
                huespedes=1,
            )

    def test_range_exceeds_max_days_raises(self):
        with pytest.raises(ValueError, match="must not exceed 30 days"):
            SearchRequest(
                ciudad="Medellín",
                pais="Colombia",
                estado_provincia="",
                fecha_inicio=date(2026, 1, 1),
                fecha_fin=date(2026, 3, 1),
                huespedes=1,
            )

    def test_huespedes_zero_raises(self):
        with pytest.raises(ValueError):
            SearchRequest(
                ciudad="Cali",
                pais="Colombia",
                estado_provincia="",
                fecha_inicio=date(2026, 3, 15),
                fecha_fin=date(2026, 3, 16),
                huespedes=0,
            )

    def test_empty_ciudad_raises(self):
        with pytest.raises(ValueError):
            SearchRequest(
                ciudad="",
                pais="Colombia",
                estado_provincia="",
                fecha_inicio=date(2026, 3, 15),
                fecha_fin=date(2026, 3, 16),
                huespedes=2,
            )

    def test_same_day_is_valid(self):
        req = SearchRequest(
            ciudad="Cartagena",
            pais="Colombia",
            estado_provincia="",
            fecha_inicio=date(2026, 3, 15),
            fecha_fin=date(2026, 3, 15),
            huespedes=1,
        )
        assert req.fecha_inicio == req.fecha_fin

    def test_max_30_days_is_valid(self):
        req = SearchRequest(
            ciudad="Cartagena",
            pais="Colombia",
            estado_provincia="",
            fecha_inicio=date(2026, 3, 1),
            fecha_fin=date(2026, 3, 31),
            huespedes=1,
        )
        assert (req.fecha_fin - req.fecha_inicio).days == 30
