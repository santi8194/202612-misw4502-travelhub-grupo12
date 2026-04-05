from decimal import Decimal
from uuid import UUID

from modules.catalog.domain.entities import (
	CategoriaHabitacion,
	Coordenadas,
	construir_propiedad,
	VODireccion,
)
from modules.catalog.domain.events import PropiedadCreada


class CreateProperty:
	"""Comando para crear una nueva propiedad."""

	def __init__(self, repository, event_bus):
		self.repository = repository
		self.event_bus = event_bus

	def execute(
		self,
		id_propiedad: UUID,
		nombre: str,
		estrellas: int,
		ciudad: str,
		pais: str,
		latitud: float,
		longitud: float,
		porcentaje_impuesto: Decimal,
		categorias_habitacion: list[CategoriaHabitacion] | None = None,
	) -> dict:
		"""
		Crea una nueva propiedad y publica el evento de creacion.

		Args:
			id_propiedad: UUID único de la propiedad
			nombre: Nombre comercial de la propiedad
			estrellas: Categoría (1-5)
			ciudad: Ciudad de ubicación
			pais: País de ubicación
			latitud: Coordenada de latitud
			longitud: Coordenada de longitud
			porcentaje_impuesto: Porcentaje de impuesto aplicable
			categorias_habitacion: Categorías de habitación opcionales

		Returns:
			Dict con información de la propiedad creada y evento generado
		"""
		# Validar que la propiedad no exista
		existing_property = self.repository.obtain(id_propiedad)
		if existing_property:
			return {
				"message": "Property already exists",
				"id_propiedad": str(id_propiedad),
			}

		# Crear objetos de valor
		coordenadas = Coordenadas(lat=latitud, lng=longitud)
		ubicacion = VODireccion(ciudad=ciudad, pais=pais, coordenadas=coordenadas)

		# Construir propiedad
		propiedad = construir_propiedad(
			id_propiedad=id_propiedad,
			nombre=nombre,
			estrellas=estrellas,
			ubicacion=ubicacion,
			porcentaje_impuesto=porcentaje_impuesto,
			categorias_habitacion=categorias_habitacion,
		)

		# Guardar propiedad
		self.repository.save(propiedad)

		# Crear y publicar evento
		evento = PropiedadCreada(
			id_propiedad=propiedad.id_propiedad,
			nombre=propiedad.nombre,
			estrellas=propiedad.estrellas,
			ciudad=ubicacion.ciudad,
			pais=ubicacion.pais,
			porcentaje_impuesto=propiedad.porcentaje_impuesto,
		)

		self.event_bus.publish_event(
			routing_key=evento.routing_key,
			event_type=evento.type,
			payload=evento.to_dict(),
		)

		return {
			"id_propiedad": str(propiedad.id_propiedad),
			"nombre": propiedad.nombre,
			"estrellas": propiedad.estrellas,
			"ubicacion": {
				"ciudad": ubicacion.ciudad,
				"pais": ubicacion.pais,
				"coordenadas": {
					"lat": coordenadas.lat,
					"lng": coordenadas.lng,
				},
			},
			"event_generated": evento.type,
		}
