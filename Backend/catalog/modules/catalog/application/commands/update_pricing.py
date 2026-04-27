from decimal import Decimal
from uuid import UUID

from modules.catalog.domain.entities import VODinero
from modules.catalog.domain.events import TarifasActualizadas


class UpdatePricing:
	"""Comando para actualizar tarifas diferenciadas de una categoría de habitación."""

	def __init__(self, repository, event_bus):
		self.repository = repository
		self.event_bus = event_bus

	def execute(
		self,
		id_propiedad: UUID,
		id_categoria: UUID,
		tarifa_base_monto: Decimal,
		moneda: str,
		cargo_servicio: Decimal = Decimal("0"),
		tarifa_fin_de_semana_monto: Decimal | None = None,
		tarifa_temporada_alta_monto: Decimal | None = None,
	) -> dict:
		"""Actualiza tarifa base y tarifas diferenciadas de una categoría.

		Args:
			id_propiedad: UUID de la propiedad dueña de la categoría.
			id_categoria: UUID de la categoría a actualizar.
			tarifa_base_monto: Nuevo monto de la tarifa base.
			moneda: Código ISO 4217 de la moneda (3 chars).
			cargo_servicio: Cargo por servicio aplicado a todas las tarifas.
			tarifa_fin_de_semana_monto: Tarifa especial fin de semana (None = no aplica).
			tarifa_temporada_alta_monto: Tarifa especial temporada alta (None = no aplica).

		Returns:
			Dict con resumen de tarifas actualizadas o error.
		"""
		propiedad = self.repository.obtain(id_propiedad)
		if not propiedad:
			return {"error": "Property not found", "id_propiedad": str(id_propiedad)}

		categoria = propiedad.obtener_categoria(id_categoria)
		if not categoria:
			return {"error": "Category not found", "id_categoria": str(id_categoria)}

		# Actualizar tarifa base
		categoria.precio_base = VODinero(
			monto=tarifa_base_monto,
			moneda=moneda,
			cargo_servicio=cargo_servicio,
		)

		# Construir tarifas diferenciadas (None si no se envían)
		tarifa_fds = (
			VODinero(monto=tarifa_fin_de_semana_monto, moneda=moneda, cargo_servicio=cargo_servicio)
			if tarifa_fin_de_semana_monto is not None
			else None
		)
		tarifa_ta = (
			VODinero(monto=tarifa_temporada_alta_monto, moneda=moneda, cargo_servicio=cargo_servicio)
			if tarifa_temporada_alta_monto is not None
			else None
		)

		categoria.actualizar_tarifas(tarifa_fds, tarifa_ta)
		self.repository.save(propiedad)

		evento = TarifasActualizadas(
			id_propiedad=id_propiedad,
			id_categoria=id_categoria,
			tarifa_base_monto=tarifa_base_monto,
			moneda=moneda,
			tarifa_fin_de_semana_monto=tarifa_fin_de_semana_monto,
			tarifa_temporada_alta_monto=tarifa_temporada_alta_monto,
		)
		self.event_bus.publish_event(
			routing_key=evento.routing_key,
			event_type=evento.type,
			payload=evento.to_dict(),
		)

		return {
			"id_propiedad": str(id_propiedad),
			"id_categoria": str(id_categoria),
			"tarifa_base": {
				"monto": str(tarifa_base_monto),
				"moneda": moneda,
				"cargo_servicio": str(cargo_servicio),
			},
			"tarifa_fin_de_semana": {"monto": str(tarifa_fin_de_semana_monto), "moneda": moneda}
			if tarifa_fin_de_semana_monto is not None
			else None,
			"tarifa_temporada_alta": {"monto": str(tarifa_temporada_alta_monto), "moneda": moneda}
			if tarifa_temporada_alta_monto is not None
			else None,
			"message": "Tarifas actualizadas correctamente",
		}
