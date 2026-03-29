"""Tests for the destination autocomplete endpoint."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.infrastructure.redis_destination_repository import RedisDestinationRepository
from app.main import app, get_destination_repo


# ── Helpers ──────────────────────────────────────────────────────────────────


def _mock_destination_repo(return_value: list[dict] | None = None):
    """Create a mock RedisDestinationRepository."""
    repo = AsyncMock(spec=RedisDestinationRepository)
    repo.autocomplete.return_value = return_value or []
    return repo


@pytest.fixture(autouse=True)
def _override_destination_repo():
    """Override the destination repo dependency for all tests."""
    repo = _mock_destination_repo([])
    app.dependency_overrides[get_destination_repo] = lambda: repo
    yield
    app.dependency_overrides.clear()


# ── Tests ────────────────────────────────────────────────────────────────────


class TestAutocompleteDestinations:
    def test_autocomplete_returns_results(self):
        mock_results = [
            {"ciudad": "Cartagena", "estado_provincia": "Bolívar", "pais": "Colombia"},
            {"ciudad": "Cali", "estado_provincia": "Valle del Cauca", "pais": "Colombia"},
        ]
        repo = _mock_destination_repo(mock_results)
        app.dependency_overrides[get_destination_repo] = lambda: repo

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/v1/search/destinations", params={"q": "car"})

        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2
        assert data["results"][0]["ciudad"] == "Cartagena"

    def test_autocomplete_empty_results(self):
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/v1/search/destinations", params={"q": "xyz"})

        assert response.status_code == 200
        data = response.json()
        assert data["results"] == []

    def test_autocomplete_q_too_short(self):
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/v1/search/destinations", params={"q": "ab"})

        assert response.status_code == 422

    def test_autocomplete_missing_q(self):
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/v1/search/destinations")

        assert response.status_code == 422

    def test_autocomplete_redis_unavailable(self):
        app.dependency_overrides[get_destination_repo] = lambda: (_ for _ in ()).throw(
            Exception("Redis not initialized")
        )
        # Override with None to trigger 503
        app.dependency_overrides.pop(get_destination_repo, None)

        # Temporarily set _dest_repository to None
        import app.main as main_module

        original = main_module._dest_repository
        main_module._dest_repository = None
        try:
            client = TestClient(app, raise_server_exceptions=False)
            response = client.get("/api/v1/search/destinations", params={"q": "car"})
            assert response.status_code == 503
        finally:
            main_module._dest_repository = original
