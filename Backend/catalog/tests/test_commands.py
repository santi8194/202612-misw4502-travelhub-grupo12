import pytest
from decimal import Decimal
from uuid import UUID
from unittest.mock import Mock
import uuid
from catalog.modules.catalog.application.commands.create_property import CreateProperty
from catalog.modules.catalog.application.commands.register_category_housing import RegisterCategoryHousing
from catalog.modules.catalog.application.commands.update_inventory import UpdateInventory
from catalog.modules.catalog.application.commands.obtain_property_by_category_id import ObtainPropertyByCategoryId
from catalog.modules.catalog.application.commands.obtain_category_by_id import ObtainCategoryById
from catalog.modules.catalog.application.commands.obtain_categories_by_property_id import ObtainCategoriesByPropertyId
from catalog.modules.catalog.domain.entities import (
	Coordenadas,
	VODireccion,
	VODinero,
	VORegla,
	CategoriaHabitacion,
	Media,
	TipoMedia,
	Propiedad,
	construir_propiedad,
)
from datetime import date

# UUIDs fijos para las pruebas
PROPERTY_UUID = UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479")
CATEGORIA_UUID = UUID("aabbccdd-1111-2222-3333-aabbccdd0001")


@pytest.fixture
def mock_repository():
	"""Repositorio simulado para pruebas unitarias."""
	return Mock()


@pytest.fixture
def mock_event_bus():
	"""Event bus simulado para pruebas unitarias."""
	return Mock()


@pytest.fixture
def property_id():
	"""UUID fijo de propiedad para pruebas."""
	return PROPERTY_UUID


@pytest.fixture
def ubicacion_base():
	"""VODireccion con estado_provincia para reutilizar en fixtures."""
	coords = Coordenadas(lat=10.42, lng=-75.54)
	return VODireccion(ciudad="Cartagena", pais="Colombia", estado_provincia="Bolívar", coordenadas=coords)


@pytest.fixture
def propiedad_base(property_id, ubicacion_base):
	"""Propiedad base sin categorías para reutilizar en pruebas."""
	return construir_propiedad(
		id_propiedad=property_id,
		nombre="Hotel Test",
		estrellas=4,
		ubicacion=ubicacion_base,
		porcentaje_impuesto=Decimal("19.00"),
	)


# ==================== CreateProperty ====================

class TestCreateProperty:
	"""Pruebas para el comando CreateProperty"""

	def test_create_property_success(self, mock_repository, mock_event_bus, property_id):
		"""Verifica que una propiedad nueva se cree correctamente."""
		mock_repository.obtain.return_value = None

		command = CreateProperty(mock_repository, mock_event_bus)
		result = command.execute(
			id_propiedad=property_id,
			nombre="Hotel Test",
			estrellas=4,
			ciudad="Cartagena",
			estado_provincia="Bolívar",
			pais="Colombia",
			latitud=10.42,
			longitud=-75.54,
			porcentaje_impuesto=Decimal("19.00"),
		)

		assert result["nombre"] == "Hotel Test"
		assert result["estrellas"] == 4
		assert result["ubicacion"]["estado_provincia"] == "Bolívar"
		assert result["event_generated"] == "PropiedadCreada"
		assert mock_repository.save.called
		assert mock_event_bus.publish_event.called

	def test_create_property_already_exists(self, mock_repository, mock_event_bus, property_id, propiedad_base):
		"""Verifica que crear una propiedad duplicada retorne mensaje de existencia."""
		mock_repository.obtain.return_value = propiedad_base

		command = CreateProperty(mock_repository, mock_event_bus)
		result = command.execute(
			id_propiedad=property_id,
			nombre="Hotel Test",
			estrellas=4,
			ciudad="Cartagena",
			estado_provincia="Bolívar",
			pais="Colombia",
			latitud=10.42,
			longitud=-75.54,
			porcentaje_impuesto=Decimal("19.00"),
		)

		assert result["message"] == "Property already exists"
		assert not mock_repository.save.called

	def test_create_property_evento_contiene_estado_provincia(self, mock_repository, mock_event_bus, property_id):
		"""Verifica que el evento publicado contiene estado_provincia."""
		mock_repository.obtain.return_value = None

		command = CreateProperty(mock_repository, mock_event_bus)
		command.execute(
			id_propiedad=property_id,
			nombre="Hotel Test",
			estrellas=4,
			ciudad="Cartagena",
			estado_provincia="Bolívar",
			pais="Colombia",
			latitud=10.42,
			longitud=-75.54,
			porcentaje_impuesto=Decimal("19.00"),
		)

		# Verificar que publish_event fue llamado con payload que incluye estado_provincia
		call_kwargs = mock_event_bus.publish_event.call_args[1]
		payload = call_kwargs["payload"]
		assert payload["estado_provincia"] == "Bolívar"


