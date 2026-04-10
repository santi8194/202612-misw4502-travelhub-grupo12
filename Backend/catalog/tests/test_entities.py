import pytest
from decimal import Decimal
from catalog.modules.catalog.domain.entities import (
	Coordenadas,
	VODireccion,
	VODinero,
	VORegla,
	Media,
	Amenidad,
	Inventario,
	CategoriaHabitacion,
)


class TestCoordenadas:
	"""Pruebas para el value object Coordenadas"""

	def test_coordenadas_validas(self):
		coords = Coordenadas(lat=10.42, lng=-75.54)
		assert coords.lat == 10.42
		assert coords.lng == -75.54

	def test_coordenadas_latitud_invalida(self):
		with pytest.raises(ValueError, match="latitud debe estar entre -90 y 90"):
			Coordenadas(lat=95, lng=-75.54)

	def test_coordenadas_longitud_invalida(self):
		with pytest.raises(ValueError, match="longitud debe estar entre -180 y 180"):
			Coordenadas(lat=10.42, lng=200)


class TestVODireccion:
	"""Pruebas para el value object VODireccion"""

	def test_direccion_valida(self):
		coords = Coordenadas(lat=10.42, lng=-75.54)
		direccion = VODireccion(ciudad="Cartagena", pais="Colombia", coordenadas=coords)
		assert direccion.ciudad == "Cartagena"
		assert direccion.pais == "Colombia"

	def test_direccion_ciudad_vacia(self):
		coords = Coordenadas(lat=10.42, lng=-75.54)
		with pytest.raises(ValueError, match="ciudad es obligatoria"):
			VODireccion(ciudad="", pais="Colombia", coordenadas=coords)

	def test_direccion_pais_vacio(self):
		coords = Coordenadas(lat=10.42, lng=-75.54)
		with pytest.raises(ValueError, match="pais es obligatorio"):
			VODireccion(ciudad="Cartagena", pais="", coordenadas=coords)


class TestVODinero:
	"""Pruebas para el value object VODinero"""

	def test_dinero_valido(self):
		dinero = VODinero(monto=Decimal("350000.00"), moneda="COP")
		assert dinero.monto == Decimal("350000.00")
		assert dinero.moneda == "COP"

	def test_dinero_monto_negativo(self):
		with pytest.raises(ValueError, match="monto debe ser mayor a cero"):
			VODinero(monto=Decimal("-100.00"), moneda="COP")

	def test_dinero_moneda_invalida(self):
		with pytest.raises(ValueError, match="moneda debe tener 3 caracteres"):
			VODinero(monto=Decimal("350000.00"), moneda="CO")

	def test_dinero_moneda_normalizada(self):
		dinero = VODinero(monto=Decimal("350000.00"), moneda="cop")
		assert dinero.moneda == "COP"


class TestVORegla:
	"""Pruebas para el value object VORegla"""

	def test_regla_valida(self):
		regla = VORegla(dias_anticipacion=5, porcentaje_penalidad=Decimal("50.0"))
		assert regla.dias_anticipacion == 5
		assert regla.porcentaje_penalidad == Decimal("50.00")

	def test_regla_dias_negativo(self):
		with pytest.raises(ValueError, match="dias de anticipacion no pueden ser negativos"):
			VORegla(dias_anticipacion=-1, porcentaje_penalidad=Decimal("50.0"))

	def test_regla_penalidad_fuera_rango(self):
		with pytest.raises(ValueError, match="penalidad debe estar entre 0 y 100"):
			VORegla(dias_anticipacion=5, porcentaje_penalidad=Decimal("150.0"))


class TestMedia:
	"""Pruebas para la entidad Media"""

	def test_media_valida(self):
		from catalog.modules.catalog.domain.entities import TipoMedia
		media = Media(
			id_media="media-001",
			url_full="https://cdn.example.com/hotel.jpg",
			tipo=TipoMedia.FOTO_PORTADA,
			orden=1,
		)
		assert media.id_media == "media-001"

	def test_media_url_invalida(self):
		from catalog.modules.catalog.domain.entities import TipoMedia
		with pytest.raises(ValueError, match="URL del recurso multimedia debe ser valida"):
			Media(
				id_media="media-001",
				url_full="invalid-url",
				tipo=TipoMedia.FOTO_PORTADA,
				orden=1,
			)

	def test_media_orden_invalido(self):
		from catalog.modules.catalog.domain.entities import TipoMedia
		with pytest.raises(ValueError, match="orden de la media debe ser mayor"):
			Media(
				id_media="media-001",
				url_full="https://cdn.example.com/hotel.jpg",
				tipo=TipoMedia.FOTO_PORTADA,
				orden=0,
			)


