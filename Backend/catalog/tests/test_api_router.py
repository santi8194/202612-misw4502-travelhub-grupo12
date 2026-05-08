from datetime import date
from decimal import Decimal
from unittest.mock import Mock
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from api import router as router_module
from config.app import create_app
from modules.catalog.domain.entities import (
	CategoriaHabitacion,
	Coordenadas,
	Inventario,
	Media,
	TipoMedia,
	VODinero,
	VODireccion,
	VORegla,
	construir_propiedad,
)


PROPERTY_UUID = UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479")
CATEGORY_UUID = UUID("aabbccdd-1111-2222-3333-aabbccdd0001")


def _build_client() -> TestClient:
	return TestClient(create_app())


def _build_property(with_category: bool = False):
	ubicacion = VODireccion(
		ciudad="Cartagena",
		estado_provincia="Bolívar",
		pais="Colombia",
		coordenadas=Coordenadas(lat=10.42, lng=-75.54),
	)
	categorias = []
	if with_category:
		categorias = [
			CategoriaHabitacion(
				id_categoria=CATEGORY_UUID,
				codigo_mapeo_pms="ROOM-DLX-01",
				nombre_comercial="Habitación Deluxe",
				descripcion="Habitación de lujo",
				precio_base=VODinero(
					monto=Decimal("350000.00"),
					moneda="COP",
					cargo_servicio=Decimal("25000.00"),
				),
				capacidad_pax=4,
				politica_cancelacion=VORegla(
					dias_anticipacion=5,
					porcentaje_penalidad=Decimal("50.0"),
				),
				media=[
					Media(
						id_media="cover-1",
						url_full="https://cdn.example.com/cover.jpg",
						tipo=TipoMedia.FOTO_PORTADA,
						orden=1,
					)
				],
			)
		]

	return construir_propiedad(
		id_propiedad=PROPERTY_UUID,
		nombre="Hotel Test",
		estrellas=4,
		ubicacion=ubicacion,
		porcentaje_impuesto=Decimal("19.00"),
		categorias_habitacion=categorias,
	)


def test_health_endpoint_returns_service_status():
	client = _build_client()

	response = client.get("/health")

	assert response.status_code == 200
	assert response.json() == {"status": "ok", "service": "catalog"}


def test_create_property_endpoint_generates_uuid_and_delegates(monkeypatch):
	client = _build_client()
	fixed_uuid = UUID("00000000-0000-0000-0000-000000000123")
	captured = {}

	class FakeCreateProperty:
		def __init__(self, repository, event_bus):
			captured["repository"] = repository
			captured["event_bus"] = event_bus

		def execute(self, **kwargs):
			captured["kwargs"] = kwargs
			return {"id_propiedad": str(kwargs["id_propiedad"]), "event_generated": "PropiedadCreada"}

	monkeypatch.setattr(router_module, "CreateProperty", FakeCreateProperty)
	monkeypatch.setattr(router_module, "uuid4", lambda: fixed_uuid)

	response = client.post(
		"/properties",
		json={
			"nombre": "Hotel Test",
			"estrellas": 4,
			"ciudad": "Cartagena",
			"estado_provincia": "Bolívar",
			"pais": "Colombia",
			"latitud": 10.42,
			"longitud": -75.54,
			"porcentaje_impuesto": "19.00",
		},
	)

	assert response.status_code == 200
	assert response.json()["id_propiedad"] == str(fixed_uuid)
	assert captured["kwargs"]["id_propiedad"] == fixed_uuid
	assert captured["kwargs"]["estado_provincia"] == "Bolívar"


