"""
Pruebas unitarias para ObtainCategoryViewDetail y la entidad Resena.

Cubre la query de detalle de propiedad, la lógica de galería, el cálculo
de rating promedio en el dominio y la validación de la entidad Resena.
Todas las pruebas usan mocks (sin base de datos real).
"""
import pytest
from decimal import Decimal
from uuid import UUID
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock

from catalog.modules.catalog.application.queries.obtain_category_view_detail import (
	ObtainCategoryViewDetail,
)
from catalog.modules.catalog.domain.entities import (
	Coordenadas,
	VODireccion,
	VODinero,
	VORegla,
	CategoriaHabitacion,
	Media,
	TipoMedia,
	Amenidad,
	Resena,
	Propiedad,
	construir_propiedad,
)

# UUIDs fijos para las pruebas
PROPERTY_UUID = UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479")
CATEGORIA_UUID = UUID("aabbccdd-1111-2222-3333-aabbccdd0001")
RESENA_UUID_1 = UUID("11111111-1111-1111-1111-111111111111")
RESENA_UUID_2 = UUID("22222222-2222-2222-2222-222222222222")
USUARIO_UUID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")

# Fecha base para crear reseñas en orden cronológico
FECHA_BASE = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


# ==================== Fixtures ====================


@pytest.fixture
def mock_repository():
	"""Repositorio simulado para pruebas unitarias."""
	return Mock()


@pytest.fixture
def ubicacion_base():
	"""VODireccion válida para pruebas."""
	coords = Coordenadas(lat=44.83, lng=-0.57)
	return VODireccion(
		ciudad="Bordeaux",
		pais="France",
		estado_provincia="Nouvelle-Aquitaine",
		coordenadas=coords,
	)


@pytest.fixture
def categoria_base():
	"""CategoriaHabitacion válida con amenidades y media para pruebas."""
	precio = VODinero(monto=Decimal("75.00"), moneda="USD", cargo_servicio=Decimal("13.00"))
	regla = VORegla(dias_anticipacion=3, porcentaje_penalidad=Decimal("50.00"))
	return CategoriaHabitacion(
		id_categoria=CATEGORIA_UUID,
		codigo_mapeo_pms="SUITE-DLX-01",
		nombre_comercial="Suite Deluxe",
		descripcion="Suite de lujo con vista al río",
		precio_base=precio,
		capacidad_pax=7,
		politica_cancelacion=regla,
		media=[
			Media(
				id_media="media-portada",
				url_full="https://cdn.example.com/portada.jpg",
				tipo=TipoMedia.FOTO_PORTADA,
				orden=1,
			),
			Media(
				id_media="media-galeria-1",
				url_full="https://cdn.example.com/sala.jpg",
				tipo=TipoMedia.IMAGEN_GALERIA,
				orden=2,
			),
		],
		amenidades=[
			Amenidad(id_amenidad="amen-wifi", nombre="WiFi", icono="wifi"),
			Amenidad(id_amenidad="amen-cocina", nombre="Cocina", icono="kitchen"),
		],
	)


def _crear_resena(id_resena: UUID, calificacion: int, dias_atras: int) -> Resena:
	"""Helper para crear reseñas con fecha relativa al FECHA_BASE."""
	return Resena(
		id_resena=id_resena,
		id_propiedad=PROPERTY_UUID,
		id_usuario=USUARIO_UUID,
		nombre_autor="Autor Test",
		avatar_url="https://cdn.example.com/avatar.jpg",
		calificacion=calificacion,
		comentario="Comentario de prueba muy detallado",
		fecha_creacion=FECHA_BASE - timedelta(days=dias_atras),
	)


@pytest.fixture
def propiedad_con_resenas(ubicacion_base):
	"""Propiedad con 3 reseñas de calificaciones distintas."""
	resenas = [
		_crear_resena(UUID("11111111-1111-1111-1111-111111111111"), calificacion=5, dias_atras=1),
		_crear_resena(UUID("22222222-2222-2222-2222-222222222222"), calificacion=4, dias_atras=2),
		_crear_resena(UUID("33333333-3333-3333-3333-333333333333"), calificacion=3, dias_atras=3),
	]
	return construir_propiedad(
		id_propiedad=PROPERTY_UUID,
		nombre="Bordeaux Getaway",
		estrellas=4,
		ubicacion=ubicacion_base,
		porcentaje_impuesto=Decimal("10.00"),
		resenas=resenas,
	)


