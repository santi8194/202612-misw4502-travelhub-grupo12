"""Pruebas unitarias para el repositorio de OpenSearch.

No requiere un servidor OpenSearch real: se prueban los métodos estáticos
(_build_query, _hit_to_entity) y se mockea el cliente para buscar().
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from app.domain.entities import Coordenadas, Disponibilidad, Hospedaje
from app.domain.strategies import PriceFirstStrategy
from app.infrastructure.opensearch_repository import OpenSearchHospedajeRepository


# ── Helpers ────────────────────────────────────────────────────────────────────


def _make_hit(overrides: dict | None = None) -> dict:
    """Construye un hit de OpenSearch con valores por defecto."""
    base = {
        "_source": {
            "id_propiedad": "550e8400-e29b-41d4-a716-446655440000",
            "id_categoria": "660e8400-e29b-41d4-a716-446655440001",
            "propiedad_nombre": "Hotel Test",
            "categoria_nombre": "Hotel",
            "imagen_principal_url": "https://cdn.example.com/img.jpg",
            "amenidades_destacadas": ["WiFi", "Piscina"],
            "estrellas": 4,
            "rating_promedio": 4.5,
            "ciudad": "Cartagena",
            "estado_provincia": "Bolívar",
            "pais": "Colombia",
            "coordenadas": {"lat": 10.39, "lon": -75.53},
            "capacidad_pax": 4,
            "precio_base": 350000.0,
            "moneda": "COP",
            "es_reembolsable": True,
            "disponibilidad": [
                {"fecha": "2026-03-15", "cupos": 5},
                {"fecha": "2026-03-16", "cupos": 3},
            ],
        }
    }
    if overrides:
        base["_source"].update(overrides)
    return base


# ── Clase de tests: _build_query ─────────────────────────────────────────────


class TestBuildQuery:
    """Verifica la construcción de queries booleanas de OpenSearch."""

    def test_incluye_term_ciudad_y_pais(self):
        """La query debe incluir términos exactos para ciudad y país."""
        query = OpenSearchHospedajeRepository._build_query(
            ciudad="Cartagena",
            estado_provincia="",
            pais="Colombia",
            fecha_inicio=date(2026, 3, 15),
            fecha_fin=date(2026, 3, 15),
            huespedes=2,
        )
        must = query["bool"]["must"]
        terms = [c for c in must if "term" in c]
        assert {"term": {"ciudad.keyword": "Cartagena"}} in terms
        assert {"term": {"pais.keyword": "Colombia"}} in terms

    def test_incluye_estado_provincia_cuando_esta_presente(self):
        """Si se proporciona estado_provincia, debe aparecer como term adicional."""
        query = OpenSearchHospedajeRepository._build_query(
            ciudad="Cartagena",
            estado_provincia="Bolívar",
            pais="Colombia",
            fecha_inicio=date(2026, 3, 15),
            fecha_fin=date(2026, 3, 15),
            huespedes=2,
        )
        must = query["bool"]["must"]
        terms = [c for c in must if "term" in c]
        assert {"term": {"estado_provincia.keyword": "Bolívar"}} in terms

    def test_genera_filtro_nested_por_cada_dia(self):
        """Debe generar un filtro nested por cada día del rango."""
        query = OpenSearchHospedajeRepository._build_query(
            ciudad="Cartagena",
            estado_provincia="",
            pais="Colombia",
            fecha_inicio=date(2026, 3, 15),
            fecha_fin=date(2026, 3, 17),
            huespedes=2,
        )
        must = query["bool"]["must"]
        nested = [c for c in must if "nested" in c]
        assert len(nested) == 3  # 15, 16, 17

    def test_filtro_nested_requiere_fecha_y_cupos(self):
        """Cada filtro nested debe exigir fecha específica y cupos >= huespedes."""
        query = OpenSearchHospedajeRepository._build_query(
            ciudad="Cartagena",
            estado_provincia="",
            pais="Colombia",
            fecha_inicio=date(2026, 3, 15),
            fecha_fin=date(2026, 3, 15),
            huespedes=3,
        )
        # La query debe tener bool.must con al menos ciudad, pais y un nested
        must = query["bool"]["must"]
        # Verificar que hay al menos 3 clauses (ciudad, pais, nested)
        assert len(must) >= 3
        # Buscar el nested clause
        nested_clauses = [c for c in must if isinstance(c, dict) and "nested" in c]
        assert len(nested_clauses) >= 1
        nested_clause = nested_clauses[0]
        # Verificar estructura del nested
        assert nested_clause["nested"]["path"] == "disponibilidad"
        nested_must = nested_clause["nested"]["query"]["bool"]["must"]
        # Debe haber 2 must: term para fecha y range para cupos
        assert len(nested_must) == 2
        # Verificar term de fecha
        term_clause = next(c for c in nested_must if "term" in c)
        assert term_clause["term"]["disponibilidad.fecha"] == "2026-03-15"
        # Verificar range de cupos
        range_clause = next(c for c in nested_must if "range" in c)
        assert range_clause["range"]["disponibilidad.cupos"]["gte"] == 3


# ── Clase de tests: _hit_to_entity ───────────────────────────────────────────


class TestHitToEntity:
    """Verifica la conversión de hits de OpenSearch a entidades de dominio."""

    def test_convierte_hit_a_hospedaje(self):
        """Un hit con todos los campos debe convertirse a una entidad Hospedaje."""
        hit = _make_hit()
        entidad = OpenSearchHospedajeRepository._hit_to_entity(hit)
        assert isinstance(entidad, Hospedaje)
        assert entidad.propiedad_nombre == "Hotel Test"
        assert entidad.ciudad == "Cartagena"
        assert entidad.pais == "Colombia"

    def test_id_propiedad_es_uuid(self):
        """El id_propiedad debe parsearse como UUID."""
        hit = _make_hit()
        entidad = OpenSearchHospedajeRepository._hit_to_entity(hit)
        assert isinstance(entidad.id_propiedad, UUID)

    def test_id_categoria_es_uuid(self):
        """El id_categoria debe parsearse como UUID."""
        hit = _make_hit()
        entidad = OpenSearchHospedajeRepository._hit_to_entity(hit)
        assert isinstance(entidad.id_categoria, UUID)

    def test_precio_base_es_decimal(self):
        """El precio_base debe ser de tipo Decimal."""
        hit = _make_hit()
        entidad = OpenSearchHospedajeRepository._hit_to_entity(hit)
        assert isinstance(entidad.precio_base, Decimal)
        assert entidad.precio_base == Decimal("350000")

    def test_coordenadas_parseadas(self):
        """Las coordenadas deben parsearse como Coordenadas."""
        hit = _make_hit()
        entidad = OpenSearchHospedajeRepository._hit_to_entity(hit)
        assert isinstance(entidad.coordenadas, Coordenadas)
        assert entidad.coordenadas.lat == 10.39
        assert entidad.coordenadas.lon == -75.53

    def test_disponibilidad_parseada(self):
        """La disponibilidad debe convertirse en objetos Disponibilidad."""
        hit = _make_hit()
        entidad = OpenSearchHospedajeRepository._hit_to_entity(hit)
        assert len(entidad.disponibilidad) == 2
        assert isinstance(entidad.disponibilidad[0], Disponibilidad)
        assert entidad.disponibilidad[0].fecha == date(2026, 3, 15)
        assert entidad.disponibilidad[0].cupos == 5

    def test_campos_opcionales_usan_valores_por_defecto(self):
        """Si faltan campos opcionales, deben usar valores por defecto."""
        # El hit debe omitir campos para que .get() use el default
        # (src.get(key, default) retorna None si la clave existe con valor None)
        hit = _make_hit(overrides={
            "coordenadas": {},
        })
        # Eliminar claves que no deben existir en el hit para probar defaults
        hit["_source"].pop("estrellas", None)
        hit["_source"].pop("rating_promedio", None)
        hit["_source"].pop("estado_provincia", None)
        hit["_source"].pop("capacidad_pax", None)
        hit["_source"].pop("es_reembolsable", None)
        entidad = OpenSearchHospedajeRepository._hit_to_entity(hit)
        assert entidad.estrellas == 0
        assert entidad.rating_promedio == 0.0
        assert entidad.estado_provincia == ""
        assert entidad.coordenadas.lat == 0.0
        assert entidad.coordenadas.lon == 0.0
        assert entidad.capacidad_pax == 1
        assert entidad.es_reembolsable is False


# ── Clase de tests: buscar con mock ─────────────────────────────────────────


class TestBuscar:
    """Verifica buscar() con un cliente OpenSearch mockeado."""

    @pytest.mark.asyncio
    async def test_buscar_retorna_lista_de_hospedajes(self):
        """buscar() debe retornar una lista de entidades Hospedaje."""
        mock_client = AsyncMock()
        mock_client.search.return_value = {
            "hits": {
                "hits": [
                    _make_hit(),
                    _make_hit(overrides={"propiedad_nombre": "Hotel B"}),
                ]
            }
        }
        repo = OpenSearchHospedajeRepository(mock_client, "hospedajes")
        strategy = PriceFirstStrategy()

        resultados = await repo.buscar(
            ciudad="Cartagena",
            estado_provincia="",
            pais="Colombia",
            fecha_inicio=date(2026, 3, 15),
            fecha_fin=date(2026, 3, 15),
            huespedes=2,
            strategy=strategy,
        )

        assert len(resultados) == 2
        assert all(isinstance(r, Hospedaje) for r in resultados)
        assert resultados[0].propiedad_nombre == "Hotel Test"
        assert resultados[1].propiedad_nombre == "Hotel B"

    @pytest.mark.asyncio
    async def test_buscar_retorna_vacio_sin_hits(self):
        """Si OpenSearch retorna cero hits, debe retornar lista vacía."""
        mock_client = AsyncMock()
        mock_client.search.return_value = {"hits": {"hits": []}}
        repo = OpenSearchHospedajeRepository(mock_client, "hospedajes")
        strategy = PriceFirstStrategy()

        resultados = await repo.buscar(
            ciudad="Inexistente",
            estado_provincia="",
            pais="PaisX",
            fecha_inicio=date(2026, 3, 15),
            fecha_fin=date(2026, 3, 15),
            huespedes=1,
            strategy=strategy,
        )

        assert resultados == []
