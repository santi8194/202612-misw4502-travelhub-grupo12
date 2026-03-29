"""Integration tests for the FastAPI search endpoint."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.application.use_cases import BuscarHospedaje
from app.domain.entities import Coordenadas, Disponibilidad, Hospedaje
from app.domain.strategies import PriceFirstStrategy
from app.main import app, get_use_case


# ── Fixtures ─────────────────────────────────────────────────────────────────


def _sample_hospedaje() -> Hospedaje:
    return Hospedaje(
        id_propiedad=uuid4(),
        id_categoria=uuid4(),
        propiedad_nombre="Hotel Test",
        categoria_nombre="Hotel",
        imagen_principal_url="https://cdn.example.com/img.jpg",
        amenidades_destacadas=["WiFi", "Pool"],
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
        disponibilidad=[
            Disponibilidad(fecha=date(2026, 3, 15), cupos=5),
        ],
    )


def _mock_use_case(return_value: list[Hospedaje] | None = None):
    """Create a BuscarHospedaje with a mocked repository."""
    repo = AsyncMock()
    repo.buscar.return_value = return_value or []
    return BuscarHospedaje(repository=repo, strategy=PriceFirstStrategy())


@pytest.fixture(autouse=True)
def _override_use_case():
    """Ensure the use case dependency is always overridden in tests."""
    use_case = _mock_use_case([])
    app.dependency_overrides[get_use_case] = lambda: use_case
    yield
    app.dependency_overrides.clear()


# ── Tests ────────────────────────────────────────────────────────────────────


class TestHealthEndpoint:
    def test_health_returns_ok(self):
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "search"


class TestSearchEndpoint:
    def test_search_valid_request(self):
        hospedaje = _sample_hospedaje()
        use_case = _mock_use_case([hospedaje])
        app.dependency_overrides[get_use_case] = lambda: use_case

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get(
            "/api/v1/search",
            params={
                "destino": "Cartagena",
                "fecha_inicio": "2026-03-15",
                "fecha_fin": "2026-03-17",
                "huespedes": 2,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["resultados"][0]["propiedad_nombre"] == "Hotel Test"
        assert data["resultados"][0]["ciudad"] == "Cartagena"

    def test_search_empty_results(self):
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get(
            "/api/v1/search",
            params={
                "destino": "Inexistente",
                "fecha_inicio": "2026-03-15",
                "fecha_fin": "2026-03-17",
                "huespedes": 1,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["resultados"] == []

    def test_search_missing_destino(self):
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get(
            "/api/v1/search",
            params={
                "fecha_inicio": "2026-03-15",
                "fecha_fin": "2026-03-17",
                "huespedes": 2,
            },
        )
        assert response.status_code == 422

    def test_search_missing_huespedes(self):
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get(
            "/api/v1/search",
            params={
                "destino": "Cartagena",
                "fecha_inicio": "2026-03-15",
                "fecha_fin": "2026-03-17",
            },
        )
        assert response.status_code == 422

    def test_search_invalid_date_range(self):
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get(
            "/api/v1/search",
            params={
                "destino": "Cartagena",
                "fecha_inicio": "2026-03-20",
                "fecha_fin": "2026-03-15",
                "huespedes": 2,
            },
        )
        assert response.status_code == 422

    def test_search_huespedes_zero(self):
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get(
            "/api/v1/search",
            params={
                "destino": "Cartagena",
                "fecha_inicio": "2026-03-15",
                "fecha_fin": "2026-03-17",
                "huespedes": 0,
            },
        )
        assert response.status_code == 422

    def test_search_range_exceeds_30_days(self):
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get(
            "/api/v1/search",
            params={
                "destino": "Cartagena",
                "fecha_inicio": "2026-01-01",
                "fecha_fin": "2026-03-01",
                "huespedes": 1,
            },
        )
        assert response.status_code == 422

    def test_response_contains_coordenadas(self):
        hospedaje = _sample_hospedaje()
        use_case = _mock_use_case([hospedaje])
        app.dependency_overrides[get_use_case] = lambda: use_case

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get(
            "/api/v1/search",
            params={
                "destino": "Cartagena",
                "fecha_inicio": "2026-03-15",
                "fecha_fin": "2026-03-17",
                "huespedes": 2,
            },
        )

        assert response.status_code == 200
        coords = response.json()["resultados"][0]["coordenadas"]
        assert coords["lat"] == 10.39
        assert coords["lon"] == -75.53
