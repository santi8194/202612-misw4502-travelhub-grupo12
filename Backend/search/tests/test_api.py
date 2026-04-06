"""Pruebas de integración para el endpoint de búsqueda de FastAPI."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.application.use_cases import BuscarHospedaje
from app.domain.entities import Coordenadas, Disponibilidad, Hospedaje
from app.domain.strategies import PriceFirstStrategy
from app.main import app
from app.dependencies import get_use_case


# ── Fixtures ─────────────────────────────────────────────────────────────────



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
    def test_search_valid_request(self, sample_hospedaje):
        use_case = _mock_use_case([sample_hospedaje])
        app.dependency_overrides[get_use_case] = lambda: use_case

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get(
            "/api/v1/search",
            params={
                "ciudad": "Cartagena",
                "pais": "Colombia",
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
                "ciudad": "Inexistente",
                "pais": "PaisX",
                "fecha_inicio": "2026-03-15",
                "fecha_fin": "2026-03-17",
                "huespedes": 1,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["resultados"] == []

    def test_search_missing_ciudad(self):
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
                "ciudad": "Cartagena",
                "pais": "Colombia",
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
                "ciudad": "Cartagena",
                "pais": "Colombia",
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
                "ciudad": "Cartagena",
                "pais": "Colombia",
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
                "ciudad": "Cartagena",
                "pais": "Colombia",
                "fecha_inicio": "2026-01-01",
                "fecha_fin": "2026-03-01",
                "huespedes": 1,
            },
        )
        assert response.status_code == 422

    def test_response_contains_coordenadas(self, sample_hospedaje):
        use_case = _mock_use_case([sample_hospedaje])
        app.dependency_overrides[get_use_case] = lambda: use_case

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get(
            "/api/v1/search",
            params={
                "ciudad": "Cartagena",
                "pais": "Colombia",
                "fecha_inicio": "2026-03-15",
                "fecha_fin": "2026-03-17",
                "huespedes": 2,
            },
        )

        assert response.status_code == 200
        coords = response.json()["resultados"][0]["coordenadas"]
        assert coords["lat"] == 10.39
        assert coords["lon"] == -75.53
