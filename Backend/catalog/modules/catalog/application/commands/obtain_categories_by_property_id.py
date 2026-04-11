from uuid import UUID

from modules.catalog.domain.entities import TipoMedia
from modules.catalog.domain.events import CategoriasPropiedadConsultadas


class ObtainCategoriesByPropertyId:
	"""Comando para obtener todas las categorias de una propiedad."""

	def __init__(self, repository, event_bus):
		self.repository = repository
		self.event_bus = event_bus

	def execute(self, id_propiedad: UUID) -> dict:
		propiedad = self.repository.obtain(id_propiedad)
		if not propiedad:
			return {
				"error": "Property not found",
				"id_propiedad": str(id_propiedad),
			}

		categorias = []
		for categoria in propiedad.categorias_habitacion:
			foto_portada_url = None
			for media in categoria.media:
				if media.tipo == TipoMedia.FOTO_PORTADA:
					foto_portada_url = media.url_full
					break

			categorias.append(
				{
					"id_categoria": categoria.id_categoria,
					"codigo_mapeo_pms": categoria.codigo_mapeo_pms,
					"nombre_comercial": categoria.nombre_comercial,
					"descripcion": categoria.descripcion,
					"precio_base": {
						"monto": str(categoria.precio_base.monto),
						"moneda": categoria.precio_base.moneda,
						"cargo_servicio": str(categoria.precio_base.cargo_servicio),
					},
					"foto_portada_url": foto_portada_url,
					"capacidad_pax": categoria.capacidad_pax,
					"politica_cancelacion": {
						"dias_anticipacion": categoria.politica_cancelacion.dias_anticipacion,
						"porcentaje_penalidad": str(categoria.politica_cancelacion.porcentaje_penalidad),
					},
				}
			)

		evento = CategoriasPropiedadConsultadas(
			id_propiedad=id_propiedad,
			total_categorias=len(categorias),
		)
		self.event_bus.publish_event(
			routing_key=evento.routing_key,
			event_type=evento.type,
			payload=evento.to_dict(),
		)

		return {
			"id_propiedad": str(propiedad.id_propiedad),
			"total_categorias": len(categorias),
			"categorias": categorias,
			"event_generated": evento.type,
		}
