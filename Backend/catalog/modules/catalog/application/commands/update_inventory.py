from datetime import date
from uuid import UUID

from modules.catalog.domain.entities import Inventario
from modules.catalog.domain.events import InventarioActualizado


class UpdateInventory:
	"""Comando para actualizar el inventario de una categoría de habitación."""

	def __init__(self, repository, event_bus):
		self.repository = repository
		self.event_bus = event_bus

	def execute(
		self,
		id_propiedad: UUID,
		id_categoria: str,
		id_inventario: str,
		fecha: date,
		cupos_totales: int,
		cupos_disponibles: int,
	) -> dict:
		"""
		Actualiza el inventario de una categoría en una fecha específica.

		Args:
			id_propiedad: UUID de la propiedad
			id_categoria: ID de la categoría de habitación
			id_inventario: ID único del registro de inventario
			fecha: Fecha a la que corresponde el inventario
			cupos_totales: Total de cupos disponibles
			cupos_disponibles: Cupos que aún se pueden vender

		Returns:
			Dict con información del inventario actualizado y evento generado
		"""
		# Obtener propiedad existente
		propiedad = self.repository.obtain(id_propiedad)
		if not propiedad:
			return {
				"error": "Property not found",
				"id_propiedad": str(id_propiedad),
			}

		# Verificar que la categoría existe
		categoria = propiedad.obtener_categoria(id_categoria)
		if not categoria:
			return {
				"error": "Category not found",
				"id_categoria": id_categoria,
			}

		# Crear registro de inventario
		inventario = Inventario(
			id_inventario=id_inventario,
			fecha=fecha,
			cupos_totales=cupos_totales,
			cupos_disponibles=cupos_disponibles,
		)

		# Actualizar inventario en la categoría
		inventario_actualizado = categoria.actualizar_inventario(inventario)

		# Guardar cambios
		self.repository.save(propiedad)

		# Crear y publicar evento
		evento = InventarioActualizado(
			id_propiedad=id_propiedad,
			id_categoria=id_categoria,
			id_inventario=id_inventario,
			fecha=fecha,
			cupos_totales=cupos_totales,
			cupos_disponibles=cupos_disponibles,
		)

		self.event_bus.publish_event(
			routing_key=evento.routing_key,
			event_type=evento.type,
			payload=evento.to_dict(),
		)

		return {
			"id_propiedad": str(id_propiedad),
			"id_categoria": id_categoria,
			"id_inventario": id_inventario,
			"fecha": fecha.isoformat(),
			"cupos_totales": cupos_totales,
			"cupos_disponibles": cupos_disponibles,
			"event_generated": evento.type,
		}
