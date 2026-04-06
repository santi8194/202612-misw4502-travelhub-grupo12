"""Entidades de dominio para el microservicio de búsqueda."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import List
from uuid import UUID


@dataclass(frozen=True)
class Disponibilidad:
    """Objeto de Valor que representa la disponibilidad para una fecha específica."""

    fecha: date
    cupos: int

    def __post_init__(self) -> None:
        if self.cupos < 0:
            raise ValueError("Los cupos deben ser mayores que 0")


@dataclass(frozen=True)
class Coordenadas:
    """Objeto de Valor que representa las coordenadas geográficas de un hospedaje."""

    lat: float
    lon: float

    def __post_init__(self) -> None:
        if not (-90 <= self.lat <= 90):
            raise ValueError("Latitud debe estar entre -90 y 90")
        if not (-180 <= self.lon <= 180):
            raise ValueError("Longitud debe estar entre -180 y 180")


@dataclass(frozen=True)
class Hospedaje:
    """Entidad que representa un hospedaje en el índice de búsqueda."""

    id_propiedad: UUID
    id_categoria: UUID
    propiedad_nombre: str
    categoria_nombre: str
    imagen_principal_url: str
    amenidades_destacadas: List[str]
    estrellas: int
    rating_promedio: float
    ciudad: str
    estado_provincia: str
    pais: str
    coordenadas: Coordenadas
    capacidad_pax: int
    precio_base: Decimal
    moneda: str
    es_reembolsable: bool
    disponibilidad: List[Disponibilidad] = field(default_factory=list)
