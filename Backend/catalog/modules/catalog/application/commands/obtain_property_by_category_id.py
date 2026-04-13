class ObtainPropertyByCategoryId:
	"""Comando para obtener la propiedad asociada a un id de categoria."""

	def __init__(self, repository):
		self.repository = repository

	def execute(self, id_categoria: str) -> dict:
		propiedad = self.repository.obtain_by_category_id(id_categoria)
		if not propiedad:
			return {
				"error": "Property not found for category",
				"id_categoria": id_categoria,
			}

		return {
			"id_categoria": id_categoria,
			"id_propiedad": str(propiedad.id_propiedad),
			"nombre": propiedad.nombre,
			"estrellas": propiedad.estrellas,
			"ubicacion": {
				"ciudad": propiedad.ubicacion.ciudad,
				"pais": propiedad.ubicacion.pais,
				"coordenadas": {
					"lat": propiedad.ubicacion.coordenadas.lat,
					"lng": propiedad.ubicacion.coordenadas.lng,
				},
			},
			"porcentaje_impuesto": str(propiedad.porcentaje_impuesto),
			"categorias_habitacion": len(propiedad.categorias_habitacion),
		}