# ==================== RegisterCategoryHousing ====================

class TestRegisterCategoryHousing:
	"""Pruebas para el comando RegisterCategoryHousing"""

	def test_register_category_success(self, mock_repository, mock_event_bus, property_id, propiedad_base):
		"""Verifica que una categoría nueva se registre correctamente."""
		mock_repository.obtain.return_value = propiedad_base

		command = RegisterCategoryHousing(mock_repository, mock_event_bus)
		result = command.execute(
			id_propiedad=property_id,
			codigo_mapeo_pms="ROOM-DLX-01",
			nombre_comercial="Habitación Deluxe",
			descripcion="Habitación de lujo",
			monto_precio_base=Decimal("350000.00"),
			cargo_servicio=Decimal("25000.00"),
			moneda_precio_base="COP",
			capacidad_pax=4,
			dias_anticipacion=5,
			porcentaje_penalidad=Decimal("50.0"),
			foto_portada_url="https://cdn.example.com/deluxe-portada.jpg",
		)

		assert result["id_categoria"]
		# Verificar que id_categoria es un UUID string válido
		uuid.UUID(result["id_categoria"])
		assert result["foto_portada_url"] == "https://cdn.example.com/deluxe-portada.jpg"
		assert result["precio_base"]["cargo_servicio"] == "25000.00"
		assert result["event_generated"] == "CategoriaHabitacionRegistrada"
		assert mock_repository.save.called
		assert mock_event_bus.publish_event.called

	def test_register_category_property_not_found(self, mock_repository, mock_event_bus, property_id):
		"""Verifica que registrar en propiedad inexistente retorne error."""
		mock_repository.obtain.return_value = None

		command = RegisterCategoryHousing(mock_repository, mock_event_bus)
		result = command.execute(
			id_propiedad=property_id,
			codigo_mapeo_pms="ROOM-DLX-01",
			nombre_comercial="Habitación Deluxe",
			descripcion="Habitación de lujo",
			monto_precio_base=Decimal("350000.00"),
			cargo_servicio=Decimal("25000.00"),
			moneda_precio_base="COP",
			capacidad_pax=4,
			dias_anticipacion=5,
			porcentaje_penalidad=Decimal("50.0"),
			foto_portada_url="https://cdn.example.com/deluxe-portada.jpg",
		)

		assert result["error"] == "Property not found"
		assert not mock_repository.save.called

	def test_register_category_already_exists(self, mock_repository, mock_event_bus, property_id, monkeypatch, ubicacion_base):
		"""Verifica que registrar una categoría duplicada retorne mensaje de existencia."""
		# Crear propiedad con categoría existente con UUID fijo
		precio = VODinero(monto=Decimal("350000.00"), moneda="COP")
		regla = VORegla(dias_anticipacion=5, porcentaje_penalidad=Decimal("50.0"))
		categoria = CategoriaHabitacion(
			id_categoria=CATEGORIA_UUID,
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
			ubicacion=ubicacion_base,
			porcentaje_impuesto=Decimal("19.00"),
			categorias_habitacion=[categoria],
		)
		mock_repository.obtain.return_value = propiedad
		# Forzar que uuid4() retorne el mismo UUID que ya existe
		monkeypatch.setattr(
			"catalog.modules.catalog.application.commands.register_category_housing.uuid.uuid4",
			lambda: CATEGORIA_UUID,
		)

		command = RegisterCategoryHousing(mock_repository, mock_event_bus)
		result = command.execute(
			id_propiedad=property_id,
			codigo_mapeo_pms="ROOM-DLX-01",
			nombre_comercial="Habitación Deluxe",
			descripcion="Habitación de lujo",
			monto_precio_base=Decimal("350000.00"),
			cargo_servicio=Decimal("25000.00"),
			moneda_precio_base="COP",
			capacidad_pax=4,
			dias_anticipacion=5,
			porcentaje_penalidad=Decimal("50.0"),
			foto_portada_url="https://cdn.example.com/deluxe-portada.jpg",
		)

		assert result["message"] == "Category already registered"
		assert result["id_categoria"] == str(CATEGORIA_UUID)
		assert not mock_repository.save.called


