"""
Pruebas adicionales para CatalogServiceClient: manejo de errores HTTP, URL, y métodos privados.
"""
import datetime
import json
from unittest.mock import patch, MagicMock
from urllib import error

import pytest

from modulos.reserva.infraestructura.catalog_client import CatalogServiceClient, _normalize_inventory_date


# --- Pruebas de _normalize_inventory_date ---

def test_normalize_inventory_date_extrae_solo_fecha_de_iso_datetime():
    """Verifica que _normalize_inventory_date extrae solo la fecha de un datetime ISO."""
    resultado = _normalize_inventory_date("2026-04-01T10:30:00")
    assert resultado == "2026-04-01"


def test_normalize_inventory_date_mantiene_fecha_simple():
    """Verifica que _normalize_inventory_date mantiene una fecha simple sin cambios."""
    resultado = _normalize_inventory_date("2026-04-01")
    assert resultado == "2026-04-01"


def test_normalize_inventory_date_maneja_fecha_con_zona_horaria():
    """Verifica que _normalize_inventory_date maneja fechas con zona horaria."""
    resultado = _normalize_inventory_date("2026-04-01T10:30:00+00:00")
    assert resultado == "2026-04-01"


# --- Pruebas de _default_base_url ---

def test_default_base_url_retorna_cloudfront_por_defecto():
    """Verifica que _default_base_url retorna la URL de CloudFront por defecto."""
    client = CatalogServiceClient()
    url = client._default_base_url()
    
    assert url == "https://d1d660udfb1fc0.cloudfront.net/catalog"


@patch("os.path.exists")
def test_default_base_url_retorna_cloudfront_en_docker(mock_exists):
    """Verifica que _default_base_url retorna CloudFront incluso en Docker."""
    mock_exists.return_value = True
    
    client = CatalogServiceClient()
    url = client._default_base_url()
    
    assert url == "https://d1d660udfb1fc0.cloudfront.net/catalog"


# --- Pruebas de _request_json con errores HTTP ---

@patch("modulos.reserva.infraestructura.catalog_client.request.urlopen")
def test_request_json_maneja_http_error_con_json_response(mock_urlopen):
    """Verifica que _request_json maneja HTTPError con respuesta JSON."""
    client = CatalogServiceClient(base_url="http://catalog.local")
    
    error_response = json.dumps({"error": "Categoría no encontrada"}).encode("utf-8")
    http_error = error.HTTPError("url", 404, "Not Found", {}, MagicMock())
    http_error.read = MagicMock(return_value=error_response)
    mock_urlopen.side_effect = http_error
    
    with pytest.raises(ValueError, match="Categoría no encontrada"):
        client._request_json("GET", "/categories/123")


@patch("modulos.reserva.infraestructura.catalog_client.request.urlopen")
def test_request_json_maneja_http_error_sin_json_response(mock_urlopen):
    """Verifica que _request_json maneja HTTPError sin respuesta JSON válida."""
    client = CatalogServiceClient(base_url="http://catalog.local")
    
    http_error = error.HTTPError("url", 500, "Internal Server Error", {}, MagicMock())
    http_error.read = MagicMock(return_value=b"Error interno del servidor")
    mock_urlopen.side_effect = http_error
    
    with pytest.raises(ValueError, match="(HTTP 500|Error interno del servidor)"):
        client._request_json("GET", "/categories/123")


@patch("modulos.reserva.infraestructura.catalog_client.request.urlopen")
def test_request_json_maneja_url_error(mock_urlopen):
    """Verifica que _request_json maneja URLError (conexión fallida)."""
    client = CatalogServiceClient(base_url="http://catalog.local")
    
    mock_urlopen.side_effect = error.URLError("Connection refused")
    
    with pytest.raises(ValueError, match="No fue posible conectar con el servicio de catalog"):
        client._request_json("GET", "/categories/123")


@patch("modulos.reserva.infraestructura.catalog_client.request.urlopen")
def test_request_json_envia_headers_correctos_para_get(mock_urlopen):
    """Verifica que _request_json envía headers correctos para GET."""
    client = CatalogServiceClient(base_url="http://catalog.local")
    
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"result": "ok"}'
    mock_urlopen.return_value.__enter__.return_value = mock_response
    
    client._request_json("GET", "/test")
    
    request_obj = mock_urlopen.call_args[0][0]
    assert request_obj.headers["Accept"] == "application/json"
    assert "Content-type" not in request_obj.headers


