import datetime

import pytest

from modulos.reserva.infraestructura.catalog_client import CatalogServiceClient


def _inventory_item(fecha: str, disponibles: int = 3, totales: int = 5) -> dict:
    return {
        "id_inventario": f"inv-{fecha}",
        "fecha": fecha,
        "cupos_totales": totales,
        "cupos_disponibles": disponibles,
    }


def test_reserve_inventory_actualiza_todas_las_fechas_hasta_checkout_inclusive():
    client = CatalogServiceClient(base_url="http://catalog.local")
    fechas = ["2026-04-01", "2026-04-02", "2026-04-03"]

    client.get_property_by_category_id = lambda _id_categoria: {"id_propiedad": "prop-1"}
    client.get_category_by_id = lambda _id_categoria: {
        "inventario": [
            _inventory_item("2026-04-01T00:00:00", disponibles=4),
            _inventory_item("2026-04-02", disponibles=4),
            _inventory_item("2026-04-03", disponibles=4),
        ]
    }

    updated_items: list[dict] = []

    def _fake_update(_id_propiedad: str, _id_categoria: str, item: dict) -> dict:
        updated_items.append(item)
        return {}

    client.update_inventory = _fake_update

    original_items = client.reserve_inventory(
        id_categoria="cat-1",
        fecha_check_in=datetime.date(2026, 4, 1),
        fecha_check_out=datetime.date(2026, 4, 3),
    )

    assert [item["fecha"] for item in updated_items] == fechas
    assert all(item["cupos_disponibles"] == 3 for item in updated_items)
    assert [item["fecha"] for item in original_items] == fechas
    assert all(item["cupos_disponibles"] == 4 for item in original_items)


def test_release_inventory_intenta_todas_las_fechas_y_reporta_fallos():
    client = CatalogServiceClient(base_url="http://catalog.local")

    client.get_property_by_category_id = lambda _id_categoria: {"id_propiedad": "prop-1"}
    client.get_category_by_id = lambda _id_categoria: {
        "inventario": [
            _inventory_item("2026-04-01", disponibles=2),
            _inventory_item("2026-04-02", disponibles=2),
            _inventory_item("2026-04-03", disponibles=2),
        ]
    }

    attempted_dates: list[str] = []

    def _fake_update(_id_propiedad: str, _id_categoria: str, item: dict) -> dict:
        attempted_dates.append(item["fecha"])
        if item["fecha"] == "2026-04-02":
            raise ValueError("fallo de red")
        return {}

    client.update_inventory = _fake_update

    with pytest.raises(ValueError, match="2026-04-02"):
        client.release_inventory(
            id_categoria="cat-1",
            fecha_check_in=datetime.date(2026, 4, 1),
            fecha_check_out=datetime.date(2026, 4, 3),
        )

    assert attempted_dates == ["2026-04-01", "2026-04-02", "2026-04-03"]