@pytest.fixture
def propiedad_sin_resenas(ubicacion_base):
	"""Propiedad sin reseñas para probar rating 0.0."""
	return construir_propiedad(
		id_propiedad=PROPERTY_UUID,
		nombre="Hotel Sin Reseñas",
		estrellas=3,
		ubicacion=ubicacion_base,
		porcentaje_impuesto=Decimal("10.00"),
	)


# ==================== TestObtainCategoryViewDetail ====================


class TestObtainCategoryViewDetail:
	"""Pruebas para la query ObtainCategoryViewDetail."""

	def test_detalle_categoria_exitoso(
		self, mock_repository, propiedad_con_resenas, categoria_base
	):
		"""Verifica que retorna el payload completo cuando la categoría existe."""
		mock_repository.obtain_view_detail.return_value = (
			propiedad_con_resenas,
			categoria_base,
		)

		query = ObtainCategoryViewDetail(mock_repository)
		result = query.execute(CATEGORIA_UUID)

		# Verificar estructura de primer nivel
		assert "propiedad" in result
		assert "categoria" in result
		assert "amenidades" in result
		assert "galeria" in result
		assert "rating_promedio" in result
		assert "total_resenas" in result
		assert "resenas" in result

		# Verificar datos de la propiedad
		assert result["propiedad"]["nombre"] == "Bordeaux Getaway"
		assert result["propiedad"]["id_propiedad"] == str(PROPERTY_UUID)

		# Verificar datos de la categoría
		assert result["categoria"]["id_categoria"] == str(CATEGORIA_UUID)
		assert result["categoria"]["nombre_comercial"] == "Suite Deluxe"

	def test_detalle_categoria_no_encontrada(self, mock_repository):
		"""Verifica que retorna error cuando la categoría no existe."""
		mock_repository.obtain_view_detail.return_value = None

		query = ObtainCategoryViewDetail(mock_repository)
		id_inexistente = UUID("00000000-0000-0000-0000-000000000000")
		result = query.execute(id_inexistente)

		assert result["error"] == "Category not found"
		assert result["id_categoria"] == str(id_inexistente)

	def test_galeria_maximo_10_elementos(
		self, mock_repository, propiedad_sin_resenas, ubicacion_base
	):
		"""Verifica que la galería se trunca a 10 elementos cuando hay más."""
		# Crear categoría con 15 medios
		precio = VODinero(monto=Decimal("75.00"), moneda="USD")
		regla = VORegla(dias_anticipacion=3, porcentaje_penalidad=Decimal("50.00"))
		media_excesiva = [
			Media(id_media=f"media-{i}", url_full=f"https://cdn.example.com/{i}.jpg",
				  tipo=TipoMedia.IMAGEN_GALERIA, orden=i)
			for i in range(1, 16)  # 15 imágenes de galería
		]
		categoria_grande = CategoriaHabitacion(
			id_categoria=CATEGORIA_UUID,
			codigo_mapeo_pms="TEST-001",
			nombre_comercial="Test",
			descripcion="Descripción",
			precio_base=precio,
			capacidad_pax=2,
			politica_cancelacion=regla,
			media=media_excesiva,
		)
		mock_repository.obtain_view_detail.return_value = (
			propiedad_sin_resenas,
			categoria_grande,
		)

		query = ObtainCategoryViewDetail(mock_repository)
		result = query.execute(CATEGORIA_UUID)

		# La galería no debe superar 10 elementos
		assert len(result["galeria"]) == 10

	def test_galeria_portada_siempre_primera(
		self, mock_repository, propiedad_sin_resenas
	):
		"""Verifica que FOTO_PORTADA siempre aparece como primer elemento."""
		precio = VODinero(monto=Decimal("75.00"), moneda="USD")
		regla = VORegla(dias_anticipacion=3, porcentaje_penalidad=Decimal("50.00"))
		# Portada con orden alto (debería aparecer primera de todas formas)
		categoria = CategoriaHabitacion(
			id_categoria=CATEGORIA_UUID,
			codigo_mapeo_pms="TEST-001",
			nombre_comercial="Test",
			descripcion="Descripción",
			precio_base=precio,
			capacidad_pax=2,
			politica_cancelacion=regla,
			media=[
				Media(id_media="galeria-1", url_full="https://cdn.example.com/g1.jpg",
					  tipo=TipoMedia.IMAGEN_GALERIA, orden=1),
				Media(id_media="portada", url_full="https://cdn.example.com/portada.jpg",
					  tipo=TipoMedia.FOTO_PORTADA, orden=2),
			],
		)
		mock_repository.obtain_view_detail.return_value = (propiedad_sin_resenas, categoria)

		query = ObtainCategoryViewDetail(mock_repository)
		result = query.execute(CATEGORIA_UUID)

		# La portada siempre debe ser la primera
		assert result["galeria"][0]["tipo"] == TipoMedia.FOTO_PORTADA.value

	def test_rating_promedio_con_resenas(
		self, mock_repository, propiedad_con_resenas, categoria_base
	):
		"""Verifica que el rating promedio se calcula correctamente."""
		# propiedad_con_resenas tiene calificaciones 5, 4 y 3 → promedio = 4.0
		mock_repository.obtain_view_detail.return_value = (
			propiedad_con_resenas,
			categoria_base,
		)

		query = ObtainCategoryViewDetail(mock_repository)
		result = query.execute(CATEGORIA_UUID)

		assert result["rating_promedio"] == 4.0
		assert result["total_resenas"] == 3

	def test_rating_promedio_sin_resenas(
		self, mock_repository, propiedad_sin_resenas, categoria_base
	):
		"""Verifica que retorna 0.0 cuando la propiedad no tiene reseñas."""
		mock_repository.obtain_view_detail.return_value = (
			propiedad_sin_resenas,
			categoria_base,
		)

		query = ObtainCategoryViewDetail(mock_repository)
		result = query.execute(CATEGORIA_UUID)

		assert result["rating_promedio"] == 0.0
		assert result["total_resenas"] == 0
		assert result["resenas"] == []

	def test_resenas_maximo_10_recientes(self, mock_repository, ubicacion_base, categoria_base):
		"""Verifica que solo se retornan las 10 reseñas más recientes cuando hay más de 10."""
		# Crear 15 reseñas con distintas fechas
		resenas_15 = [
			_crear_resena(
				UUID(f"0000{i:04d}-0000-0000-0000-000000000000"),
				calificacion=4,
				dias_atras=i,
			)
			for i in range(1, 16)
		]
		propiedad = construir_propiedad(
			id_propiedad=PROPERTY_UUID,
			nombre="Hotel Muchas Reseñas",
			estrellas=4,
			ubicacion=ubicacion_base,
			porcentaje_impuesto=Decimal("10.00"),
			resenas=resenas_15,
		)
		mock_repository.obtain_view_detail.return_value = (propiedad, categoria_base)

		query = ObtainCategoryViewDetail(mock_repository)
		result = query.execute(CATEGORIA_UUID)

		# Máximo 10 reseñas en la respuesta, aunque total_resenas muestra el real
		assert len(result["resenas"]) == 10
		assert result["total_resenas"] == 15

	def test_resenas_orden_descendente(self, mock_repository, ubicacion_base, categoria_base):
		"""Verifica que las reseñas se ordenan de más reciente a más antigua."""
		resenas = [
			_crear_resena(UUID("11111111-1111-1111-1111-111111111111"), calificacion=5, dias_atras=3),
			_crear_resena(UUID("22222222-2222-2222-2222-222222222222"), calificacion=4, dias_atras=1),
			_crear_resena(UUID("33333333-3333-3333-3333-333333333333"), calificacion=3, dias_atras=2),
		]
		propiedad = construir_propiedad(
			id_propiedad=PROPERTY_UUID,
			nombre="Hotel Test",
			estrellas=4,
			ubicacion=ubicacion_base,
			porcentaje_impuesto=Decimal("10.00"),
			resenas=resenas,
		)
		mock_repository.obtain_view_detail.return_value = (propiedad, categoria_base)

		query = ObtainCategoryViewDetail(mock_repository)
		result = query.execute(CATEGORIA_UUID)

		# La más reciente (1 día atrás) debe ser la primera
		fechas = [r["fecha_creacion"] for r in result["resenas"]]
		assert fechas == sorted(fechas, reverse=True)

	def test_amenidades_serializadas(
		self, mock_repository, propiedad_con_resenas, categoria_base
	):
		"""Verifica que las amenidades están presentes y completas en el payload."""
		mock_repository.obtain_view_detail.return_value = (
			propiedad_con_resenas,
			categoria_base,
		)

		query = ObtainCategoryViewDetail(mock_repository)
		result = query.execute(CATEGORIA_UUID)

		# categoria_base tiene 2 amenidades
		assert len(result["amenidades"]) == 2
		id_amenidades = {a["id_amenidad"] for a in result["amenidades"]}
		assert "amen-wifi" in id_amenidades
		assert "amen-cocina" in id_amenidades
		# Verificar estructura de cada amenidad
		for amenidad in result["amenidades"]:
			assert "id_amenidad" in amenidad
			assert "nombre" in amenidad
			assert "icono" in amenidad