@patch("modulos.reserva.infraestructura.catalog_client.request.urlopen")
def test_request_json_envia_headers_y_body_para_post(mock_urlopen):
    """Verifica que _request_json envía headers y body correctos para POST."""
    client = CatalogServiceClient(base_url="http://catalog.local")
    
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"result": "created"}'
    mock_urlopen.return_value.__enter__.return_value = mock_response
    
    body = {"dato": "valor"}
    client._request_json("POST", "/test", body=body)
    
    request_obj = mock_urlopen.call_args[0][0]
    assert request_obj.headers["Accept"] == "application/json"
    assert request_obj.headers["Content-type"] == "application/json"
    assert json.loads(request_obj.data.decode("utf-8")) == body


# --- Pruebas de get_property_by_category_id ---

@patch("modulos.reserva.infraestructura.catalog_client.request.urlopen")
def test_get_property_by_category_id_retorna_propiedad(mock_urlopen):
    """Verifica que get_property_by_category_id retorna la propiedad correctamente."""
    client = CatalogServiceClient(base_url="http://catalog.local")
    
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({"id_propiedad": "prop-1"}).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_response
    
    resultado = client.get_property_by_category_id("cat-1")
    
    assert resultado["id_propiedad"] == "prop-1"


# --- Pruebas de get_category_by_id ---

@patch("modulos.reserva.infraestructura.catalog_client.request.urlopen")
def test_get_category_by_id_retorna_categoria(mock_urlopen):
    """Verifica que get_category_by_id retorna la categoría correctamente."""
    client = CatalogServiceClient(base_url="http://catalog.local")
    
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({"id_categoria": "cat-1", "inventario": []}).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_response
    
    resultado = client.get_category_by_id("cat-1")
    
    assert resultado["id_categoria"] == "cat-1"


# --- Pruebas de get_categories_by_property_id ---

@patch("modulos.reserva.infraestructura.catalog_client.request.urlopen")
def test_get_categories_by_property_id_retorna_categorias(mock_urlopen):
    """Verifica que get_categories_by_property_id retorna las categorías."""
    client = CatalogServiceClient(base_url="http://catalog.local")
    
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({"categorias": []}).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_response
    
    resultado = client.get_categories_by_property_id("prop-1")
    
    assert "categorias" in resultado


# --- Pruebas de update_inventory ---

@patch("modulos.reserva.infraestructura.catalog_client.request.urlopen")
def test_update_inventory_envia_payload_correcto(mock_urlopen):
    """Verifica que update_inventory envía el payload correcto."""
    client = CatalogServiceClient(base_url="http://catalog.local")
    
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"result": "updated"}'
    mock_urlopen.return_value.__enter__.return_value = mock_response
    
    inventory_item = {
        "id_inventario": "inv-1",
        "fecha": "2026-04-01",
        "cupos_totales": 5,
        "cupos_disponibles": 3,
    }
    
    client.update_inventory("prop-1", "cat-1", inventory_item)
    
    request_obj = mock_urlopen.call_args[0][0]
    body = json.loads(request_obj.data.decode("utf-8"))
    
    assert body["id_propiedad"] == "prop-1"
    assert body["id_categoria"] == "cat-1"
    assert body["id_inventario"] == "inv-1"
    assert body["cupos_disponibles"] == 3


# --- Pruebas de restore_inventory ---

def test_restore_inventory_intenta_restaurar_todos_los_items():
    """Verifica que restore_inventory intenta restaurar todos los items, incluso si algunos fallan."""
    client = CatalogServiceClient(base_url="http://catalog.local")
    
    original_items = [
        {"id_propiedad": "prop-1", "fecha": "2026-04-01", "cupos_disponibles": 4, "id_inventario": "inv-1", "cupos_totales": 5},
        {"id_propiedad": "prop-1", "fecha": "2026-04-02", "cupos_disponibles": 4, "id_inventario": "inv-2", "cupos_totales": 5},
    ]
    
    intentos = []
    
    def fake_update(id_propiedad, id_categoria, item):
        intentos.append(item["fecha"])
        if item["fecha"] == "2026-04-01":
            raise ValueError("Error de red")
    
    client.update_inventory = fake_update
    
    # restore_inventory no debe lanzar excepción, solo continuar
    client.restore_inventory("cat-1", original_items)
    
    assert len(intentos) == 2
    assert "2026-04-01" in intentos
    assert "2026-04-02" in intentos


