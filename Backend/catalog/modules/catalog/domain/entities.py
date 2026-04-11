from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Iterable
from urllib.parse import urlparse
from uuid import UUID


class TipoMedia(str, Enum):
	FOTO_PORTADA = "FOTO_PORTADA"
	IMAGEN_GALERIA = "IMAGEN_GALERIA"
	VIDEO = "VIDEO"


@dataclass(frozen=True, slots=True)
class Coordenadas:
	lat: float
	lng: float

	def __post_init__(self) -> None:
		if not -90 <= self.lat <= 90:
			raise ValueError("La latitud debe estar entre -90 y 90")
		if not -180 <= self.lng <= 180:
			raise ValueError("La longitud debe estar entre -180 y 180")


@dataclass(frozen=True, slots=True)
class VODireccion:
	ciudad: str
	pais: str
	coordenadas: Coordenadas

	def __post_init__(self) -> None:
		if not self.ciudad.strip():
			raise ValueError("La ciudad es obligatoria")
		if not self.pais.strip():
			raise ValueError("El pais es obligatorio")


@dataclass(frozen=True, slots=True)
class VODinero:
	monto: Decimal
	moneda: str
	cargo_servicio: Decimal = Decimal("0.00")

	def __post_init__(self) -> None:
		try:
			normalized_amount = Decimal(self.monto)
		except (InvalidOperation, TypeError) as error:
			raise ValueError("El monto debe ser un valor decimal valido") from error

		try:
			normalized_service_charge = Decimal(self.cargo_servicio)
		except (InvalidOperation, TypeError) as error:
			raise ValueError("El cargo por servicio debe ser un valor decimal valido") from error

		if normalized_amount <= Decimal("0"):
			raise ValueError("El monto debe ser mayor a cero")
		if normalized_service_charge < Decimal("0"):
			raise ValueError("El cargo por servicio no puede ser negativo")
		if len(self.moneda.strip()) != 3:
			raise ValueError("La moneda debe tener 3 caracteres")

		object.__setattr__(self, "monto", normalized_amount.quantize(Decimal("0.01")))
		object.__setattr__(self, "moneda", self.moneda.strip().upper())
		object.__setattr__(self, "cargo_servicio", normalized_service_charge.quantize(Decimal("0.01")))


@dataclass(frozen=True, slots=True)
class VORegla:
	dias_anticipacion: int
	porcentaje_penalidad: Decimal

	def __post_init__(self) -> None:
		try:
			penalty = Decimal(self.porcentaje_penalidad)
		except (InvalidOperation, TypeError) as error:
			raise ValueError("La penalidad debe ser un decimal valido") from error

		if self.dias_anticipacion < 0:
			raise ValueError("Los dias de anticipacion no pueden ser negativos")
		if not Decimal("0") <= penalty <= Decimal("100"):
			raise ValueError("La penalidad debe estar entre 0 y 100")

		object.__setattr__(self, "porcentaje_penalidad", penalty.quantize(Decimal("0.01")))


@dataclass(slots=True)
class Media:
	id_media: str
	url_full: str
	tipo: TipoMedia
	orden: int

	def __post_init__(self) -> None:
		if not self.id_media.strip():
			raise ValueError("El ID de media es obligatorio")
		parsed_url = urlparse(self.url_full)
		if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
			raise ValueError("La URL del recurso multimedia debe ser valida")
		if self.orden < 1:
			raise ValueError("El orden de la media debe ser mayor o igual a 1")


@dataclass(slots=True)
class Amenidad:
	id_amenidad: str
	nombre: str
	icono: str

	def __post_init__(self) -> None:
		if not self.id_amenidad.strip():
			raise ValueError("El ID de amenidad es obligatorio")
		if not self.nombre.strip():
			raise ValueError("El nombre de la amenidad es obligatorio")
		if not self.icono.strip():
			raise ValueError("El icono de la amenidad es obligatorio")


@dataclass(slots=True)
class Inventario:
	id_inventario: str
	fecha: date
	cupos_totales: int
	cupos_disponibles: int

	def __post_init__(self) -> None:
		if not self.id_inventario.strip():
			raise ValueError("El ID de inventario es obligatorio")
		if self.cupos_totales < 0:
			raise ValueError("Los cupos totales no pueden ser negativos")
		if self.cupos_disponibles < 0:
			raise ValueError("Los cupos disponibles no pueden ser negativos")
		if self.cupos_disponibles > self.cupos_totales:
			raise ValueError("Los cupos disponibles no pueden superar los cupos totales")


