"""Tests para el Mock PMS — simulador de sistema externo."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health():
    """GET /health retorna estado ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "mock-pms"}


def test_get_inventory_changes_sin_filtro():
    """Sin since devuelve todos los registros."""
    response = client.get("/api/inventory/changes")
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "mock-pms"
    assert "changes" in data
    assert isinstance(data["changes"], list)
    assert len(data["changes"]) > 0
    assert "queried_at" in data


def test_get_inventory_changes_con_since_futuro():
    """Con since muy futuro devuelve lista vacía."""
    response = client.get("/api/inventory/changes?since=2099-01-01T00:00:00Z")
    assert response.status_code == 200
    data = response.json()
    assert data["changes"] == []


def test_get_inventory_changes_con_since_pasado():
    """Con since en el pasado devuelve al menos un registro."""
    response = client.get("/api/inventory/changes?since=2000-01-01T00:00:00Z")
    assert response.status_code == 200
    data = response.json()
    assert len(data["changes"]) > 0


def test_get_inventory_changes_since_invalido():
    """Since con formato inválido retorna 400."""
    response = client.get("/api/inventory/changes?since=not-a-date")
    assert response.status_code == 400


def test_force_webhook_hotel_no_encontrado():
    """Hotel code inexistente retorna 404."""
    response = client.post("/force-webhook?hotel_code=HOTEL-INEXISTENTE&cupos=0")
    assert response.status_code == 404


def test_force_webhook_exitoso():
    """Webhook disparado correctamente retorna 200 con estado webhook_dispatched."""
    mock_response = MagicMock()
    mock_response.status_code = 200

    mock_client_instance = AsyncMock()
    mock_client_instance.post = AsyncMock(return_value=mock_response)

    mock_async_client = MagicMock()
    mock_async_client.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_async_client.__aexit__ = AsyncMock(return_value=None)

    with patch("main.httpx.AsyncClient", return_value=mock_async_client):
        response = client.post("/force-webhook?hotel_code=COL-APAR-001&cupos=3")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "webhook_dispatched"
    assert body["pms_integration_response"] == 200


def test_force_webhook_connect_error():
    """Error de conexión con pms-integration retorna 503."""
    mock_client_instance = AsyncMock()
    mock_client_instance.post = AsyncMock(
        side_effect=httpx.ConnectError("Connection refused")
    )

    mock_async_client = MagicMock()
    mock_async_client.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_async_client.__aexit__ = AsyncMock(return_value=None)

    with patch("main.httpx.AsyncClient", return_value=mock_async_client):
        response = client.post("/force-webhook?hotel_code=COL-APAR-001&cupos=0")

    assert response.status_code == 503
    assert "pms-integration" in response.json()["detail"]