def test_register_category_endpoint_returns_404_when_property_not_found(monkeypatch):
	client = _build_client()

	class FakeRegisterCategory:
		def __init__(self, repository, event_bus):
			pass

		def execute(self, **kwargs):
			return {"error": "Property not found", "id_propiedad": str(kwargs["id_propiedad"])}

	monkeypatch.setattr(router_module, "RegisterCategoryHousing", FakeRegisterCategory)

	response = client.post(
		f"/properties/{PROPERTY_UUID}/categories",
		json={
			"id_propiedad": str(PROPERTY_UUID),
			"codigo_mapeo_pms": "ROOM-DLX-01",
			"nombre_comercial": "Habitación Deluxe",
			"descripcion": "Habitación de lujo",
			"monto_precio_base": "350000.00",
			"cargo_servicio": "25000.00",
			"moneda_precio_base": "COP",
			"capacidad_pax": 4,
			"dias_anticipacion": 5,
			"porcentaje_penalidad": "50.0",
			"foto_portada_url": "https://cdn.example.com/cover.jpg",
		},
	)

	assert response.status_code == 404
	assert response.json()["error"] == "Property not found"


def test_register_category_endpoint_maps_duplicate_integrity_error(monkeypatch):
	client = _build_client()

	class FakeRegisterCategory:
		def __init__(self, repository, event_bus):
			pass

		def execute(self, **kwargs):
			raise IntegrityError("stmt", "params", Exception("codigo_mapeo_pms duplicado"))

	monkeypatch.setattr(router_module, "RegisterCategoryHousing", FakeRegisterCategory)

	response = client.post(
		f"/properties/{PROPERTY_UUID}/categories",
		json={
			"id_propiedad": str(PROPERTY_UUID),
			"codigo_mapeo_pms": "ROOM-DLX-01",
			"nombre_comercial": "Habitación Deluxe",
			"descripcion": "Habitación de lujo",
			"monto_precio_base": "350000.00",
			"cargo_servicio": "25000.00",
			"moneda_precio_base": "COP",
			"capacidad_pax": 4,
			"dias_anticipacion": 5,
			"porcentaje_penalidad": "50.0",
			"foto_portada_url": "https://cdn.example.com/cover.jpg",
		},
	)

	assert response.status_code == 409
	assert "codigo diferente" in response.json()["error"]


def test_register_category_endpoint_maps_unexpected_exception(monkeypatch):
	client = _build_client()

	class FakeRegisterCategory:
		def __init__(self, repository, event_bus):
			pass

		def execute(self, **kwargs):
			raise RuntimeError("boom")

	monkeypatch.setattr(router_module, "RegisterCategoryHousing", FakeRegisterCategory)

	response = client.post(
		f"/properties/{PROPERTY_UUID}/categories",
		json={
			"id_propiedad": str(PROPERTY_UUID),
			"codigo_mapeo_pms": "ROOM-DLX-01",
			"nombre_comercial": "Habitación Deluxe",
			"descripcion": "Habitación de lujo",
			"monto_precio_base": "350000.00",
			"cargo_servicio": "25000.00",
			"moneda_precio_base": "COP",
			"capacidad_pax": 4,
			"dias_anticipacion": 5,
			"porcentaje_penalidad": "50.0",
			"foto_portada_url": "https://cdn.example.com/cover.jpg",
		},
	)

	assert response.status_code == 500
	assert response.json()["error"] == "No se pudo registrar la categoria: boom"


def test_register_category_endpoint_maps_generic_integrity_error(monkeypatch):
	client = _build_client()

	class FakeRegisterCategory:
		def __init__(self, repository, event_bus):
			pass

		def execute(self, **kwargs):
			raise IntegrityError("stmt", "params", Exception("violacion de integridad"))

	monkeypatch.setattr(router_module, "RegisterCategoryHousing", FakeRegisterCategory)

	response = client.post(
		f"/properties/{PROPERTY_UUID}/categories",
		json={
			"id_propiedad": str(PROPERTY_UUID),
			"codigo_mapeo_pms": "ROOM-DLX-01",
			"nombre_comercial": "Habitación Deluxe",
			"descripcion": "Habitación de lujo",
			"monto_precio_base": "350000.00",
			"cargo_servicio": "25000.00",
			"moneda_precio_base": "COP",
			"capacidad_pax": 4,
			"dias_anticipacion": 5,
			"porcentaje_penalidad": "50.0",
			"foto_portada_url": "https://cdn.example.com/cover.jpg",
		},
	)

	assert response.status_code == 409
	assert response.json() == {
		"error": "Conflicto de integridad al registrar la categoria.",
	}