@dataclass(slots=True)
class CategoriaHabitacion:
	id_categoria: str
	codigo_mapeo_pms: str
	nombre_comercial: str
	descripcion: str
	precio_base: VODinero
	capacidad_pax: int
	politica_cancelacion: VORegla
	media: list[Media] = field(default_factory=list)
	amenidades: list[Amenidad] = field(default_factory=list)
	inventario: list[Inventario] = field(default_factory=list)

	def __post_init__(self) -> None:
		if not self.id_categoria.strip():
			raise ValueError("El ID de categoria es obligatorio")
		if not self.codigo_mapeo_pms.strip():
			raise ValueError("El codigo de mapeo PMS es obligatorio")
		if not self.nombre_comercial.strip():
			raise ValueError("El nombre comercial es obligatorio")
		if not self.descripcion.strip():
			raise ValueError("La descripcion es obligatoria")
		if self.capacidad_pax <= 0:
			raise ValueError("La capacidad de pasajeros debe ser mayor a cero")

	def actualizar_inventario(self, inventario_actualizado: Inventario) -> Inventario:
		for index, inventario in enumerate(self.inventario):
			same_inventory = inventario.id_inventario == inventario_actualizado.id_inventario
			same_date = inventario.fecha == inventario_actualizado.fecha
			if same_inventory or same_date:
				self.inventario[index] = inventario_actualizado
				return inventario_actualizado

		self.inventario.append(inventario_actualizado)
		return inventario_actualizado

	def disponibilidad_para(self, fecha_objetivo: date) -> Inventario | None:
		for inventario in self.inventario:
			if inventario.fecha == fecha_objetivo:
				return inventario
		return None


@dataclass(slots=True)
class Propiedad:
	id_propiedad: UUID
	nombre: str
	estrellas: int
	ubicacion: VODireccion
	porcentaje_impuesto: Decimal
	categorias_habitacion: list[CategoriaHabitacion] = field(default_factory=list)

	def __post_init__(self) -> None:
		try:
			tax = Decimal(self.porcentaje_impuesto)
		except (InvalidOperation, TypeError) as error:
			raise ValueError("El porcentaje de impuesto debe ser un decimal valido") from error

		if not self.nombre.strip():
			raise ValueError("El nombre de la propiedad es obligatorio")
		if not 1 <= self.estrellas <= 5:
			raise ValueError("La cantidad de estrellas debe estar entre 1 y 5")
		if not Decimal("0") <= tax <= Decimal("100"):
			raise ValueError("El porcentaje de impuesto debe estar entre 0 y 100")

		object.__setattr__(self, "porcentaje_impuesto", tax.quantize(Decimal("0.01")))

	def registrar_categoria(self, categoria: CategoriaHabitacion) -> None:
		if self.obtener_categoria(categoria.id_categoria) is not None:
			raise ValueError("La categoria de habitacion ya existe para esta propiedad")
		self.categorias_habitacion.append(categoria)

	def obtener_categoria(self, id_categoria: str) -> CategoriaHabitacion | None:
		for categoria in self.categorias_habitacion:
			if categoria.id_categoria == id_categoria:
				return categoria
		return None

	def actualizar_inventario(self, id_categoria: str, inventario_actualizado: Inventario) -> Inventario:
		categoria = self.obtener_categoria(id_categoria)
		if categoria is None:
			raise ValueError("La categoria de habitacion no existe en la propiedad")
		return categoria.actualizar_inventario(inventario_actualizado)

	def disponibilidad_para(self, id_categoria: str, fecha_objetivo: date) -> Inventario | None:
		categoria = self.obtener_categoria(id_categoria)
		if categoria is None:
			return None
		return categoria.disponibilidad_para(fecha_objetivo)


def construir_propiedad(
	id_propiedad: UUID,
	nombre: str,
	estrellas: int,
	ubicacion: VODireccion,
	porcentaje_impuesto: Decimal,
	categorias_habitacion: Iterable[CategoriaHabitacion] | None = None,
) -> Propiedad:
	return Propiedad(
		id_propiedad=id_propiedad,
		nombre=nombre,
		estrellas=estrellas,
		ubicacion=ubicacion,
		porcentaje_impuesto=porcentaje_impuesto,
		categorias_habitacion=list(categorias_habitacion or []),
	)
