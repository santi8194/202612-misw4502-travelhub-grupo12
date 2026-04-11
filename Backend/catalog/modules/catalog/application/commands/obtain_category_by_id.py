from modules.catalog.domain.entities import TipoMedia


class ObtainCategoryById:
	"""Comando para obtener una categoria por su id."""

	def __init__(self, repository):
		self.repository = repository

	def execute(self, id_categoria: str) -> dict:
		categoria = self.repository.obtain_category_by_id(id_categoria)
		if not categoria:
			return {
				"error": "Category not found",
				"id_categoria": id_categoria,
			}

		foto_portada_url = None
		for media in categoria.media:
			if media.tipo == TipoMedia.FOTO_PORTADA:
				foto_portada_url = media.url_full
				break

		return {
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
			"inventario": [
				{
					"id_inventario": item.id_inventario,
					"fecha": item.fecha.isoformat(),
					"cupos_totales": item.cupos_totales,
					"cupos_disponibles": item.cupos_disponibles,
				}
				for item in categoria.inventario
			],
		}