# ==================== UpdateInventory ====================

class TestUpdateInventory:
	"""Pruebas para el comando UpdateInventory"""

	def _propiedad_con_categoria(self, property_id, ubicacion_base) -> Propiedad:
		"""Helper: crea propiedad con una categoría."""
		precio = VODinero(monto=Decimal("350000.00"), moneda="COP")
		regla = VORegla(dias_anticipacion=5, porcentaje_penalidad=Decimal("50.0"))
		categoria = CategoriaHabitacion(
			id_categoria=CATEGORIA_UUID,
			codigo_mapeo_pms="ROOM-DLX-01",
			nombre_comercial="Habitación Deluxe",
			descripcion="Habitación de lujo",
			precio_base=precio,
			capacidad_pax=4,
			politica_cancelacion=regla,
		)
		return construir_propiedad(
			id_propiedad=property_id,
			nombre="Hotel Test",
			estrellas=4,
			ubicacion=ubicacion_base,
			porcentaje_impuesto=Decimal("19.00"),
			categorias_habitacion=[categoria],
		)

	def test_update_inventory_success(self, mock_repository, mock_event_bus, property_id, ubicacion_base):
		"""Verifica que el inventario se actualice correctamente."""
		propiedad = self._propiedad_con_categoria(property_id, ubicacion_base)
		mock_repository.obtain.return_value = propiedad

		command = UpdateInventory(mock_repository, mock_event_bus)
		result = command.execute(
			id_propiedad=property_id,
			id_categoria=CATEGORIA_UUID,
			id_inventario="inv-2026-05-10",
			fecha=date(2026, 5, 10),
			cupos_totales=10,
			cupos_disponibles=3,
		)

		assert result["cupos_disponibles"] == 3
		assert result["id_categoria"] == str(CATEGORIA_UUID)
		assert result["event_generated"] == "InventarioActualizado"
		assert mock_repository.save.called
		assert mock_event_bus.publish_event.called

	def test_update_inventory_property_not_found(self, mock_repository, mock_event_bus, property_id):
		"""Verifica que actualizar inventario en propiedad inexistente retorne error."""
		mock_repository.obtain.return_value = None

		command = UpdateInventory(mock_repository, mock_event_bus)
		result = command.execute(
			id_propiedad=property_id,
			id_categoria=CATEGORIA_UUID,
			id_inventario="inv-2026-05-10",
			fecha=date(2026, 5, 10),
			cupos_totales=10,
			cupos_disponibles=3,
		)

		assert result["error"] == "Property not found"
		assert not mock_repository.save.called

	def test_update_inventory_category_not_found(self, mock_repository, mock_event_bus, property_id, propiedad_base):
		"""Verifica que actualizar inventario en categoría inexistente retorne error."""
		mock_repository.obtain.return_value = propiedad_base

		command = UpdateInventory(mock_repository, mock_event_bus)
		result = command.execute(
			id_propiedad=property_id,
			id_categoria=UUID("00000000-0000-0000-0000-000000000000"),
			id_inventario="inv-2026-05-10",
			fecha=date(2026, 5, 10),
			cupos_totales=10,
			cupos_disponibles=3,
		)

		assert result["error"] == "Category not found"
		assert not mock_repository.save.called


