import pytest
from decimal import Decimal
from uuid import UUID
from unittest.mock import Mock
from catalog.modules.catalog.application.commands.create_property import CreateProperty
from catalog.modules.catalog.application.commands.register_category_housing import RegisterCategoryHousing
from catalog.modules.catalog.application.commands.update_inventory import UpdateInventory
from catalog.modules.catalog.domain.entities import (
	Coordenadas,
	VODireccion,
	VODinero,
	VORegla,
	CategoriaHabitacion,
	Propiedad,
	construir_propiedad,
)
from datetime import date


@pytest.fixture
def mock_repository():
	return Mock()


@pytest.fixture
def mock_event_bus():
	return Mock()


@pytest.fixture
def property_id():
	return UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479")


class TestCreateProperty:
	"""Pruebas para el comando CreateProperty"""

	def test_create_property_success(self, mock_repository, mock_event_bus, property_id):
		mock_repository.obtain.return_value = None

		command = CreateProperty(mock_repository, mock_event_bus)
		result = command.execute(
			id_propiedad=property_id,
			nombre="Hotel Test",
			estrellas=4,
			ciudad="Cartagena",
			pais="Colombia",
			latitud=10.42,
			longitud=-75.54,
			porcentaje_impuesto=Decimal("19.00"),
		)

		assert result["nombre"] == "Hotel Test"
		assert result["estrellas"] == 4
		assert result["event_generated"] == "PropiedadCreada"
		assert mock_repository.save.called
		assert mock_event_bus.publish_event.called

	def test_create_property_already_exists(self, mock_repository, mock_event_bus, property_id):
		# Propiedad existente
		coords = Coordenadas(lat=10.42, lng=-75.54)
		ubicacion = VODireccion(ciudad="Cartagena", pais="Colombia", coordenadas=coords)
		existing_property = construir_propiedad(
			id_propiedad=property_id,
			nombre="Existing Hotel",
			estrellas=4,
			ubicacion=ubicacion,
			porcentaje_impuesto=Decimal("19.00"),
		)
		mock_repository.obtain.return_value = existing_property

		command = CreateProperty(mock_repository, mock_event_bus)
		result = command.execute(
			id_propiedad=property_id,
			nombre="Hotel Test",
			estrellas=4,
			ciudad="Cartagena",
			pais="Colombia",
			latitud=10.42,
			longitud=-75.54,
			porcentaje_impuesto=Decimal("19.00"),
		)

		assert result["message"] == "Property already exists"
		assert not mock_repository.save.called


class TestRegisterCategoryHousing:
	"""Pruebas para el comando RegisterCategoryHousing"""

	def test_register_category_success(self, mock_repository, mock_event_bus, property_id):
		# Crear propiedad sin categorías
		coords = Coordenadas(lat=10.42, lng=-75.54)
		ubicacion = VODireccion(ciudad="Cartagena", pais="Colombia", coordenadas=coords)
		propiedad = construir_propiedad(
			id_propiedad=property_id,
			nombre="Hotel Test",
			estrellas=4,
			ubicacion=ubicacion,
			porcentaje_impuesto=Decimal("19.00"),
		)
		mock_repository.obtain.return_value = propiedad

		command = RegisterCategoryHousing(mock_repository, mock_event_bus)
		result = command.execute(
			id_propiedad=property_id,
			id_categoria="deluxe-001",
			codigo_mapeo_pms="ROOM-DLX-01",
			nombre_comercial="Habitación Deluxe",
			descripcion="Habitación de lujo",
			monto_precio_base=Decimal("350000.00"),
			moneda_precio_base="COP",
			capacidad_pax=4,
			dias_anticipacion=5,
			porcentaje_penalidad=Decimal("50.0"),
		)

		assert result["id_categoria"] == "deluxe-001"
		assert result["event_generated"] == "CategoriaHabitacionRegistrada"
		assert mock_repository.save.called
		assert mock_event_bus.publish_event.called

	def test_register_category_property_not_found(self, mock_repository, mock_event_bus, property_id):
		mock_repository.obtain.return_value = None

		command = RegisterCategoryHousing(mock_repository, mock_event_bus)
		result = command.execute(
			id_propiedad=property_id,
			id_categoria="deluxe-001",
			codigo_mapeo_pms="ROOM-DLX-01",
			nombre_comercial="Habitación Deluxe",
			descripcion="Habitación de lujo",
			monto_precio_base=Decimal("350000.00"),
			moneda_precio_base="COP",
			capacidad_pax=4,
			dias_anticipacion=5,
			porcentaje_penalidad=Decimal("50.0"),
		)

		assert result["error"] == "Property not found"
		assert not mock_repository.save.called

	def test_register_category_already_exists(self, mock_repository, mock_event_bus, property_id):
		# Crear propiedad con categoría
		coords = Coordenadas(lat=10.42, lng=-75.54)
		ubicacion = VODireccion(ciudad="Cartagena", pais="Colombia", coordenadas=coords)
		precio = VODinero(monto=Decimal("350000.00"), moneda="COP")
		regla = VORegla(dias_anticipacion=5, porcentaje_penalidad=Decimal("50.0"))
		categoria = CategoriaHabitacion(
			id_categoria="deluxe-001",
			codigo_mapeo_pms="ROOM-DLX-01",
			nombre_comercial="Habitación Deluxe",
			descripcion="Habitación de lujo",
			precio_base=precio,
			capacidad_pax=4,
			politica_cancelacion=regla,
		)
		propiedad = construir_propiedad(
			id_propiedad=property_id,
			nombre="Hotel Test",
			estrellas=4,
			ubicacion=ubicacion,
			porcentaje_impuesto=Decimal("19.00"),
			categorias_habitacion=[categoria],
		)
		mock_repository.obtain.return_value = propiedad

		command = RegisterCategoryHousing(mock_repository, mock_event_bus)
		result = command.execute(
			id_propiedad=property_id,
			id_categoria="deluxe-001",
			codigo_mapeo_pms="ROOM-DLX-01",
			nombre_comercial="Habitación Deluxe",
			descripcion="Habitación de lujo",
			monto_precio_base=Decimal("350000.00"),
			moneda_precio_base="COP",
			capacidad_pax=4,
			dias_anticipacion=5,
			porcentaje_penalidad=Decimal("50.0"),
		)

		assert result["message"] == "Category already registered"
		assert not mock_repository.save.called


