"""Pydantic v2 DTOs for request validation and response serialisation."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


# ── Request ──────────────────────────────────────────────────────────────────

MAX_RANGE_DAYS = 30


class SearchRequest(BaseModel):
    """Query-parameter DTO for the search endpoint."""

    ciudad: str = Field(..., min_length=1, description="City name")
    estado_provincia: str = Field("", description="State or province (optional)")
    pais: str = Field(..., min_length=1, description="Country name")
    fecha_inicio: date = Field(..., description="Check-in date (inclusive)")
    fecha_fin: date = Field(..., description="Check-out date (inclusive)")
    huespedes: int = Field(..., ge=1, description="Number of guests (>= 1)")

    @model_validator(mode="after")
    def _validate_date_range(self) -> "SearchRequest":
        if self.fecha_fin < self.fecha_inicio:
            raise ValueError("fecha_fin must be >= fecha_inicio")
        delta = (self.fecha_fin - self.fecha_inicio).days
        if delta > MAX_RANGE_DAYS:
            raise ValueError(
                f"Date range must not exceed {MAX_RANGE_DAYS} days "
                f"(requested {delta} days)"
            )
        return self


# ── Response ─────────────────────────────────────────────────────────────────


class CoordenadasDTO(BaseModel):
    lat: float
    lon: float


class HospedajeResponse(BaseModel):
    """Single accommodation result."""

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
    coordenadas: CoordenadasDTO
    capacidad_pax: int
    precio_base: Decimal
    moneda: str
    es_reembolsable: bool


class SearchResponse(BaseModel):
    """Response wrapper for search results."""

    resultados: List[HospedajeResponse]
    total: int


class DestinationItem(BaseModel):
    """Single destination suggestion for autocomplete."""

    ciudad: str
    estado_provincia: str
    pais: str


class DestinationResponse(BaseModel):
    """Response wrapper for destination autocomplete."""

    results: List[DestinationItem]
