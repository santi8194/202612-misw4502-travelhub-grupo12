import pytest
from decimal import Decimal
from uuid import UUID
from catalog.modules.catalog.domain.entities import (
	Coordenadas,
	VODireccion,
	VODinero,
	VORegla,
	Media,
	Amenidad,
	Inventario,
	CategoriaHabitacion,
	Propiedad,
	construir_propiedad,
	TipoMedia,
)


# ==================== Coordenadas ====================

class TestCoordenadas:
	"""Pruebas para el value object Coordenadas"""

	def test_coordenadas_validas(self):
		"""Verifica que coordenadas dentro del rango sean aceptadas."""
		coords = Coordenadas(lat=10.42, lng=-75.54)
		assert coords.lat == 10.42
		assert coords.lng == -75.54

	def test_coordenadas_latitud_invalida(self):
		"""Verifica que latitud fuera de rango lance error."""
		with pytest.raises(ValueError, match="latitud debe estar entre -90 y 90"):
			Coordenadas(lat=95, lng=-75.54)

	def test_coordenadas_longitud_invalida(self):
		"""Verifica que longitud fuera de rango lance error."""
		with pytest.raises(ValueError, match="longitud debe estar entre -180 y 180"):
			Coordenadas(lat=10.42, lng=200)


# ==================== VODireccion ====================

class TestVODireccion:
	"""Pruebas para el value object VODireccion"""

	def test_direccion_valida(self):
		"""Verifica que una dirección completa sea aceptada."""
		coords = Coordenadas(lat=10.42, lng=-75.54)
		direccion = VODireccion(ciudad="Cartagena", pais="Colombia", estado_provincia="Bolívar", coordenadas=coords)
		assert direccion.ciudad == "Cartagena"
		assert direccion.pais == "Colombia"
		assert direccion.estado_provincia == "Bolívar"

	def test_direccion_ciudad_vacia(self):
		"""Verifica que una ciudad vacía lance error."""
		coords = Coordenadas(lat=10.42, lng=-75.54)
		with pytest.raises(ValueError, match="ciudad es obligatoria"):
			VODireccion(ciudad="", pais="Colombia", estado_provincia="Bolívar", coordenadas=coords)

	def test_direccion_pais_vacio(self):
		"""Verifica que un país vacío lance error."""
		coords = Coordenadas(lat=10.42, lng=-75.54)
		with pytest.raises(ValueError, match="pais es obligatorio"):
			VODireccion(ciudad="Cartagena", pais="", estado_provincia="Bolívar", coordenadas=coords)

	def test_direccion_estado_provincia_vacio(self):
		"""Verifica que estado_provincia vacío lance error."""
		coords = Coordenadas(lat=10.42, lng=-75.54)
		with pytest.raises(ValueError, match="estado/provincia es obligatorio"):
			VODireccion(ciudad="Cartagena", pais="Colombia", estado_provincia="", coordenadas=coords)


# ==================== VODinero ====================

class TestVODinero:
	"""Pruebas para el value object VODinero"""

	def test_dinero_valido(self):
		"""Verifica que un dinero con valores correctos sea aceptado."""
		dinero = VODinero(monto=Decimal("350000.00"), moneda="COP", cargo_servicio=Decimal("25000.00"))
		assert dinero.monto == Decimal("350000.00")
		assert dinero.moneda == "COP"
		assert dinero.cargo_servicio == Decimal("25000.00")

	def test_dinero_monto_negativo(self):
		"""Verifica que un monto negativo lance error."""
		with pytest.raises(ValueError, match="monto debe ser mayor a cero"):
			VODinero(monto=Decimal("-100.00"), moneda="COP")

	def test_dinero_moneda_invalida(self):
		"""Verifica que una moneda con menos de 3 caracteres lance error."""
		with pytest.raises(ValueError, match="moneda debe tener 3 caracteres"):
			VODinero(monto=Decimal("350000.00"), moneda="CO")

	def test_dinero_moneda_normalizada(self):
		"""Verifica que la moneda sea normalizada a mayúsculas."""
		dinero = VODinero(monto=Decimal("350000.00"), moneda="cop")
		assert dinero.moneda == "COP"

	def test_dinero_cargo_servicio_por_defecto(self):
		"""Verifica que el cargo de servicio por defecto sea cero."""
		dinero = VODinero(monto=Decimal("350000.00"), moneda="COP")
		assert dinero.cargo_servicio == Decimal("0.00")

	def test_dinero_cargo_servicio_negativo(self):
		"""Verifica que un cargo de servicio negativo lance error."""
		with pytest.raises(ValueError, match="cargo por servicio no puede ser negativo"):
			VODinero(monto=Decimal("350000.00"), moneda="COP", cargo_servicio=Decimal("-1.00"))


# ==================== VORegla ====================

