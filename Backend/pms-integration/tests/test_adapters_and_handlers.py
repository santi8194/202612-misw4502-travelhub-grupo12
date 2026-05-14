"""Tests para adaptadores PMS y handlers de infraestructura."""

import pytest
from unittest.mock import MagicMock, patch
from datetime import date

from modules.pms.application.adapters.mock_pms_adapter import MockPMSAdapter
from modules.pms.application.adapters.adapter_registry import get_adapter
from modules.pms.infrastructure.services.handlers import (
    handle_confirm_reservation,
    handle_cancel_reservation,
)

_HANDLERS_MODULE = "modules.pms.infrastructure.services.handlers"


@pytest.fixture
def adapter():
    """Instancia de MockPMSAdapter (no requiere archivos externos)."""
    return MockPMSAdapter()


# ─── MockPMSAdapter.normalize_webhook ───

def test_normalize_webhook_exitoso(adapter):
    """Normaliza correctamente un payload válido y genera el codigo_mapeo_pms compuesto."""
    payload = {
        "hotel_code": "COL-TEST-001",
        "room_type_code": "RM001",
        "date": "2026-06-01",
        "total_units": 10,
        "available_units": 7,
        "last_modified": "2026-06-01T10:00:00Z",
    }
    dto = adapter.normalize_webhook(payload)
    assert dto.codigo_mapeo_pms == "COL-TEST-001:RM001"
    assert dto.cupos_disponibles == 7
    assert dto.cupos_totales == 10
    assert dto.fecha == date(2026, 6, 1)


def test_normalize_webhook_codigo_compuesto_formato(adapter):
    """El codigo_mapeo_pms tiene el formato hotel_code:room_type_code."""
    payload = {
        "hotel_code": "MEX-RESO-099",
        "room_type_code": "RM099",
        "date": "2026-07-15",
        "total_units": 5,
        "available_units": 3,
        "last_modified": "2026-07-15T08:00:00Z",
    }
    dto = adapter.normalize_webhook(payload)
    partes = dto.codigo_mapeo_pms.split(":")
    assert len(partes) == 2
    assert partes[0] == "MEX-RESO-099"
    assert partes[1] == "RM099"


def test_normalize_webhook_campo_faltante(adapter):
    """Lanza ValueError cuando falta un campo requerido en el webhook."""
    with pytest.raises(ValueError):
        adapter.normalize_webhook({"hotel_code": "COL-TEST-001"})


def test_normalize_webhook_campo_date_faltante(adapter):
    """Lanza ValueError cuando falta el campo date."""
    with pytest.raises(ValueError):
        adapter.normalize_webhook({
            "hotel_code": "COL-TEST-001",
            "room_type_code": "RM001",
            "total_units": 5,
            "available_units": 3,
            "last_modified": "2026-06-01T10:00:00Z",
        })


# ─── MockPMSAdapter.normalize_poll_response ───

def test_normalize_poll_response_exitoso(adapter):
    """Normaliza correctamente una respuesta de polling con múltiples cambios."""
    response = {
        "provider": "mock-pms",
        "changes": [
            {
                "hotel_code": "COL-TEST-001",
                "room_type_code": "RM001",
                "date": "2026-06-01",
                "total_units": 10,
                "available_units": 5,
                "last_modified": "2026-06-01T10:00:00Z",
            },
            {
                "hotel_code": "COL-TEST-002",
                "room_type_code": "RM002",
                "date": "2026-06-02",
                "total_units": 8,
                "available_units": 2,
                "last_modified": "2026-06-02T10:00:00Z",
            },
        ],
    }
    dtos = adapter.normalize_poll_response(response)
    assert len(dtos) == 2
    assert dtos[0].codigo_mapeo_pms == "COL-TEST-001:RM001"
    assert dtos[1].codigo_mapeo_pms == "COL-TEST-002:RM002"
    assert dtos[0].cupos_disponibles == 5


def test_normalize_poll_response_lista_vacia(adapter):
    """Retorna lista vacía cuando no hay cambios."""
    dtos = adapter.normalize_poll_response({"changes": []})
    assert dtos == []


def test_normalize_poll_response_sin_clave_changes(adapter):
    """Retorna lista vacía cuando la clave changes no está presente."""
    dtos = adapter.normalize_poll_response({"provider": "mock-pms"})
    assert dtos == []


# ─── adapter_registry.get_adapter ───

def test_get_adapter_mock():
    """get_adapter('mock') retorna un MockPMSAdapter."""
    adapter = get_adapter("mock")
    assert isinstance(adapter, MockPMSAdapter)


def test_get_adapter_proveedor_no_soportado():
    """Lanza ValueError cuando el proveedor no está registrado."""
    with pytest.raises(ValueError, match="no soportado"):
        get_adapter("opera")


# ─── handlers: handle_confirm_reservation ───

def test_handle_confirm_reservation_delega_use_case():
    """handle_confirm_reservation invoca ConfirmReservation.execute con los datos correctos."""
    mock_repo = MagicMock()
    mock_bus = MagicMock()
    mock_uc = MagicMock()
    mock_uc.execute.return_value = {"id_reserva": "res-1", "state": "CONFIRMED"}

    with patch(f"{_HANDLERS_MODULE}.ReservationRepository", return_value=mock_repo), \
         patch(f"{_HANDLERS_MODULE}.EventBus", return_value=mock_bus), \
         patch(f"{_HANDLERS_MODULE}.ConfirmReservation", return_value=mock_uc):

        handle_confirm_reservation({
            "id_reserva": "res-1",
            "id_habitacion": "room-1",
            "fecha_reserva": "2026-06-01",
        })

    mock_uc.execute.assert_called_once_with("res-1", "room-1", "2026-06-01")


def test_handle_confirm_reservation_sin_fecha_reserva():
    """handle_confirm_reservation funciona aunque fecha_reserva sea None."""
    mock_repo = MagicMock()
    mock_bus = MagicMock()
    mock_uc = MagicMock()
    mock_uc.execute.return_value = {"state": "CONFIRMED"}

    with patch(f"{_HANDLERS_MODULE}.ReservationRepository", return_value=mock_repo), \
         patch(f"{_HANDLERS_MODULE}.EventBus", return_value=mock_bus), \
         patch(f"{_HANDLERS_MODULE}.ConfirmReservation", return_value=mock_uc):

        handle_confirm_reservation({"id_reserva": "res-2", "id_habitacion": "room-2"})

    mock_uc.execute.assert_called_once_with("res-2", "room-2", None)


# ─── handlers: handle_cancel_reservation ───

def test_handle_cancel_reservation_delega_use_case():
    """handle_cancel_reservation invoca CancelReservation.execute con el id correcto."""
    mock_repo = MagicMock()
    mock_bus = MagicMock()
    mock_uc = MagicMock()
    mock_uc.execute.return_value = {"id_reserva": "res-3", "state": "CANCELLED"}

    with patch(f"{_HANDLERS_MODULE}.ReservationRepository", return_value=mock_repo), \
         patch(f"{_HANDLERS_MODULE}.EventBus", return_value=mock_bus), \
         patch(f"{_HANDLERS_MODULE}.CancelReservation", return_value=mock_uc):

        handle_cancel_reservation({"id_reserva": "res-3"})

    mock_uc.execute.assert_called_once_with("res-3")
