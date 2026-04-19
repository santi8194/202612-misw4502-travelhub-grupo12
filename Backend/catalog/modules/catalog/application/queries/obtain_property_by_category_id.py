from uuid import UUID


class ObtainPropertyByCategoryId:
	"""Query para obtener la propiedad asociada a un UUID de categoria."""

	def __init__(self, repository):
		self.repository = repository

	def execute(self, id_categoria: UUID) -> dict:
		"""Obtiene la propiedad que contiene la categoria indicada.

		Args:
			id_categoria: UUID de la categoria de habitacion

		Returns:
			Dict con datos de la propiedad o error si no se encuentra
		"""
		propiedad = self.repository.obtain_by_category_id(id_categoria)
		if not propiedad:
			return {
				"error": "Property not found for category",
				# Serializar UUID a str en la respuesta
				"id_categoria": str(id_categoria),
			}

		return {
			# Serializar UUID a str en la respuesta
			"id_categoria": str(id_categoria),
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
			"categorias_habitacion": len(propiedad.categorias_habitacion),
		}