class TestUpdateInventory:
	"""Pruebas para el comando UpdateInventory"""

	def test_update_inventory_success(self, mock_repository, mock_event_bus, property_id):
		# Crear propiedad con categoría
		coords = Coordenadas(lat=10.42, lng=-75.54)
		ubicacion = VODireccion(ciudad="Cartagena", pais="Colombia", coordenadas=coords)
		precio = VODinero(monto=Decimal("350000.00"), moneda="COP")
		regla = VORegla(dias_anticipacion=5, porcentaje_penalidad=Decimal("50.0"))
		categoria = CategoriaHabitacion(
			id_categoria="deluxe-001",
			codigo_mapeo_pms="ROOM-DLX-01",
			nombre_comercial="Habitación Deluxe",
			descripcion="Habitación de lujo",
			precio_base=precio,
			capacidad_pax=4,
			politica_cancelacion=regla,
		)
		propiedad = construir_propiedad(
			id_propiedad=property_id,
			nombre="Hotel Test",
			estrellas=4,
			ubicacion=ubicacion,
			porcentaje_impuesto=Decimal("19.00"),
			categorias_habitacion=[categoria],
		)
		mock_repository.obtain.return_value = propiedad

		command = UpdateInventory(mock_repository, mock_event_bus)
		result = command.execute(
			id_propiedad=property_id,
			id_categoria="deluxe-001",
			id_inventario="inv-2026-05-10",
			fecha=date(2026, 5, 10),
			cupos_totales=10,
			cupos_disponibles=3,
		)

		assert result["cupos_disponibles"] == 3
		assert result["event_generated"] == "InventarioActualizado"
		assert mock_repository.save.called
		assert mock_event_bus.publish_event.called

	def test_update_inventory_property_not_found(self, mock_repository, mock_event_bus, property_id):
		mock_repository.obtain.return_value = None

		command = UpdateInventory(mock_repository, mock_event_bus)
		result = command.execute(
			id_propiedad=property_id,
			id_categoria="deluxe-001",
			id_inventario="inv-2026-05-10",
			fecha=date(2026, 5, 10),
			cupos_totales=10,
			cupos_disponibles=3,
		)

		assert result["error"] == "Property not found"
		assert not mock_repository.save.called

	def test_update_inventory_category_not_found(self, mock_repository, mock_event_bus, property_id):
		# Crear propiedad sin categorías
		coords = Coordenadas(lat=10.42, lng=-75.54)
		ubicacion = VODireccion(ciudad="Cartagena", pais="Colombia", coordenadas=coords)
		propiedad = construir_propiedad(
			id_propiedad=property_id,
			nombre="Hotel Test",
			estrellas=4,
			ubicacion=ubicacion,
			porcentaje_impuesto=Decimal("19.00"),
		)
		mock_repository.obtain.return_value = propiedad

		command = UpdateInventory(mock_repository, mock_event_bus)
		result = command.execute(
			id_propiedad=property_id,
			id_categoria="nonexistent",
			id_inventario="inv-2026-05-10",
			fecha=date(2026, 5, 10),
			cupos_totales=10,
			cupos_disponibles=3,
		)

		assert result["error"] == "Category not found"
		assert not mock_repository.save.called
