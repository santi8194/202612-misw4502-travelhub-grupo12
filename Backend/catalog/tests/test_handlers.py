"""Tests unitarios para los handlers de infraestructura del Catalog."""

import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch
from uuid import uuid4

from catalog.modules.catalog.infrastructure.services.handlers import (
    handle_create_property,
    handle_register_category_housing,
    handle_update_inventory,
)

_MODULE = "catalog.modules.catalog.infrastructure.services.handlers"


def _data_create_property(**overrides):
    """Datos mínimos válidos para handle_create_property."""
    data = {
        "id_propiedad": str(uuid4()),
        "nombre": "Hotel Test",
        "estrellas": 4,
        "ciudad": "Bogotá",
        "pais": "Colombia",
        "latitud": 4.71,
        "longitud": -74.07,
        "porcentaje_impuesto": "19.00",
    }
    data.update(overrides)
    return data


def _data_register_category(**overrides):
    """Datos mínimos válidos para handle_register_category_housing."""
    data = {
        "id_propiedad": str(uuid4()),
        "codigo_mapeo_pms": "RM001",
        "nombre_comercial": "Suite Deluxe",
        "descripcion": "Habitación de lujo con vista al mar",
        "monto_precio_base": "300000",
        "cargo_servicio": "15000",
        "moneda_precio_base": "COP",
        "capacidad_pax": 2,
        "dias_anticipacion": 3,
        "porcentaje_penalidad": "50.0",
        "foto_portada_url": "https://example.com/img.jpg",
    }
    data.update(overrides)
    return data


def _data_update_inventory(**overrides):
    """Datos mínimos válidos para handle_update_inventory."""
    data = {
        "id_propiedad": str(uuid4()),
        "id_categoria": str(uuid4()),
        "id_inventario": str(uuid4()),
        "fecha": "2026-06-01",
        "cupos_totales": 10,
        "cupos_disponibles": 5,
    }
    data.update(overrides)
    return data


# ─── handle_create_property ───

def test_handle_create_property_retorna_resultado():
    """handle_create_property invoca el use case y retorna su resultado."""
    expected = {"id": str(uuid4()), "nombre": "Hotel Test"}
    mock_uc = MagicMock()
    mock_uc.execute.return_value = expected

    with patch(f"{_MODULE}.PropertyRepository"), \
         patch(f"{_MODULE}.EventBus"), \
         patch(f"{_MODULE}.CreateProperty", return_value=mock_uc):

        result = handle_create_property(_data_create_property())

    mock_uc.execute.assert_called_once()
    assert result == expected


def test_handle_create_property_pasa_porcentaje_impuesto_como_decimal():
    """handle_create_property convierte porcentaje_impuesto a Decimal."""
    mock_uc = MagicMock()
    mock_uc.execute.return_value = {}

    with patch(f"{_MODULE}.PropertyRepository"), \
         patch(f"{_MODULE}.EventBus"), \
         patch(f"{_MODULE}.CreateProperty", return_value=mock_uc):

        handle_create_property(_data_create_property(porcentaje_impuesto="19.00"))

    _, kwargs = mock_uc.execute.call_args
    assert isinstance(kwargs["porcentaje_impuesto"], Decimal)


def test_handle_create_property_campo_faltante_lanza_error():
    """Lanza error cuando faltan campos obligatorios."""
    with patch(f"{_MODULE}.PropertyRepository"), \
         patch(f"{_MODULE}.EventBus"):

        with pytest.raises((KeyError, Exception)):
            handle_create_property({"id_propiedad": str(uuid4())})


# ─── handle_register_category_housing ───

def test_handle_register_category_housing_retorna_resultado():
    """handle_register_category_housing invoca el use case y retorna su resultado."""
    expected = {"id_categoria": str(uuid4())}
    mock_uc = MagicMock()
    mock_uc.execute.return_value = expected

    with patch(f"{_MODULE}.PropertyRepository"), \
         patch(f"{_MODULE}.EventBus"), \
         patch(f"{_MODULE}.RegisterCategoryHousing", return_value=mock_uc):

        result = handle_register_category_housing(_data_register_category())

    mock_uc.execute.assert_called_once()
    assert result == expected


def test_handle_register_category_convierte_precios_a_decimal():
    """handle_register_category_housing convierte montos a Decimal."""
    mock_uc = MagicMock()
    mock_uc.execute.return_value = {}

    with patch(f"{_MODULE}.PropertyRepository"), \
         patch(f"{_MODULE}.EventBus"), \
         patch(f"{_MODULE}.RegisterCategoryHousing", return_value=mock_uc):

        handle_register_category_housing(_data_register_category())

    _, kwargs = mock_uc.execute.call_args
    assert isinstance(kwargs["monto_precio_base"], Decimal)
    assert isinstance(kwargs["cargo_servicio"], Decimal)
    assert isinstance(kwargs["porcentaje_penalidad"], Decimal)


def test_handle_register_category_campo_faltante_lanza_error():
    """Lanza error cuando faltan campos obligatorios."""
    with patch(f"{_MODULE}.PropertyRepository"), \
         patch(f"{_MODULE}.EventBus"):

        with pytest.raises((KeyError, Exception)):
            handle_register_category_housing({"id_propiedad": str(uuid4())})


# ─── handle_update_inventory ───

def test_handle_update_inventory_retorna_resultado():
    """handle_update_inventory invoca el use case y retorna su resultado."""
    expected = {"updated": True}
    mock_uc = MagicMock()
    mock_uc.execute.return_value = expected

    with patch(f"{_MODULE}.PropertyRepository"), \
         patch(f"{_MODULE}.EventBus"), \
         patch(f"{_MODULE}.UpdateInventory", return_value=mock_uc):

        result = handle_update_inventory(_data_update_inventory())

    mock_uc.execute.assert_called_once()
    assert result == expected


def test_handle_update_inventory_convierte_fecha():
    """handle_update_inventory convierte fecha de string a date."""
    from datetime import date

    mock_uc = MagicMock()
    mock_uc.execute.return_value = {}

    with patch(f"{_MODULE}.PropertyRepository"), \
         patch(f"{_MODULE}.EventBus"), \
         patch(f"{_MODULE}.UpdateInventory", return_value=mock_uc):

        handle_update_inventory(_data_update_inventory(fecha="2026-06-15"))

    _, kwargs = mock_uc.execute.call_args
    assert kwargs["fecha"] == date(2026, 6, 15)


def test_handle_update_inventory_campo_faltante_lanza_error():
    """Lanza error cuando faltan campos obligatorios."""
    with patch(f"{_MODULE}.PropertyRepository"), \
         patch(f"{_MODULE}.EventBus"):

        with pytest.raises((KeyError, Exception)):
            handle_update_inventory({"id_propiedad": str(uuid4())})
