from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from uuid import UUID


@dataclass(frozen=True, slots=True)
class DomainEvent:
	occurred_on: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class PropiedadCreada(DomainEvent):
	id_propiedad: UUID


@dataclass(frozen=True, slots=True)
class InventarioActualizado(DomainEvent):
	id_propiedad: UUID
	id_categoria: str = ""
	fecha: date = field(default_factory=date.today)
	cupos_disponibles: int = 0
