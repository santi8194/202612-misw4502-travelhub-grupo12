from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from modules.catalog.domain.entities import ConfiguracionImpuestosPais, VODinero


class CalculateRoomPrice:
	"""Query para calcular el precio total de una habitación para un rango de fechas y país."""

	def __init__(self, repository):
		self.repository = repository

	def execute(
		self,
		id_categoria: UUID,
		fecha_inicio: date,
		fecha_fin: date,
		pais_usuario: str,
	) -> dict:
		"""Ejecuta el cálculo de precio de una categoría de habitación.

		Args:
			id_categoria: UUID de la categoría
			fecha_inicio: Fecha de check-in (inclusive)
			fecha_fin: Fecha de check-out (exclusivo)
			pais_usuario: País del usuario para aplicar impuestos y moneda

		Returns:
			Dict con el desglose del precio, o dict con 'error' si falla
		"""
		if fecha_inicio >= fecha_fin:
			return {"error": "Invalid dates: fecha_inicio must be before fecha_fin"}

		noches = (fecha_fin - fecha_inicio).days

		categoria = self.repository.obtain_category_by_id(id_categoria)
		if not categoria:
			return {"error": "Category not found", "id_categoria": str(id_categoria)}

		tax_config = self.repository.obtain_tax_config_by_country(pais_usuario)

		tarifa, tipo_tarifa = self._resolve_nightly_price(categoria, fecha_inicio, fecha_fin)

		# Pre-fetch tasa de la moneda origen una sola vez para ambas conversiones
		tasa_usd_origen = self._fetch_origin_rate(tarifa.moneda, tax_config)

		precio_noche_convertido = self._convert_price(tarifa.monto, tarifa.moneda, tax_config, tasa_usd_origen)
		cargo_servicio_convertido = self._convert_price(tarifa.cargo_servicio, tarifa.moneda, tax_config, tasa_usd_origen)

		subtotal = precio_noche_convertido * noches
		impuesto_tasa = tax_config.impuesto_tasa if tax_config else Decimal("0")
		impuestos_y_cargos = subtotal * impuesto_tasa + cargo_servicio_convertido
		total = subtotal + impuestos_y_cargos

		moneda_display = tax_config.moneda if tax_config else tarifa.moneda
		simbolo_moneda = tax_config.simbolo_moneda if tax_config else tarifa.moneda
		impuesto_nombre = tax_config.impuesto_nombre if tax_config else "No Tax"

		return {
			"precio_por_noche": float(precio_noche_convertido.quantize(Decimal("0.01"))),
			"noches": noches,
			"subtotal": float(subtotal.quantize(Decimal("0.01"))),
			"impuestos_y_cargos": float(impuestos_y_cargos.quantize(Decimal("0.01"))),
			"total": float(total.quantize(Decimal("0.01"))),
			"moneda": moneda_display,
			"simbolo_moneda": simbolo_moneda,
			"tipo_tarifa": tipo_tarifa,
			"impuesto_nombre": impuesto_nombre,
		}

	# ── Helpers ────────────────────────────────────────────────────────────────

	def _resolve_nightly_price(
		self, categoria, check_in: date, check_out: date
	) -> tuple[VODinero, str]:
		"""Determina la tarifa aplicable según las fechas del rango.

		Prioridad: TEMPORADA_ALTA > FIN_DE_SEMANA > BASE.
		Los meses de temporada alta son enero, junio, julio y diciembre.
		Los días de fin de semana son viernes, sábado y domingo.
		"""
		HIGH_SEASON_MONTHS = {1, 6, 7, 12}
		WEEKEND_DAYS = {4, 5, 6}  # viernes=4, sábado=5, domingo=6

		has_high_season = False
		has_weekend = False

		for i in range((check_out - check_in).days):
			d = check_in + timedelta(days=i)
			if d.month in HIGH_SEASON_MONTHS:
				has_high_season = True
			if d.weekday() in WEEKEND_DAYS:
				has_weekend = True

		if has_high_season and self._is_valid_tariff(categoria.tarifa_temporada_alta):
			return categoria.tarifa_temporada_alta, "TEMPORADA_ALTA"

		if has_weekend and self._is_valid_tariff(categoria.tarifa_fin_de_semana):
			return categoria.tarifa_fin_de_semana, "FIN_DE_SEMANA"

		return categoria.precio_base, "BASE"

	@staticmethod
	def _is_valid_tariff(tarifa: VODinero | None) -> bool:
		return tarifa is not None

	def _fetch_origin_rate(
		self, moneda_origen: str, tax_config: ConfiguracionImpuestosPais | None
	) -> Decimal:
		"""Devuelve la tasa USD de la moneda origen.

		Si moneda_origen es USD, la tasa es 1.0.
		Si moneda_origen es la misma que la de destino, no se necesita conversión.
		En otro caso, consulta la BD una sola vez.
		"""
		moneda_destino = tax_config.moneda if tax_config else None

		if moneda_origen == "USD" or moneda_origen == moneda_destino:
			return Decimal("1.0")

		config_origen = self.repository.obtain_tax_config_by_currency(moneda_origen)
		return config_origen.tasa_usd if config_origen else Decimal("1.0")

	@staticmethod
	def _convert_price(
		monto: Decimal,
		moneda_origen: str,
		tax_config: ConfiguracionImpuestosPais | None,
		tasa_usd_origen: Decimal,
	) -> Decimal:
		"""Convierte un monto de moneda_origen a la moneda de tax_config.

		Usa USD como pivote:  monto_usd = monto / tasa_origen
		                      resultado = monto_usd * tasa_destino
		"""
		if not tax_config or moneda_origen == tax_config.moneda:
			return monto

		tasa_usd_destino = (
			tax_config.tasa_usd if tax_config.moneda != "USD" else Decimal("1.0")
		)
		monto_usd = monto / tasa_usd_origen
		return monto_usd * tasa_usd_destino