class TestVORegla:
	"""Pruebas para el value object VORegla"""

	def test_regla_valida(self):
		"""Verifica que una regla con valores correctos sea aceptada."""
		regla = VORegla(dias_anticipacion=5, porcentaje_penalidad=Decimal("50.0"))
		assert regla.dias_anticipacion == 5
		assert regla.porcentaje_penalidad == Decimal("50.00")

	def test_regla_dias_negativo(self):
		"""Verifica que días de anticipación negativos lancen error."""
		with pytest.raises(ValueError, match="dias de anticipacion no pueden ser negativos"):
			VORegla(dias_anticipacion=-1, porcentaje_penalidad=Decimal("50.0"))

	def test_regla_penalidad_fuera_rango(self):
		"""Verifica que una penalidad fuera de rango lance error."""
		with pytest.raises(ValueError, match="penalidad debe estar entre 0 y 100"):
			VORegla(dias_anticipacion=5, porcentaje_penalidad=Decimal("150.0"))


# ==================== Media ====================

class TestMedia:
	"""Pruebas para la entidad Media"""

	def test_media_valida(self):
		"""Verifica que un media con valores correctos sea aceptado."""
		media = Media(
			id_media="media-001",
			url_full="https://cdn.example.com/hotel.jpg",
			tipo=TipoMedia.FOTO_PORTADA,
			orden=1,
		)
		assert media.id_media == "media-001"

	def test_media_orden_invalido(self):
		"""Verifica que un orden menor a 1 lance error."""
		with pytest.raises(ValueError, match="orden de la media debe ser mayor"):
			Media(
				id_media="media-001",
				url_full="https://cdn.example.com/hotel.jpg",
				tipo=TipoMedia.FOTO_PORTADA,
				orden=0,
			)

	def test_media_id_vacio(self):
		"""Verifica que un id_media vacío lance error."""
		with pytest.raises(ValueError, match="ID de media es obligatorio"):
			Media(
				id_media="",
				url_full="https://cdn.example.com/hotel.jpg",
				tipo=TipoMedia.FOTO_PORTADA,
				orden=1,
			)


# ==================== Amenidad ====================

class TestAmenidad:
	"""Pruebas para la entidad Amenidad"""

	def test_amenidad_valida(self):
		"""Verifica que una amenidad con valores correctos sea aceptada."""
		amenidad = Amenidad(
			id_amenidad="am-001",
			nombre="Aire Acondicionado",
			icono="fa-snowflake",
		)
		assert amenidad.nombre == "Aire Acondicionado"

	def test_amenidad_nombre_vacio(self):
		"""Verifica que un nombre vacío lance error."""
		with pytest.raises(ValueError, match="nombre de la amenidad es obligatorio"):
			Amenidad(id_amenidad="am-001", nombre="", icono="fa-snowflake")

	def test_amenidad_icono_vacio(self):
		"""Verifica que un icono vacío lance error."""
		with pytest.raises(ValueError, match="icono de la amenidad es obligatorio"):
			Amenidad(id_amenidad="am-001", nombre="Wifi", icono="")


# ==================== Inventario ====================

class TestInventario:
	"""Pruebas para la entidad Inventario"""

	def test_inventario_valido(self):
		"""Verifica que un inventario con valores correctos sea aceptado."""
		from datetime import date
		inventario = Inventario(
			id_inventario="inv-001",
			fecha=date(2026, 5, 10),
			cupos_totales=10,
			cupos_disponibles=3,
		)
		assert inventario.cupos_disponibles == 3

	def test_inventario_cupos_invalidos(self):
		"""Verifica que cupos disponibles mayores al total lancen error."""
		from datetime import date
		with pytest.raises(ValueError, match="cupos disponibles no pueden superar los cupos totales"):
			Inventario(
				id_inventario="inv-001",
				fecha=date(2026, 5, 10),
				cupos_totales=10,
				cupos_disponibles=15,
			)

	def test_inventario_cupos_negativos(self):
		"""Verifica que cupos negativos lancen error."""
		from datetime import date
		with pytest.raises(ValueError, match="cupos totales no pueden ser negativos"):
			Inventario(
				id_inventario="inv-001",
				fecha=date(2026, 5, 10),
				cupos_totales=-1,
				cupos_disponibles=0,
			)


# ==================== CategoriaHabitacion ====================

class TestCategoriaHabitacion:
	"""Pruebas para la entidad CategoriaHabitacion"""

	def _make_categoria(self, id_categoria_str: str = "f47ac10b-58cc-4372-a567-0e02b2c3d479") -> CategoriaHabitacion:
		"""Helper: crea una categoría válida con UUID."""
		precio = VODinero(monto=Decimal("350000.00"), moneda="COP")
		regla = VORegla(dias_anticipacion=5, porcentaje_penalidad=Decimal("50.0"))
		return CategoriaHabitacion(
			id_categoria=UUID(id_categoria_str),
			codigo_mapeo_pms="ROOM-DLX-01",
			nombre_comercial="Deluxe Room",
			descripcion="Habitación de lujo",
			precio_base=precio,
			capacidad_pax=4,
			politica_cancelacion=regla,
		)

	def test_categoria_valida(self):
		"""Verifica que una categoría con valores correctos sea aceptada."""
		categoria = self._make_categoria()
		assert categoria.nombre_comercial == "Deluxe Room"
		assert isinstance(categoria.id_categoria, UUID)

	def test_categoria_capacidad_invalida(self):
		"""Verifica que una capacidad de pasajeros de cero lance error."""
		precio = VODinero(monto=Decimal("350000.00"), moneda="COP")
		regla = VORegla(dias_anticipacion=5, porcentaje_penalidad=Decimal("50.0"))
		with pytest.raises(ValueError, match="capacidad de pasajeros debe ser mayor a cero"):
			CategoriaHabitacion(
				id_categoria=UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479"),
				codigo_mapeo_pms="ROOM-DLX-01",
				nombre_comercial="Deluxe Room",
				descripcion="Habitación de lujo",
				precio_base=precio,
				capacidad_pax=0,
				politica_cancelacion=regla,
			)

	def test_actualizar_inventario(self):
		"""Verifica que el inventario se actualice correctamente."""
		from datetime import date
		categoria = self._make_categoria()
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
		"""Verifica que la disponibilidad para una fecha sea correcta."""
		from datetime import date
		categoria = self._make_categoria()
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


