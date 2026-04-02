"""Fixtures compartidos de pytest para la suite de pruebas del microservicio de búsqueda."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from app.application.dtos import SearchRequest
from app.domain.entities import Coordenadas, Disponibilidad, Hospedaje


@pytest.fixture
def sample_hospedaje() -> Hospedaje:
    """Retorna una entidad Hospedaje válida con valores por defecto realistas."""
    return Hospedaje(
        id_propiedad=uuid4(),
        id_categoria=uuid4(),
        propiedad_nombre="Hotel Test",
        categoria_nombre="Hotel",
        imagen_principal_url="https://cdn.example.com/img.jpg",
        amenidades_destacadas=["WiFi", "Pool"],
        estrellas=4,
        rating_promedio=4.5,
        ciudad="Cartagena",
        estado_provincia="Bolívar",
        pais="Colombia",
        coordenadas=Coordenadas(lat=10.39, lon=-75.53),
        capacidad_pax=4,
        precio_base=Decimal("350000"),
        moneda="COP",
        es_reembolsable=True,
        disponibilidad=[
            Disponibilidad(fecha=date(2026, 3, 15), cupos=5),
        ],
    )


@pytest.fixture
def sample_search_request() -> SearchRequest:
    """Retorna una SearchRequest válida con valores por defecto realistas."""
    return SearchRequest(
        ciudad="Cartagena",
        estado_provincia="Bolívar",
        pais="Colombia",
        fecha_inicio=date(2026, 3, 15),
        fecha_fin=date(2026, 3, 17),
        huespedes=2,
    )
