"""Pruebas unitarias para el repositorio de PostgreSQL.

Se prueban los métodos estáticos y la lógica de conversión de filas
sin necesidad de una base de datos real, usando diccionarios como
simulacro de ``asyncpg.Record``.
"""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from app.domain.entities import Coordenadas, Disponibilidad, Hospedaje
from app.domain.strategies import PriceFirstStrategy
from app.infrastructure.postgres_repository import PostgresHospedajeRepository


# ── Helpers ────────────────────────────────────────────────────────────────────


def _make_row(**overrides) -> dict:
    """Crea un registro simulado de asyncpg.Record como diccionario."""
    id_propiedad = uuid4()
    id_categoria = uuid4()
    base = {
        "id_propiedad": id_propiedad,
        "id_categoria": id_categoria,
        "propiedad_nombre": "Hotel Test",
        "categoria_nombre": "Hotel",
        "imagen_principal_url": "https://cdn.example.com/img.jpg",
        # asyncpg puede retornar JSONB como string o como dict; probamos ambos casos
        "amenidades_destacadas": json.dumps(["WiFi", "Piscina"]),
        "estrellas": 4,
        "rating_promedio": Decimal("4.5"),
        "ciudad": "Cartagena",
        "estado_provincia": "Bolívar",
        "pais": "Colombia",
        "coordenadas": json.dumps({"lat": 10.39, "lon": -75.53}),
        "capacidad_pax": 4,
        "precio_base": Decimal("350000"),
        "moneda": "COP",
        "es_reembolsable": True,
        "disponibilidad": json.dumps([
            {"fecha": "2026-03-15", "cupos": 5},
            {"fecha": "2026-03-16", "cupos": 3},
        ]),
    }
    base.update(overrides)
    return base


# ── Clase de tests: conversión de fila a entidad ──────────────────────────────


class TestRowToEntity:
    """Verifica la conversión correcta de filas de PostgreSQL a entidades de dominio."""

    def test_conversion_basica(self):
        """La conversión retorna una entidad Hospedaje con los campos correctos."""
        row = _make_row()
        entidad = PostgresHospedajeRepository._row_to_entity(row)

        assert isinstance(entidad, Hospedaje)
        assert entidad.propiedad_nombre == "Hotel Test"
        assert entidad.ciudad == "Cartagena"
        assert entidad.pais == "Colombia"
        assert entidad.moneda == "COP"
        assert entidad.es_reembolsable is True

    def test_precio_base_es_decimal(self):
        """El precio base debe ser de tipo Decimal para precisión numérica."""
        row = _make_row()
        entidad = PostgresHospedajeRepository._row_to_entity(row)

        assert isinstance(entidad.precio_base, Decimal)
        assert entidad.precio_base == Decimal("350000")

    def test_coordenadas_parseadas_desde_string(self):
        """Las coordenadas JSONB como string se parsean correctamente."""
        row = _make_row(coordenadas=json.dumps({"lat": 10.39, "lon": -75.53}))
        entidad = PostgresHospedajeRepository._row_to_entity(row)

        assert isinstance(entidad.coordenadas, Coordenadas)
        assert entidad.coordenadas.lat == 10.39
        assert entidad.coordenadas.lon == -75.53

    def test_coordenadas_parseadas_desde_dict(self):
        """Las coordenadas JSONB como dict (asyncpg con codec JSON) se parsean correctamente."""
        row = _make_row(coordenadas={"lat": 4.61, "lon": -74.08})
        entidad = PostgresHospedajeRepository._row_to_entity(row)

        assert entidad.coordenadas.lat == 4.61
        assert entidad.coordenadas.lon == -74.08

    def test_disponibilidad_parseada(self):
        """La disponibilidad JSONB se convierte a objetos Disponibilidad."""
        row = _make_row()
        entidad = PostgresHospedajeRepository._row_to_entity(row)

        assert len(entidad.disponibilidad) == 2
        assert isinstance(entidad.disponibilidad[0], Disponibilidad)
        assert entidad.disponibilidad[0].fecha == date(2026, 3, 15)
        assert entidad.disponibilidad[0].cupos == 5
        assert entidad.disponibilidad[1].fecha == date(2026, 3, 16)
        assert entidad.disponibilidad[1].cupos == 3

    def test_coordenadas_nulas_usan_cero(self):
        """Si coordenadas es None, se usan 0.0 como valor por defecto."""
        row = _make_row(coordenadas=None)
        entidad = PostgresHospedajeRepository._row_to_entity(row)

        assert entidad.coordenadas.lat == 0.0
        assert entidad.coordenadas.lon == 0.0

    def test_disponibilidad_nula_retorna_lista_vacia(self):
        """Si disponibilidad es None, se retorna lista vacía."""
        row = _make_row(disponibilidad=None)
        entidad = PostgresHospedajeRepository._row_to_entity(row)

        assert entidad.disponibilidad == []

    def test_amenidades_nulas_retornan_lista_vacia(self):
        """Si amenidades_destacadas es None, se retorna lista vacía."""
        row = _make_row(amenidades_destacadas=None)
        entidad = PostgresHospedajeRepository._row_to_entity(row)

        assert entidad.amenidades_destacadas == []

    def test_amenidades_como_dict(self):
        """Las amenidades JSONB como lista (asyncpg con codec JSON) se parsean correctamente."""
        row = _make_row(amenidades_destacadas=["WiFi", "Spa"])
        entidad = PostgresHospedajeRepository._row_to_entity(row)

        assert entidad.amenidades_destacadas == ["WiFi", "Spa"]

    def test_estrelllas_y_rating(self):
        """Los campos numéricos estrellas y rating se asignan correctamente."""
        row = _make_row(estrellas=5, rating_promedio=Decimal("4.9"))
        entidad = PostgresHospedajeRepository._row_to_entity(row)

        assert entidad.estrellas == 5
        assert entidad.rating_promedio == 4.9

    def test_id_propiedad_es_uuid(self):
        """El id_propiedad debe mantenerse como UUID."""
        id_esperado = uuid4()
        row = _make_row(id_propiedad=id_esperado)
        entidad = PostgresHospedajeRepository._row_to_entity(row)

        assert entidad.id_propiedad == id_esperado


# ── Clase de tests: estrategia SQL ────────────────────────────────────────────


class TestSqlSort:
    """Verifica que la estrategia genera la cláusula ORDER BY correcta para Postgres."""

    def test_price_first_genera_orden_ascendente(self):
        """PriceFirstStrategy debe retornar 'precio_base ASC' para Postgres."""
        strategy = PriceFirstStrategy()
        assert strategy.build_sql_sort() == "precio_base ASC"

    def test_price_first_genera_sort_opensearch(self):
        """PriceFirstStrategy debe retornar el sort DSL de OpenSearch también."""
        strategy = PriceFirstStrategy()
        result = strategy.build_sort()
        assert result == [{"precio_base": {"order": "asc"}}]
