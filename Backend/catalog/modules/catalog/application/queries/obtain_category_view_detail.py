from uuid import UUID

from modules.catalog.domain.entities import TipoMedia


class ObtainCategoryViewDetail:
	"""Query para obtener el detalle consolidado de una categoría de propiedad.

	Alimenta la vista 'Detalle de Propiedad' del frontend con un payload
	único que incluye propiedad, categoría, amenidades, galería y reseñas.
	"""

	def __init__(self, repository):
		# Repositorio de propiedades (puerto de salida)
		self.repository = repository

	def execute(self, id_categoria: UUID) -> dict:
		"""Ejecuta la consulta de detalle consolidado de la categoría.

		Retorna un payload con la propiedad, la categoría solicitada, sus
		amenidades, galería (máx. 10 elementos), el promedio de calificación
		calculado dinámicamente y las 10 reseñas más recientes.

		Args:
			id_categoria: UUID de la categoría a consultar

		Returns:
			Dict con el detalle completo o error si no se encuentra
		"""
		# Consultar jerarquía completa en un solo viaje a la BD (cero N+1)
		resultado = self.repository.obtain_view_detail(id_categoria)
		if not resultado:
			return {
				"error": "Category not found",
				# Serializar UUID a str en la respuesta de error
				"id_categoria": str(id_categoria),
			}

		propiedad, categoria = resultado

		# Construir galería: portada primero, luego galería, máximo 10 elementos
		galeria = self._construir_galeria(categoria.media)

		# Ordenar reseñas por fecha descendente y tomar las 10 más recientes
		resenas_recientes = sorted(
			propiedad.resenas,
			key=lambda r: r.fecha_creacion,
			reverse=True,
		)[:10]

		return {
			"propiedad": {
				# Serializar UUID a str en la respuesta
				"id_propiedad": str(propiedad.id_propiedad),
				"nombre": propiedad.nombre,
				"estrellas": propiedad.estrellas,
				"ubicacion": {
					"ciudad": propiedad.ubicacion.ciudad,
					"estado_provincia": propiedad.ubicacion.estado_provincia,
					"pais": propiedad.ubicacion.pais,
					"coordenadas": {
						"lat": propiedad.ubicacion.coordenadas.lat,
						"lng": propiedad.ubicacion.coordenadas.lng,
					},
				},
				"porcentaje_impuesto": str(propiedad.porcentaje_impuesto),
			},
			"categoria": {
				# Serializar UUID a str en la respuesta
				"id_categoria": str(categoria.id_categoria),
				"nombre_comercial": categoria.nombre_comercial,
				"descripcion": categoria.descripcion,
				"precio_base": {
					"monto": str(categoria.precio_base.monto),
					"moneda": categoria.precio_base.moneda,
					"cargo_servicio": str(categoria.precio_base.cargo_servicio),
				},
				"capacidad_pax": categoria.capacidad_pax,
				"politica_cancelacion": {
					"dias_anticipacion": categoria.politica_cancelacion.dias_anticipacion,
					"porcentaje_penalidad": str(
						categoria.politica_cancelacion.porcentaje_penalidad
					),
				},
			},
			# Lista completa de amenidades de la categoría
			"amenidades": [
				{
					"id_amenidad": a.id_amenidad,
					"nombre": a.nombre,
					"icono": a.icono,
				}
				for a in categoria.amenidades
			],
			# Galería ordenada con portada primero, máximo 10 elementos
			"galeria": galeria,
			# Promedio calculado dinámicamente sobre las reseñas de la propiedad
			"rating_promedio": propiedad.calcular_rating_promedio(),
			# Total real de reseñas (no limitado a 10)
			"total_resenas": len(propiedad.resenas),
			# Solo las 10 reseñas más recientes para la vista
			"resenas": [
				{
					# Serializar UUIDs a str en la respuesta
					"id_resena": str(r.id_resena),
					"id_usuario": str(r.id_usuario),
					"nombre_autor": r.nombre_autor,
					"avatar_url": r.avatar_url,
					"calificacion": r.calificacion,
					"comentario": r.comentario,
					"fecha_creacion": r.fecha_creacion.isoformat(),
				}
				for r in resenas_recientes
			],
		}

	def _construir_galeria(self, media: list) -> list[dict]:
		"""Construye la galería ordenada para la vista de detalle.

		Coloca la foto de portada siempre en primer lugar, seguida de las
		imágenes de galería ordenadas. Máximo 10 elementos en total.

		Args:
			media: Lista de objetos Media de la categoría

		Returns:
			Lista de dicts con los datos de media, máximo 10 elementos
		"""
		# Separar portada e imágenes de galería
		portada = [m for m in media if m.tipo == TipoMedia.FOTO_PORTADA]
		galeria = [m for m in media if m.tipo == TipoMedia.IMAGEN_GALERIA]

		# Portada primero, luego galería, truncar a 10
		combinada = portada + galeria
		return [
			{
				"id_media": m.id_media,
				"url_full": m.url_full,
				"tipo": m.tipo.value,
				"orden": m.orden,
			}
			for m in combinada[:10]
		]