def test_view_detail_endpoint_returns_404_when_query_fails(monkeypatch):
	client = _build_client()

	class FakeDetailQuery:
		def __init__(self, repository):
			pass

		def execute(self, id_categoria):
			return {"error": "Category not found", "id_categoria": str(id_categoria)}

	monkeypatch.setattr(router_module, "ObtainCategoryViewDetail", FakeDetailQuery)

	response = client.get(f"/categories/{CATEGORY_UUID}/view-detail")

	assert response.status_code == 404
	assert response.json()["id_categoria"] == str(CATEGORY_UUID)


def test_view_detail_endpoint_returns_success_payload(monkeypatch):
	client = _build_client()

	class FakeDetailQuery:
		def __init__(self, repository):
			pass

		def execute(self, id_categoria):
			return {"id_categoria": str(id_categoria), "ok": True}

	monkeypatch.setattr(router_module, "ObtainCategoryViewDetail", FakeDetailQuery)

	response = client.get(f"/categories/{CATEGORY_UUID}/view-detail")

	assert response.status_code == 200
	assert response.json() == {"id_categoria": str(CATEGORY_UUID), "ok": True}


def test_obtener_propiedad_returns_not_found_payload(monkeypatch):
	client = _build_client()
	monkeypatch.setattr(router_module, "repository", Mock(obtain=Mock(return_value=None)))

	response = client.get(f"/properties/{PROPERTY_UUID}")

	assert response.status_code == 200
	assert response.json() == {
		"error": "Property not found",
		"id_propiedad": str(PROPERTY_UUID),
	}


def test_obtener_disponibilidad_returns_inventory_payload(monkeypatch):
	client = _build_client()
	propiedad = _build_property(with_category=True)
	propiedad.actualizar_inventario(
		CATEGORY_UUID,
		Inventario(
			id_inventario="inv-2026-05-10",
			fecha=date(2026, 5, 10),
			cupos_totales=10,
			cupos_disponibles=3,
		),
	)
	monkeypatch.setattr(router_module, "repository", Mock(obtain=Mock(return_value=propiedad)))

	response = client.get(
		f"/properties/{PROPERTY_UUID}/categories/{CATEGORY_UUID}/availability/2026-05-10"
	)

	assert response.status_code == 200
	assert response.json() == {
		"id_propiedad": str(PROPERTY_UUID),
		"id_categoria": str(CATEGORY_UUID),
		"fecha": "2026-05-10",
		"cupos_totales": 10,
		"cupos_disponibles": 3,
	}


def test_obtener_propiedades_serializes_repository_result(monkeypatch):
	client = _build_client()
	monkeypatch.setattr(
		router_module,
		"repository",
		Mock(obtain_all=Mock(return_value=[_build_property(with_category=True)])),
	)

	response = client.get("/properties")

	assert response.status_code == 200
	body = response.json()
	assert body["total"] == 1
	assert body["propiedades"][0]["id_propiedad"] == str(PROPERTY_UUID)
	assert body["propiedades"][0]["estado_provincia"] == "Bolívar"
	assert body["propiedades"][0]["categorias"] == 1


def test_obtener_categorias_de_propiedad_delegates_query(monkeypatch):
	client = _build_client()

	class FakeQuery:
		def __init__(self, repository, event_bus):
			pass

		def execute(self, id_propiedad):
			return {"id_propiedad": str(id_propiedad), "total_categorias": 0, "categorias": []}

	monkeypatch.setattr(router_module, "ObtainCategoriesByPropertyId", FakeQuery)

	response = client.get(f"/properties/{PROPERTY_UUID}/categories")

	assert response.status_code == 200
	assert response.json()["id_propiedad"] == str(PROPERTY_UUID)