class TestAmenidad:
	"""Pruebas para la entidad Amenidad"""

	def test_amenidad_valida(self):
		amenidad = Amenidad(
			id_amenidad="am-001",
			nombre="Aire Acondicionado",
			icono="fa-snowflake",
		)
		assert amenidad.nombre == "Aire Acondicionado"

	def test_amenidad_nombre_vacio(self):
		with pytest.raises(ValueError, match="nombre de la amenidad es obligatorio"):
			Amenidad(id_amenidad="am-001", nombre="", icono="fa-snowflake")


class TestInventario:
	"""Pruebas para la entidad Inventario"""

	def test_inventario_valido(self):
		from datetime import date
		inventario = Inventario(
			id_inventario="inv-001",
			fecha=date(2026, 5, 10),
			cupos_totales=10,
			cupos_disponibles=3,
		)
		assert inventario.cupos_disponibles == 3

	def test_inventario_cupos_invalidos(self):
		from datetime import date
		with pytest.raises(ValueError, match="cupos disponibles no pueden superar los cupos totales"):
			Inventario(
				id_inventario="inv-001",
				fecha=date(2026, 5, 10),
				cupos_totales=10,
				cupos_disponibles=15,
			)


class TestCategoriaHabitacion:
	"""Pruebas para la entidad CategoriaHabitacion"""

	def test_categoria_valida(self):
		precio = VODinero(monto=Decimal("350000.00"), moneda="COP")
		regla = VORegla(dias_anticipacion=5, porcentaje_penalidad=Decimal("50.0"))

		categoria = CategoriaHabitacion(
			id_categoria="cat-001",
			codigo_mapeo_pms="ROOM-DLX-01",
			nombre_comercial="Deluxe Room",
			descripcion="Habitación de lujo",
			precio_base=precio,
			capacidad_pax=4,
			politica_cancelacion=regla,
		)
		assert categoria.nombre_comercial == "Deluxe Room"

	def test_categoria_capacidad_invalida(self):
		precio = VODinero(monto=Decimal("350000.00"), moneda="COP")
		regla = VORegla(dias_anticipacion=5, porcentaje_penalidad=Decimal("50.0"))

		with pytest.raises(ValueError, match="capacidad de pasajeros debe ser mayor a cero"):
			CategoriaHabitacion(
				id_categoria="cat-001",
				codigo_mapeo_pms="ROOM-DLX-01",
				nombre_comercial="Deluxe Room",
				descripcion="Habitación de lujo",
				precio_base=precio,
				capacidad_pax=0,
				politica_cancelacion=regla,
			)

	def test_actualizar_inventario(self):
		from datetime import date

		precio = VODinero(monto=Decimal("350000.00"), moneda="COP")
		regla = VORegla(dias_anticipacion=5, porcentaje_penalidad=Decimal("50.0"))

		categoria = CategoriaHabitacion(
			id_categoria="cat-001",
			codigo_mapeo_pms="ROOM-DLX-01",
			nombre_comercial="Deluxe Room",
			descripcion="Habitación de lujo",
			precio_base=precio,
			capacidad_pax=4,
			politica_cancelacion=regla,
		)

		inventario = Inventario(
			id_inventario="inv-001",
			fecha=date(2026, 5, 10),
			cupos_totales=10,
			cupos_disponibles=5,
		)

		resultado = categoria.actualizar_inventario(inventario)
		assert resultado.cupos_disponibles == 5
		assert len(categoria.inventario) == 1

	def test_disponibilidad_para(self):
		from datetime import date

		precio = VODinero(monto=Decimal("350000.00"), moneda="COP")
		regla = VORegla(dias_anticipacion=5, porcentaje_penalidad=Decimal("50.0"))

		categoria = CategoriaHabitacion(
			id_categoria="cat-001",
			codigo_mapeo_pms="ROOM-DLX-01",
			nombre_comercial="Deluxe Room",
			descripcion="Habitación de lujo",
			precio_base=precio,
			capacidad_pax=4,
			politica_cancelacion=regla,
		)

		inventario = Inventario(
			id_inventario="inv-001",
			fecha=date(2026, 5, 10),
			cupos_totales=10,
			cupos_disponibles=5,
		)

		categoria.actualizar_inventario(inventario)

		resultado = categoria.disponibilidad_para(date(2026, 5, 10))
		assert resultado is not None
		assert resultado.cupos_disponibles == 5

		resultado_no_existe = categoria.disponibilidad_para(date(2026, 5, 11))
		assert resultado_no_existe is None