# ==================== TestResenaEntidad ====================


class TestResenaEntidad:
	"""Pruebas directas de la entidad de dominio Resena."""

	def _resena_valida(self, id_resena=RESENA_UUID_1, calificacion=5) -> Resena:
		"""Helper: crea una reseña válida para pruebas."""
		return Resena(
			id_resena=id_resena,
			id_propiedad=PROPERTY_UUID,
			id_usuario=USUARIO_UUID,
			nombre_autor="Jose",
			avatar_url="https://cdn.example.com/jose.jpg",
			calificacion=calificacion,
			comentario="Los administradores son muy amables.",
			fecha_creacion=FECHA_BASE,
		)

	def test_calcular_rating_promedio_dominio(self, ubicacion_base):
		"""Verifica que calcular_rating_promedio retorna el resultado correcto."""
		resenas = [
			self._resena_valida(UUID("11111111-1111-1111-1111-111111111111"), calificacion=5),
			self._resena_valida(UUID("22222222-2222-2222-2222-222222222222"), calificacion=3),
		]
		# Promedio esperado: (5 + 3) / 2 = 4.0
		propiedad = construir_propiedad(
			id_propiedad=PROPERTY_UUID,
			nombre="Hotel Test",
			estrellas=4,
			ubicacion=ubicacion_base,
			porcentaje_impuesto=Decimal("10.00"),
			resenas=resenas,
		)

		promedio = propiedad.calcular_rating_promedio()

		assert promedio == 4.0

	def test_resena_validacion_calificacion_fuera_de_rango(self):
		"""Verifica que una calificación fuera de [1-5] lanza ValueError."""
		with pytest.raises(ValueError, match="calificación"):
			Resena(
				id_resena=RESENA_UUID_1,
				id_propiedad=PROPERTY_UUID,
				id_usuario=USUARIO_UUID,
				nombre_autor="Test",
				avatar_url=None,
				calificacion=6,  # Fuera del rango permitido
				comentario="Comentario de prueba",
				fecha_creacion=FECHA_BASE,
			)

	def test_resena_sin_avatar_se_serializa_como_null(
		self, mock_repository, ubicacion_base, categoria_base
	):
		"""Verifica que avatar_url=None se incluye como null en el payload sin errores."""
		resena_sin_avatar = Resena(
			id_resena=RESENA_UUID_1,
			id_propiedad=PROPERTY_UUID,
			id_usuario=USUARIO_UUID,
			nombre_autor="Luke",
			avatar_url=None,  # Sin avatar
			calificacion=5,
			comentario="Excelente lugar!",
			fecha_creacion=FECHA_BASE,
		)
		propiedad = construir_propiedad(
			id_propiedad=PROPERTY_UUID,
			nombre="Hotel Test",
			estrellas=4,
			ubicacion=ubicacion_base,
			porcentaje_impuesto=Decimal("10.00"),
			resenas=[resena_sin_avatar],
		)
		mock_repository.obtain_view_detail.return_value = (propiedad, categoria_base)

		query = ObtainCategoryViewDetail(mock_repository)
		result = query.execute(CATEGORIA_UUID)

		# avatar_url debe ser None en el payload (se serializa como null en JSON)
		assert result["resenas"][0]["avatar_url"] is None
		assert result["resenas"][0]["nombre_autor"] == "Luke"
