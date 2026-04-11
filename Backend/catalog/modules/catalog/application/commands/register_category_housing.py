from decimal import Decimal
from uuid import UUID
import uuid

from modules.catalog.domain.entities import (
	CategoriaHabitacion,
	Media,
	TipoMedia,
	VODinero,
	VORegla,
)
from modules.catalog.domain.events import CategoriaHabitacionRegistrada


class RegisterCategoryHousing:
	"""Comando para registrar una nueva categoría de habitación."""

	def __init__(self, repository, event_bus):
		self.repository = repository
		self.event_bus = event_bus

	def execute(
		self,
		id_propiedad: UUID,
		codigo_mapeo_pms: str,
		nombre_comercial: str,
		descripcion: str,
		monto_precio_base: Decimal,
		cargo_servicio: Decimal,
		moneda_precio_base: str,
		capacidad_pax: int,
		dias_anticipacion: int,
		porcentaje_penalidad: Decimal,
		foto_portada_url: str,
	) -> dict:
		"""
		Registra una nueva categoría de habitación en una propiedad.

		Args:
			id_propiedad: UUID de la propiedad
			codigo_mapeo_pms: Código para sincronización PMS
			nombre_comercial: Nombre comercial de la categoría
			descripcion: Descripción detallada
			monto_precio_base: Monto del precio base
			cargo_servicio: Cargo por servicio aplicado al precio base
			moneda_precio_base: Moneda (ej. COP, USD)
			capacidad_pax: Capacidad máxima de personas
			dias_anticipacion: Días de anticipación para cancelación
			porcentaje_penalidad: Porcentaje de penalidad
			foto_portada_url: URL de la foto portada de la categoría

		Returns:
			Dict con información de la categoría registrada y evento generado
		"""
		# Obtener propiedad existente
		propiedad = self.repository.obtain(id_propiedad)
		if not propiedad:
			return {
				"error": "Property not found",
				"id_propiedad": str(id_propiedad),
			}

		# Generar ID único de categoría como UUID
		id_categoria = str(uuid.uuid4())

		# Verificar que la categoría no exista
		categoria_existente = propiedad.obtener_categoria(id_categoria)
		if categoria_existente:
			return {
				"message": "Category already registered",
				"id_categoria": id_categoria,
			}

		# Crear objetos de valor
		precio_base = VODinero(
			monto=monto_precio_base,
			moneda=moneda_precio_base,
			cargo_servicio=cargo_servicio,
		)
		politica_cancelacion = VORegla(
			dias_anticipacion=dias_anticipacion,
			porcentaje_penalidad=porcentaje_penalidad,
		)
		foto_portada = Media(
			id_media=f"{id_categoria}-foto-portada",
			url_full=foto_portada_url,
			tipo=TipoMedia.FOTO_PORTADA,
			orden=1,
		)

		# Crear categoría de habitación
		categoria = CategoriaHabitacion(
			id_categoria=id_categoria,
			codigo_mapeo_pms=codigo_mapeo_pms,
			nombre_comercial=nombre_comercial,
			descripcion=descripcion,
			precio_base=precio_base,
			capacidad_pax=capacidad_pax,
			politica_cancelacion=politica_cancelacion,
			media=[foto_portada],
		)

		# Registrar categoría en la propiedad
		propiedad.registrar_categoria(categoria)

		# Guardar cambios
		self.repository.save(propiedad)

		# Crear y publicar evento
		evento = CategoriaHabitacionRegistrada(
			id_propiedad=id_propiedad,
			id_categoria=categoria.id_categoria,
			nombre_comercial=categoria.nombre_comercial,
			codigo_mapeo_pms=categoria.codigo_mapeo_pms,
		)

		self.event_bus.publish_event(
			routing_key=evento.routing_key,
			event_type=evento.type,
			payload=evento.to_dict(),
		)

		return {
			"id_propiedad": str(id_propiedad),
			"id_categoria": categoria.id_categoria,
			"nombre_comercial": categoria.nombre_comercial,
			"codigo_mapeo_pms": categoria.codigo_mapeo_pms,
			"descripcion": categoria.descripcion,
			"precio_base": {
				"monto": str(categoria.precio_base.monto),
				"moneda": categoria.precio_base.moneda,
				"cargo_servicio": str(categoria.precio_base.cargo_servicio),
			},
			"foto_portada_url": foto_portada.url_full,
			"capacidad_pax": categoria.capacidad_pax,
			"politica_cancelacion": {
				"dias_anticipacion": categoria.politica_cancelacion.dias_anticipacion,
				"porcentaje_penalidad": str(
					categoria.politica_cancelacion.porcentaje_penalidad
				),
			},
			"event_generated": evento.type,
		}
