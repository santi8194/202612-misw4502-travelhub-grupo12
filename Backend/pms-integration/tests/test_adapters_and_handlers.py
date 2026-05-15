"""Tests para adaptadores PMS y handlers de infraestructura."""

import json
import pytest
from unittest.mock import MagicMock, patch
from uuid import UUID

from modules.pms.application.adapters.mock_pms_adapter import MockPMSAdapter
from modules.pms.application.adapters.adapter_registry import get_adapter
from modules.pms.infrastructure.services.handlers import (
    handle_confirm_reservation,
    handle_cancel_reservation,
)

_FAKE_MAPPING = {
    "mappings": {
        "COL-TEST-001": {
            "property_uuid": "550e8400-e29b-41d4-a716-446655440000",
            "rooms": {
                "RM001": {
                    "category_uuid": "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
                }
            },
        }
    }
}

_HANDLERS_MODULE = "modules.pms.infrastructure.services.handlers"


@pytest.fixture
def mapping_file(tmp_path):
    """Crea un archivo de mapeo temporal para las pruebas."""
    f = tmp_path / "pms_uuid_mapping_full.json"
    f.write_text(json.dumps(_FAKE_MAPPING))
    return str(f)


@pytest.fixture
def adapter(mapping_file):
    """Instancia de MockPMSAdapter con mapeo temporal."""
    return MockPMSAdapter(mapping_file=mapping_file)


# ─── MockPMSAdapter._load_mapping ───

def test_load_mapping_archivo_no_encontrado(tmp_path):
    """Lanza ValueError cuando el archivo de mapeo no existe."""
    with pytest.raises(ValueError, match="no encontrado"):
        MockPMSAdapter(mapping_file=str(tmp_path / "inexistente.json"))


def test_load_mapping_json_invalido(tmp_path):
    """Lanza ValueError cuando el JSON es inválido."""
    f = tmp_path / "bad.json"
    f.write_text("not-valid-json{{")
    with pytest.raises(ValueError, match="parsear"):
        MockPMSAdapter(mapping_file=str(f))


# ─── MockPMSAdapter._get_uuids ───

def test_get_uuids_hotel_no_encontrado(adapter):
    """Lanza ValueError cuando el hotel_code no está en el mapeo."""
    with pytest.raises(ValueError, match="no encontrado"):
        adapter._get_uuids("HOTEL-INEXISTENTE", "RM001")


def test_get_uuids_room_no_encontrado(adapter):
    """Lanza ValueError cuando el room_type_code no existe en el hotel."""
    with pytest.raises(ValueError, match="no encontrado"):
        adapter._get_uuids("COL-TEST-001", "RM999")


def test_get_uuids_exitoso(adapter):
    """Retorna la tupla (property_uuid, category_uuid) correctamente."""
    prop_uuid, cat_uuid = adapter._get_uuids("COL-TEST-001", "RM001")
    assert prop_uuid == UUID("550e8400-e29b-41d4-a716-446655440000")
    assert cat_uuid == UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


# ─── MockPMSAdapter.normalize_webhook ───

def test_normalize_webhook_exitoso(adapter):
    """Normaliza correctamente un payload válido de webhook."""
    payload = {
        "hotel_code": "COL-TEST-001",
        "room_type_code": "RM001",
        "date": "2026-06-01",
        "total_units": 10,
        "available_units": 7,
        "last_modified": "2026-06-01T10:00:00Z",
    }
    dto = adapter.normalize_webhook(payload)
    assert dto.id_propiedad == UUID("550e8400-e29b-41d4-a716-446655440000")
    assert dto.id_categoria == UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
    assert dto.cupos_disponibles == 7


def test_normalize_webhook_campo_faltante(adapter):
    """Lanza ValueError cuando falta un campo requerido en el webhook."""
    with pytest.raises(ValueError):
        adapter.normalize_webhook({"hotel_code": "COL-TEST-001"})


def test_normalize_webhook_hotel_no_mapeado(adapter):
    """Lanza ValueError cuando el hotel_code no está en el mapeo."""
    payload = {
        "hotel_code": "UNKNOWN",
        "room_type_code": "RM001",
        "date": "2026-06-01",
        "total_units": 5,
        "available_units": 3,
        "last_modified": "2026-06-01T10:00:00Z",
    }
    with pytest.raises(ValueError):
        adapter.normalize_webhook(payload)


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
            }
        ],
    }
    dtos = adapter.normalize_poll_response(response)
    assert len(dtos) == 1
    assert dtos[0].cupos_disponibles == 5


def test_normalize_poll_response_lista_vacia(adapter):
    """Retorna lista vacía cuando no hay cambios."""
    dtos = adapter.normalize_poll_response({"changes": []})
    assert dtos == []


# ─── adapter_registry.get_adapter ───

def test_get_adapter_mock(mapping_file):
    """get_adapter('mock') retorna un MockPMSAdapter."""
    with patch.object(MockPMSAdapter, "_load_mapping", return_value=_FAKE_MAPPING["mappings"]):
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