# ==================== ObtainPropertyByCategoryId ====================

class TestObtainPropertyByCategoryId:
	"""Pruebas para el comando ObtainPropertyByCategoryId"""

	def test_obtain_property_by_category_id_success(self, mock_repository, ubicacion_base):
		"""Verifica que se obtenga la propiedad por id de categoría."""
		propiedad = construir_propiedad(
			id_propiedad=PROPERTY_UUID,
			nombre="Hotel Test",
			estrellas=4,
			ubicacion=ubicacion_base,
			porcentaje_impuesto=Decimal("19.00"),
		)
		mock_repository.obtain_by_category_id.return_value = propiedad

		command = ObtainPropertyByCategoryId(mock_repository)
		result = command.execute(CATEGORIA_UUID)

		assert result["id_categoria"] == str(CATEGORIA_UUID)
		assert result["id_propiedad"] == str(PROPERTY_UUID)
		assert result["nombre"] == "Hotel Test"
		assert result["ubicacion"]["estado_provincia"] == "Bolívar"

	def test_obtain_property_by_category_id_not_found(self, mock_repository):
		"""Verifica que categoría inexistente retorne error."""
		mock_repository.obtain_by_category_id.return_value = None

		command = ObtainPropertyByCategoryId(mock_repository)
		result = command.execute(UUID("00000000-0000-0000-0000-000000000099"))

		assert result["error"] == "Property not found for category"
		assert result["id_categoria"] == "00000000-0000-0000-0000-000000000099"


# ==================== ObtainCategoryById ====================

class TestObtainCategoryById:
	"""Pruebas para el comando ObtainCategoryById"""

	def test_obtain_category_by_id_success(self, mock_repository):
		"""Verifica que se obtenga la categoría por su UUID."""
		precio = VODinero(monto=Decimal("350000.00"), moneda="COP", cargo_servicio=Decimal("25000.00"))
		regla = VORegla(dias_anticipacion=5, porcentaje_penalidad=Decimal("50.0"))
		categoria = CategoriaHabitacion(
			id_categoria=CATEGORIA_UUID,
			codigo_mapeo_pms="ROOM-DLX-01",
			nombre_comercial="Habitación Deluxe",
			descripcion="Habitación de lujo",
			precio_base=precio,
			capacidad_pax=4,
			politica_cancelacion=regla,
			media=[
				Media(
					id_media=f"{str(CATEGORIA_UUID)}-foto-portada",
					url_full="https://cdn.example.com/deluxe-portada.jpg",
					tipo=TipoMedia.FOTO_PORTADA,
					orden=1,
				)
			],
		)
		mock_repository.obtain_category_by_id.return_value = categoria

		command = ObtainCategoryById(mock_repository)
		result = command.execute(CATEGORIA_UUID)

		assert result["id_categoria"] == str(CATEGORIA_UUID)
		assert result["codigo_mapeo_pms"] == "ROOM-DLX-01"
		assert result["precio_base"]["moneda"] == "COP"
		assert result["precio_base"]["cargo_servicio"] == "25000.00"
		assert result["foto_portada_url"] == "https://cdn.example.com/deluxe-portada.jpg"

	def test_obtain_category_by_id_not_found(self, mock_repository):
		"""Verifica que categoría inexistente retorne error."""
		mock_repository.obtain_category_by_id.return_value = None

		command = ObtainCategoryById(mock_repository)
		result = command.execute(UUID("00000000-0000-0000-0000-000000000099"))

		assert result["error"] == "Category not found"
		assert result["id_categoria"] == "00000000-0000-0000-0000-000000000099"


# ==================== ObtainCategoriesByPropertyId ====================