# --- Pruebas de _build_inventory_updates edge cases ---

def test_build_inventory_updates_lanza_error_si_categoria_no_existe():
    """Verifica que _build_inventory_updates lanza error si la categoría no existe."""
    client = CatalogServiceClient(base_url="http://catalog.local")
    
    client.get_property_by_category_id = lambda _: {"error": "No encontrada"}
    
    with pytest.raises(ValueError, match="La categoria no existe en catalog"):
        client._build_inventory_updates(
            "cat-inexistente",
            datetime.date(2026, 4, 1),
            datetime.date(2026, 4, 2),
            delta=-1,
            require_availability=True,
            cap_at_total=False,
        )


def test_build_inventory_updates_lanza_error_si_no_hay_inventario_para_fecha():
    """Verifica que _build_inventory_updates lanza error si no hay inventario para una fecha."""
    client = CatalogServiceClient(base_url="http://catalog.local")
    
    client.get_property_by_category_id = lambda _: {"id_propiedad": "prop-1"}
    client.get_category_by_id = lambda _: {
        "inventario": [
            {"fecha": "2026-04-01", "cupos_disponibles": 3, "cupos_totales": 5, "id_inventario": "inv-1"}
        ]
    }
    
    with pytest.raises(ValueError, match="No existe inventario para la categoria en la fecha 2026-04-02"):
        client._build_inventory_updates(
            "cat-1",
            datetime.date(2026, 4, 1),
            datetime.date(2026, 4, 2),
            delta=-1,
            require_availability=True,
            cap_at_total=False,
        )


def test_build_inventory_updates_lanza_error_si_no_hay_disponibilidad():
    """Verifica que _build_inventory_updates lanza error si no hay disponibilidad y require_availability=True."""
    client = CatalogServiceClient(base_url="http://catalog.local")
    
    client.get_property_by_category_id = lambda _: {"id_propiedad": "prop-1"}
    client.get_category_by_id = lambda _: {
        "inventario": [
            {"fecha": "2026-04-01", "cupos_disponibles": 0, "cupos_totales": 5, "id_inventario": "inv-1"}
        ]
    }
    
    with pytest.raises(ValueError, match="No hay disponibilidad para la categoria en la fecha 2026-04-01"):
        client._build_inventory_updates(
            "cat-1",
            datetime.date(2026, 4, 1),
            datetime.date(2026, 4, 1),
            delta=-1,
            require_availability=True,
            cap_at_total=False,
        )


def test_build_inventory_updates_aplica_cap_at_total():
    """Verifica que _build_inventory_updates limita cupos_disponibles al total cuando cap_at_total=True."""
    client = CatalogServiceClient(base_url="http://catalog.local")
    
    client.get_property_by_category_id = lambda _: {"id_propiedad": "prop-1"}
    client.get_category_by_id = lambda _: {
        "inventario": [
            {"fecha": "2026-04-01", "cupos_disponibles": 4, "cupos_totales": 5, "id_inventario": "inv-1"}
        ]
    }
    
    id_propiedad, updated_items = client._build_inventory_updates(
        "cat-1",
        datetime.date(2026, 4, 1),
        datetime.date(2026, 4, 1),
        delta=2,  # Intentar aumentar a 6
        require_availability=False,
        cap_at_total=True,
    )
    
    assert updated_items[0]["cupos_disponibles"] == 5  # Limitado al total


def test_build_inventory_updates_no_genera_update_si_no_hay_cambio():
    """Verifica que _build_inventory_updates no genera update si cupos_disponibles no cambia."""
    client = CatalogServiceClient(base_url="http://catalog.local")
    
    client.get_property_by_category_id = lambda _: {"id_propiedad": "prop-1"}
    client.get_category_by_id = lambda _: {
        "inventario": [
            {"fecha": "2026-04-01", "cupos_disponibles": 5, "cupos_totales": 5, "id_inventario": "inv-1"}
        ]
    }
    
    id_propiedad, updated_items = client._build_inventory_updates(
        "cat-1",
        datetime.date(2026, 4, 1),
        datetime.date(2026, 4, 1),
        delta=1,
        require_availability=False,
        cap_at_total=True,  # Ya está en el máximo
    )
    
    assert len(updated_items) == 0
