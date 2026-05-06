"""Pruebas unitarias para la generación de datos seed locales."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from app.infrastructure.local_seed_data import (
    build_seed_destinations,
    build_seed_documents,
    _generate_availability,
    PROPERTIES,
)


class TestGenerateAvailability:
    """Verifica la función que genera disponibilidad diaria."""

    def test_genera_60_dias_por_defecto(self):
        """Por defecto debe generar 60 días de disponibilidad."""
        resultado = _generate_availability(0)
        assert len(resultado) == 60

    def test_cada_dia_tiene_fecha_y_cupos(self):
        """Cada registro de disponibilidad debe tener fecha y cupos."""
        resultado = _generate_availability(0, days=3)
        assert len(resultado) == 3
        for item in resultado:
            assert "fecha" in item
            assert "cupos" in item
            assert isinstance(item["cupos"], int)

    def test_fechas_son_consecutivas(self):
        """Las fechas generadas deben ser consecutivas."""
        resultado = _generate_availability(0, days=5)
        fechas = [date.fromisoformat(item["fecha"]) for item in resultado]
        for i in range(1, len(fechas)):
            delta = (fechas[i] - fechas[i - 1]).days
            assert delta == 1


class TestBuildSeedDocuments:
    """Verifica la construcción de documentos de hospedajes seed."""

    def test_cantidad_igual_a_properties(self):
        """Debe generar tantos documentos como propiedades en PROPERTIES."""
        docs = build_seed_documents()
        assert len(docs) == len(PROPERTIES)

    def test_todos_los_campos_requeridos_presentes(self):
        """Cada documento debe contener todos los campos obligatorios."""
        docs = build_seed_documents()
        campos_requeridos = [
            "id_propiedad", "id_categoria", "propiedad_nombre",
            "categoria_nombre", "imagen_principal_url", "amenidades_destacadas",
            "estrellas", "rating_promedio", "ciudad", "estado_provincia",
            "pais", "coordenadas", "capacidad_pax", "precio_base",
            "moneda", "es_reembolsable", "disponibilidad",
        ]
        for doc in docs:
            for campo in campos_requeridos:
                assert campo in doc

    def test_ids_son_uuid_validos(self):
        """id_propiedad e id_categoria deben ser UUIDs válidos."""
        docs = build_seed_documents()
        for doc in docs:
            UUID(doc["id_propiedad"])
            UUID(doc["id_categoria"])

    def test_coordenadas_tienen_lat_lon(self):
        """Las coordenadas deben incluir lat y lon."""
        docs = build_seed_documents()
        for doc in docs:
            assert "lat" in doc["coordenadas"]
            assert "lon" in doc["coordenadas"]
            assert isinstance(doc["coordenadas"]["lat"], float)
            assert isinstance(doc["coordenadas"]["lon"], float)

    def test_disponibilidad_es_lista_no_vacia(self):
        """Cada documento debe tener disponibilidad como lista con elementos."""
        docs = build_seed_documents()
        for doc in docs:
            assert isinstance(doc["disponibilidad"], list)
            assert len(doc["disponibilidad"]) > 0

    def test_id_categoria_es_unico_por_fila(self):
        """id_categoria debe ser único entre todos los documentos."""
        docs = build_seed_documents()
        ids_categoria = [doc["id_categoria"] for doc in docs]
        assert len(ids_categoria) == len(set(ids_categoria))


class TestBuildSeedDestinations:
    """Verifica la construcción de destinos seed para autocompletado."""

    def test_retorna_lista(self):
        """La función debe retornar una lista."""
        destinos = build_seed_destinations()
        assert isinstance(destinos, list)
        assert len(destinos) > 0

    def test_cada_destino_tiene_campos_requeridos(self):
        """Cada destino debe tener id_destino, ciudad, ciudad_lower, estado_provincia, pais."""
        destinos = build_seed_destinations()
        for dest in destinos:
            assert "id_destino" in dest
            assert "ciudad" in dest
            assert "ciudad_lower" in dest
            assert "estado_provincia" in dest
            assert "pais" in dest

    def test_ciudad_lower_es_minusculas(self):
        """ciudad_lower debe ser la versión en minúsculas de ciudad."""
        destinos = build_seed_destinations()
        for dest in destinos:
            assert dest["ciudad_lower"] == dest["ciudad"].lower()

    def test_no_hay_destinos_duplicados(self):
        """No debe haber duplicados por (ciudad_lower, estado_provincia, pais)."""
        destinos = build_seed_destinations()
        combinaciones = [
            (d["ciudad_lower"], d["estado_provincia"], d["pais"])
            for d in destinos
        ]
        assert len(combinaciones) == len(set(combinaciones))

    def test_id_destino_es_uuid_valido(self):
        """id_destino debe ser un UUID válido."""
        destinos = build_seed_destinations()
        for dest in destinos:
            UUID(dest["id_destino"])
