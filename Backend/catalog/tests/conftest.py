import pytest
from decimal import Decimal
from uuid import UUID
from datetime import date
from catalog.modules.catalog.domain.entities import (
	Coordenadas,
	VODireccion,
	VODinero,
	VORegla,
	CategoriaHabitacion,
	Inventario,
	Propiedad,
	construir_propiedad,
)


@pytest.fixture
def property_id():
	"""UUID de propiedad para pruebas"""
	return UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479")


@pytest.fixture
def coordenadas_test():
	"""Coordenadas válidas para pruebas"""
	return Coordenadas(lat=10.42, lng=-75.54)


@pytest.fixture
def ubicacion_test(coordenadas_test):
	"""Ubicación válida para pruebas"""
	return VODireccion(
		ciudad="Cartagena",
		pais="Colombia",
		coordenadas=coordenadas_test,
	)


@pytest.fixture
def dinero_test():
	"""Dinero válido para pruebas"""
	return VODinero(monto=Decimal("350000.00"), moneda="COP")


@pytest.fixture
def regla_cancelacion_test():
	"""Política de cancelación válida para pruebas"""
	return VORegla(
		dias_anticipacion=5,
		porcentaje_penalidad=Decimal("50.0"),
	)


@pytest.fixture
def categoria_test(dinero_test, regla_cancelacion_test):
	"""Categoría de habitación válida para pruebas"""
	return CategoriaHabitacion(
		id_categoria="deluxe-001",
		codigo_mapeo_pms="ROOM-DLX-01",
		nombre_comercial="Habitación Deluxe",
		descripcion="Habitación de lujo con vista al mar",
		precio_base=dinero_test,
		capacidad_pax=4,
		politica_cancelacion=regla_cancelacion_test,
	)


@pytest.fixture
def inventario_test():
	"""Inventario válido para pruebas"""
	return Inventario(
		id_inventario="inv-2026-05-10",
		fecha=date(2026, 5, 10),
		cupos_totales=10,
		cupos_disponibles=5,
	)


@pytest.fixture
def propiedad_test(property_id, ubicacion_test, categoria_test):
	"""Propiedad válida para pruebas"""
	return construir_propiedad(
		id_propiedad=property_id,
		nombre="Hotel Boutique Las Palmas",
		estrellas=4,
		ubicacion=ubicacion_test,
		porcentaje_impuesto=Decimal("19.00"),
		categorias_habitacion=[categoria_test],
	)


@pytest.fixture
def propiedad_sin_categorias(property_id, ubicacion_test):
	"""Propiedad sin categorías para pruebas"""
	return construir_propiedad(
		id_propiedad=property_id,
		nombre="Hotel Test",
		estrellas=3,
		ubicacion=ubicacion_test,
		porcentaje_impuesto=Decimal("16.00"),
	)