def test_actualizar_inventario_delegates_command(monkeypatch):
	client = _build_client()
	recorded = {}

	class FakeUpdateInventory:
		def __init__(self, repository, event_bus):
			pass

		def execute(self, **kwargs):
			recorded.update(kwargs)
			return {
				"id_propiedad": str(kwargs["id_propiedad"]),
				"id_categoria": str(kwargs["id_categoria"]),
				"id_inventario": kwargs["id_inventario"],
				"event_generated": "InventarioActualizado",
			}

	monkeypatch.setattr(router_module, "UpdateInventory", FakeUpdateInventory)

	response = client.put(
		f"/properties/{PROPERTY_UUID}/categories/{CATEGORY_UUID}/inventory",
		json={
			"id_inventario": "inv-1",
			"fecha": "2026-05-10",
			"cupos_totales": 10,
			"cupos_disponibles": 7,
		},
	)

	assert response.status_code == 200
	assert response.json()["event_generated"] == "InventarioActualizado"
	assert recorded["id_propiedad"] == PROPERTY_UUID
	assert recorded["id_categoria"] == CATEGORY_UUID


def test_actualizar_inventario_rejects_path_body_mismatch(monkeypatch):
	client = _build_client()
	monkeypatch.setattr(router_module, "UpdateInventory", Mock())

	response = client.put(
		f"/properties/{PROPERTY_UUID}/categories/{CATEGORY_UUID}/inventory",
		json={
			"id_propiedad": str(CATEGORY_UUID),
			"id_inventario": "inv-1",
			"fecha": "2026-05-10",
			"cupos_totales": 10,
			"cupos_disponibles": 7,
		},
	)

	assert response.status_code == 400
	assert response.json()["error"] == "Path/body property mismatch"


def test_obtener_propiedad_success_payload(monkeypatch):
	client = _build_client()
	monkeypatch.setattr(router_module, "repository", Mock(obtain=Mock(return_value=_build_property())))

	response = client.get(f"/properties/{PROPERTY_UUID}")

	assert response.status_code == 200
	body = response.json()
	assert body["id_propiedad"] == str(PROPERTY_UUID)
	assert body["nombre"] == "Hotel Test"
	assert body["ubicacion"]["estado_provincia"] == "Bolívar"


def test_obtener_propiedad_por_categoria_delegates_query(monkeypatch):
	client = _build_client()

	class FakeByCategory:
		def __init__(self, repository):
			pass

		def execute(self, id_categoria):
			return {"id_categoria": str(id_categoria), "id_propiedad": str(PROPERTY_UUID)}

	monkeypatch.setattr(router_module, "ObtainPropertyByCategoryId", FakeByCategory)

	response = client.get(f"/properties/by-category/{CATEGORY_UUID}")

	assert response.status_code == 200
	assert response.json()["id_propiedad"] == str(PROPERTY_UUID)


def test_obtener_categoria_por_id_delegates_query(monkeypatch):
	client = _build_client()

	class FakeCategoryById:
		def __init__(self, repository):
			pass

		def execute(self, id_categoria):
			return {"id_categoria": str(id_categoria), "nombre_comercial": "Deluxe"}

	monkeypatch.setattr(router_module, "ObtainCategoryById", FakeCategoryById)

	response = client.get(f"/categories/{CATEGORY_UUID}")

	assert response.status_code == 200
	assert response.json()["nombre_comercial"] == "Deluxe"


def test_obtener_disponibilidad_returns_property_not_found(monkeypatch):
	client = _build_client()
	monkeypatch.setattr(router_module, "repository", Mock(obtain=Mock(return_value=None)))

	response = client.get(
		f"/properties/{PROPERTY_UUID}/categories/{CATEGORY_UUID}/availability/2026-05-10"
	)

	assert response.status_code == 200
	assert response.json() == {
		"error": "Property not found",
		"id_propiedad": str(PROPERTY_UUID),
	}


def test_obtener_disponibilidad_returns_no_inventory(monkeypatch):
	client = _build_client()
	monkeypatch.setattr(router_module, "repository", Mock(obtain=Mock(return_value=_build_property())))

	response = client.get(
		f"/properties/{PROPERTY_UUID}/categories/{CATEGORY_UUID}/availability/2026-05-10"
	)

	assert response.status_code == 200
	body = response.json()
	assert body["error"] == "No inventory found"
	assert body["id_propiedad"] == str(PROPERTY_UUID)
	assert body["id_categoria"] == str(CATEGORY_UUID)
	assert body["fecha"] == "2026-05-10"