class TestObtainCategoriesByPropertyId:
	"""Pruebas para el comando ObtainCategoriesByPropertyId"""

	def test_obtain_categories_by_property_id_success(self, mock_repository, mock_event_bus, ubicacion_base):
		"""Verifica que se obtengan todas las categorías de una propiedad."""
		precio = VODinero(monto=Decimal("350000.00"), moneda="COP", cargo_servicio=Decimal("25000.00"))
		regla = VORegla(dias_anticipacion=5, porcentaje_penalidad=Decimal("50.0"))
		categoria = CategoriaHabitacion(
			id_categoria=CATEGORIA_UUID,
			codigo_mapeo_pms="ROOM-DLX-01",
			nombre_comercial="Habitación Deluxe",
			descripcion="Habitación de lujo",
			precio_base=precio,
			capacidad_pax=4,
			politica_cancelacion=regla,
			media=[
				Media(
					id_media=f"{str(CATEGORIA_UUID)}-foto-portada",
					url_full="https://cdn.example.com/deluxe-portada.jpg",
					tipo=TipoMedia.FOTO_PORTADA,
					orden=1,
				)
			],
		)
		propiedad = construir_propiedad(
			id_propiedad=PROPERTY_UUID,
			nombre="Hotel Test",
			estrellas=4,
			ubicacion=ubicacion_base,
			porcentaje_impuesto=Decimal("19.00"),
			categorias_habitacion=[categoria],
		)
		mock_repository.obtain.return_value = propiedad

		command = ObtainCategoriesByPropertyId(mock_repository, mock_event_bus)
		result = command.execute(PROPERTY_UUID)

		assert result["id_propiedad"] == str(PROPERTY_UUID)
		assert result["total_categorias"] == 1
		assert result["categorias"][0]["id_categoria"] == str(CATEGORIA_UUID)
		assert result["categorias"][0]["foto_portada_url"] == "https://cdn.example.com/deluxe-portada.jpg"
		assert result["categorias"][0]["precio_base"]["cargo_servicio"] == "25000.00"
		assert result["event_generated"] == "CategoriasPropiedadConsultadas"
		assert mock_event_bus.publish_event.called

	def test_obtain_categories_by_property_id_not_found(self, mock_repository, mock_event_bus):
		"""Verifica que propiedad inexistente retorne error."""
		mock_repository.obtain.return_value = None

		command = ObtainCategoriesByPropertyId(mock_repository, mock_event_bus)
		result = command.execute(PROPERTY_UUID)

		assert result["error"] == "Property not found"
		assert result["id_propiedad"] == str(PROPERTY_UUID)
		assert not mock_event_bus.publish_event.called


# ==================== Eventos de Dominio ====================

class TestEventos:
	"""Pruebas para los eventos de dominio y su serialización."""

	def test_propiedad_creada_to_dict_serializa_correctamente(self):
		"""Verifica que to_dict() serialice UUID y Decimal a strings."""
		from catalog.modules.catalog.domain.events import PropiedadCreada
		from decimal import Decimal

		evento = PropiedadCreada(
			id_propiedad=PROPERTY_UUID,
			nombre="Hotel Test",
			estrellas=4,
			ciudad="Cartagena",
			estado_provincia="Bolívar",
			pais="Colombia",
			porcentaje_impuesto=Decimal("19.00"),
		)
		d = evento.to_dict()

		# UUID debe ser string en el dict
		assert isinstance(d["id_propiedad"], str)
		assert d["id_propiedad"] == str(PROPERTY_UUID)
		# Decimal debe ser string en el dict
		assert isinstance(d["porcentaje_impuesto"], str)
		assert d["estado_provincia"] == "Bolívar"

	def test_categoria_registrada_to_dict_serializa_id_categoria(self):
		"""Verifica que to_dict() serialice id_categoria UUID a string."""
		from catalog.modules.catalog.domain.events import CategoriaHabitacionRegistrada

		evento = CategoriaHabitacionRegistrada(
			id_propiedad=PROPERTY_UUID,
			id_categoria=CATEGORIA_UUID,
			nombre_comercial="Deluxe",
			codigo_mapeo_pms="ROOM-DLX-01",
		)
		d = evento.to_dict()

		assert isinstance(d["id_categoria"], str)
		assert d["id_categoria"] == str(CATEGORIA_UUID)
