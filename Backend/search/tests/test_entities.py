"""Unit tests for domain entities."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from app.domain.entities import Coordenadas, Disponibilidad, Hospedaje


# ── Disponibilidad ───────────────────────────────────────────────────────────


class TestDisponibilidad:
    def test_create_valid(self):
        d = Disponibilidad(fecha=date(2026, 3, 15), cupos=5)
        assert d.fecha == date(2026, 3, 15)
        assert d.cupos == 5

    def test_cupos_zero_is_valid(self):
        d = Disponibilidad(fecha=date(2026, 1, 1), cupos=0)
        assert d.cupos == 0

    def test_negative_cupos_raises(self):
        with pytest.raises(ValueError, match="Los cupos deben ser mayores que 0"):
            Disponibilidad(fecha=date(2026, 1, 1), cupos=-1)

    def test_frozen(self):
        d = Disponibilidad(fecha=date(2026, 1, 1), cupos=3)
        with pytest.raises(AttributeError):
            d.cupos = 10  # type: ignore[misc]


# ── Coordenadas ──────────────────────────────────────────────────────────────


class TestCoordenadas:
    def test_create_valid(self):
        c = Coordenadas(lat=10.39, lon=-75.53)
        assert c.lat == 10.39
        assert c.lon == -75.53

    def test_lat_out_of_range(self):
        with pytest.raises(ValueError, match="Latitud debe estar entre"):
            Coordenadas(lat=91.0, lon=0.0)

    def test_lon_out_of_range(self):
        with pytest.raises(ValueError, match="Longitud debe estar entre"):
            Coordenadas(lat=0.0, lon=181.0)

    def test_boundary_values(self):
        c = Coordenadas(lat=90.0, lon=-180.0)
        assert c.lat == 90.0
        assert c.lon == -180.0

    def test_frozen(self):
        c = Coordenadas(lat=0.0, lon=0.0)
        with pytest.raises(AttributeError):
            c.lat = 5.0  # type: ignore[misc]


# ── Hospedaje ────────────────────────────────────────────────────────────────



class TestHospedaje:
    def test_create_valid(self, sample_hospedaje):
        assert sample_hospedaje.propiedad_nombre == "Hotel Test"
        assert sample_hospedaje.ciudad == "Cartagena"
        assert len(sample_hospedaje.disponibilidad) == 1

    def test_frozen(self, sample_hospedaje):
        with pytest.raises(AttributeError):
            sample_hospedaje.propiedad_nombre = "Changed"  # type: ignore[misc]

    def test_empty_availability(self):
        h = Hospedaje(
            id_propiedad=uuid4(), id_categoria=uuid4(),
            propiedad_nombre="Hotel Test", categoria_nombre="Hotel",
            imagen_principal_url="https://cdn.example.com/img.jpg",
            amenidades_destacadas=[],
            estrellas=3, rating_promedio=4.0,
            ciudad="Bogotá", estado_provincia="", pais="Colombia",
            coordenadas=Coordenadas(lat=4.61, lon=-74.08),
            capacidad_pax=2, precio_base=Decimal("100000"),
            moneda="COP", es_reembolsable=False,
            disponibilidad=[],
        )
        assert h.disponibilidad == []

    def test_precio_base_as_decimal(self):
        h = Hospedaje(
            id_propiedad=uuid4(), id_categoria=uuid4(),
            propiedad_nombre="Hotel Test", categoria_nombre="Hotel",
            imagen_principal_url="https://cdn.example.com/img.jpg",
            amenidades_destacadas=[],
            estrellas=3, rating_promedio=4.0,
            ciudad="Bogotá", estado_provincia="", pais="Colombia",
            coordenadas=Coordenadas(lat=4.61, lon=-74.08),
            capacidad_pax=2, precio_base=Decimal("199999.99"),
            moneda="COP", es_reembolsable=False,
            disponibilidad=[],
        )
        assert isinstance(h.precio_base, Decimal)
        assert h.precio_base == Decimal("199999.99")