# ==================== Propiedad ====================

class TestPropiedad:
	"""Pruebas para la entidad Propiedad"""

	def _make_propiedad(self) -> Propiedad:
		"""Helper: crea una propiedad válida."""
		coords = Coordenadas(lat=10.42, lng=-75.54)
		ubicacion = VODireccion(ciudad="Cartagena", pais="Colombia", estado_provincia="Bolívar", coordenadas=coords)
		return construir_propiedad(
			id_propiedad=UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479"),
			nombre="Hotel Test",
			estrellas=4,
			ubicacion=ubicacion,
			porcentaje_impuesto=Decimal("19.00"),
		)

	def _make_categoria(self) -> CategoriaHabitacion:
		"""Helper: crea una categoría válida."""
		precio = VODinero(monto=Decimal("350000.00"), moneda="COP")
		regla = VORegla(dias_anticipacion=5, porcentaje_penalidad=Decimal("50.0"))
		return CategoriaHabitacion(
			id_categoria=UUID("aabbccdd-1111-2222-3333-aabbccdd0001"),
			codigo_mapeo_pms="ROOM-DLX-01",
			nombre_comercial="Deluxe Room",
			descripcion="Habitación de lujo",
			precio_base=precio,
			capacidad_pax=4,
			politica_cancelacion=regla,
		)

	def test_propiedad_valida(self):
		"""Verifica que una propiedad con valores correctos sea aceptada."""
		propiedad = self._make_propiedad()
		assert propiedad.nombre == "Hotel Test"
		assert propiedad.ubicacion.estado_provincia == "Bolívar"

	def test_propiedad_nombre_vacio(self):
		"""Verifica que un nombre vacío lance error."""
		coords = Coordenadas(lat=10.42, lng=-75.54)
		ubicacion = VODireccion(ciudad="Cartagena", pais="Colombia", estado_provincia="Bolívar", coordenadas=coords)
		with pytest.raises(ValueError, match="nombre de la propiedad es obligatorio"):
			Propiedad(
				id_propiedad=UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479"),
				nombre="",
				estrellas=4,
				ubicacion=ubicacion,
				porcentaje_impuesto=Decimal("19.00"),
			)

	def test_propiedad_estrellas_invalidas(self):
		"""Verifica que estrellas fuera de rango lancen error."""
		coords = Coordenadas(lat=10.42, lng=-75.54)
		ubicacion = VODireccion(ciudad="Cartagena", pais="Colombia", estado_provincia="Bolívar", coordenadas=coords)
		with pytest.raises(ValueError, match="estrellas debe estar entre 1 y 5"):
			Propiedad(
				id_propiedad=UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479"),
				nombre="Hotel",
				estrellas=6,
				ubicacion=ubicacion,
				porcentaje_impuesto=Decimal("19.00"),
			)

	def test_registrar_categoria(self):
		"""Verifica que una nueva categoría se registre correctamente."""
		propiedad = self._make_propiedad()
		categoria = self._make_categoria()
		propiedad.registrar_categoria(categoria)
		assert len(propiedad.categorias_habitacion) == 1

	def test_registrar_categoria_duplicada(self):
		"""Verifica que registrar una categoría duplicada lance error."""
		propiedad = self._make_propiedad()
		categoria = self._make_categoria()
		propiedad.registrar_categoria(categoria)
		with pytest.raises(ValueError, match="categoria de habitacion ya existe"):
			propiedad.registrar_categoria(categoria)

	def test_obtener_categoria(self):
		"""Verifica que se pueda obtener una categoría por UUID."""
		propiedad = self._make_propiedad()
		categoria = self._make_categoria()
		propiedad.registrar_categoria(categoria)
		result = propiedad.obtener_categoria(UUID("aabbccdd-1111-2222-3333-aabbccdd0001"))
		assert result is not None
		assert result.nombre_comercial == "Deluxe Room"

	def test_obtener_categoria_inexistente(self):
		"""Verifica que buscar una categoría inexistente retorne None."""
		propiedad = self._make_propiedad()
		result = propiedad.obtener_categoria(UUID("00000000-0000-0000-0000-000000000000"))
		assert result is None
