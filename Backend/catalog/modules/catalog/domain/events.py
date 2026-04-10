from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class DomainEvent(ABC):
	"""Clase base para eventos de dominio."""
	occurred_on: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

	@property
	@abstractmethod
	def routing_key(self) -> str:
		"""Clave de enrutamiento para el event bus."""
		pass

	@property
	def type(self) -> str:
		"""Tipo del evento (nombre de la clase)."""
		return self.__class__.__name__

	def to_dict(self) -> dict:
		"""Convierte el evento a un diccionario."""
		return {
			**asdict(self),
			"occurred_on": self.occurred_on.isoformat(),
		}


@dataclass(frozen=True, slots=True, kw_only=True)
class PropiedadCreada(DomainEvent):
	"""Evento emitido cuando se crea una nueva propiedad."""
	id_propiedad: UUID
	nombre: str
	estrellas: int
	ciudad: str
	pais: str
	porcentaje_impuesto: Decimal

	@property
	def routing_key(self) -> str:
		return "catalog.property.created"


@dataclass(frozen=True, slots=True, kw_only=True)
class CategoriaHabitacionRegistrada(DomainEvent):
	"""Evento emitido cuando se registra una nueva categoría de habitación."""
	id_propiedad: UUID
	id_categoria: str
	nombre_comercial: str
	codigo_mapeo_pms: str

	@property
	def routing_key(self) -> str:
		return "catalog.category.registered"


@dataclass(frozen=True, slots=True, kw_only=True)
class InventarioActualizado(DomainEvent):
	"""Evento emitido cuando se actualiza el inventario de una categoría."""
	id_propiedad: UUID
	id_categoria: str
	id_inventario: str
	fecha: date
	cupos_totales: int
	cupos_disponibles: int

	@property
	def routing_key(self) -> str:
		return "catalog.inventory.updated"
