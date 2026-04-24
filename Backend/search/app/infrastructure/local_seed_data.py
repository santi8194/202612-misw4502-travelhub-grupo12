"""Deterministic sample data used for local SQLite runs."""

from __future__ import annotations

from datetime import date, timedelta
from uuid import NAMESPACE_DNS, uuid5

PROPERTIES = [
    {
        "nombre": "Hotel Boutique Las Palmas",
        "categoria": "Hotel",
        "ciudad": "Cartagena",
        "estado_provincia": "Bolivar",
        "pais": "Colombia",
        "lat": 10.3910,
        "lon": -75.5346,
        "estrellas": 5,
        "rating": 4.8,
        "precio": 450000,
        "capacidad": 4,
        "amenidades": ["Piscina", "WiFi", "Spa", "Restaurante", "Gym"],
        "imagen": "https://cdn.travelhub.example/hotel-boutique-las-palmas.jpg",
    },
    {
        "nombre": "Hostal El Viajero",
        "categoria": "Hostal",
        "ciudad": "Bogota",
        "estado_provincia": "Cundinamarca",
        "pais": "Colombia",
        "lat": 4.6097,
        "lon": -74.0817,
        "estrellas": 3,
        "rating": 4.2,
        "precio": 85000,
        "capacidad": 2,
        "amenidades": ["WiFi", "Cocina compartida", "Lavanderia"],
        "imagen": "https://cdn.travelhub.example/hostal-el-viajero.jpg",
    },
    {
        "nombre": "Cabana Montana Magica",
        "categoria": "Cabana",
        "ciudad": "Medellin",
        "estado_provincia": "Antioquia",
        "pais": "Colombia",
        "lat": 6.2442,
        "lon": -75.5812,
        "estrellas": 4,
        "rating": 4.9,
        "precio": 220000,
        "capacidad": 6,
        "amenidades": ["Chimenea", "BBQ", "Jardin", "WiFi"],
        "imagen": "https://cdn.travelhub.example/cabana-montana-magica.jpg",
    },
    {
        "nombre": "Resort Playa Dorada",
        "categoria": "Resort",
        "ciudad": "Santa Marta",
        "estado_provincia": "Magdalena",
        "pais": "Colombia",
        "lat": 11.2408,
        "lon": -74.1990,
        "estrellas": 5,
        "rating": 4.6,
        "precio": 680000,
        "capacidad": 8,
        "amenidades": ["Playa privada", "All-inclusive", "Piscina", "Spa", "WiFi"],
        "imagen": "https://cdn.travelhub.example/resort-playa-dorada.jpg",
    },
    {
        "nombre": "Apartamento Centro Historico",
        "categoria": "Apartamento",
        "ciudad": "Cartagena",
        "estado_provincia": "Bolivar",
        "pais": "Colombia",
        "lat": 10.4236,
        "lon": -75.5490,
        "estrellas": 4,
        "rating": 4.5,
        "precio": 320000,
        "capacidad": 5,
        "amenidades": ["WiFi", "Cocina", "Aire acondicionado", "Balcon"],
        "imagen": "https://cdn.travelhub.example/apto-centro-historico.jpg",
    },
    {
        "nombre": "Finca Cafetera La Esperanza",
        "categoria": "Finca",
        "ciudad": "Armenia",
        "estado_provincia": "Quindio",
        "pais": "Colombia",
        "lat": 4.5339,
        "lon": -75.6811,
        "estrellas": 4,
        "rating": 4.8,
        "precio": 195000,
        "capacidad": 10,
        "amenidades": ["Tour de cafe", "Piscina", "Naturaleza", "WiFi", "BBQ"],
        "imagen": "https://cdn.travelhub.example/finca-cafetera.jpg",
    },
]

AVAILABILITY_PATTERN = [6, 5, 4, 8, 3, 2, 7, 6, 5, 4, 3, 2]


def _generate_availability(prop_index: int, days: int = 60) -> list[dict]:
    today = date.today()
    disponibilidad = []
    for day_index in range(days):
        cupos = AVAILABILITY_PATTERN[(prop_index + day_index) % len(AVAILABILITY_PATTERN)]
        disponibilidad.append(
            {
                "fecha": (today + timedelta(days=day_index)).isoformat(),
                "cupos": cupos,
            }
        )
    return disponibilidad


def build_seed_documents() -> list[dict]:
    """Build the hospedajes seed rows."""
    documents: list[dict] = []
    for index, prop in enumerate(PROPERTIES):
        documents.append(
            {
                "id_propiedad": str(uuid5(NAMESPACE_DNS, f"propiedad:{prop['nombre']}")),
                "id_categoria": str(uuid5(NAMESPACE_DNS, f"categoria:{prop['categoria']}")),
                "propiedad_nombre": prop["nombre"],
                "categoria_nombre": prop["categoria"],
                "imagen_principal_url": prop["imagen"],
                "amenidades_destacadas": prop["amenidades"],
                "estrellas": prop["estrellas"],
                "rating_promedio": prop["rating"],
                "ciudad": prop["ciudad"],
                "estado_provincia": prop["estado_provincia"],
                "pais": prop["pais"],
                "coordenadas": {"lat": prop["lat"], "lon": prop["lon"]},
                "capacidad_pax": prop["capacidad"],
                "precio_base": prop["precio"],
                "moneda": "COP",
                "es_reembolsable": index % 2 == 0,
                "disponibilidad": _generate_availability(index),
            }
        )
    return documents


def build_seed_destinations() -> list[dict]:
    """Build unique destination rows for autocomplete."""
    seen: set[tuple[str, str, str]] = set()
    destinos: list[dict] = []

    for prop in PROPERTIES:
        ciudad_lower = prop["ciudad"].lower()
        key = (ciudad_lower, prop["estado_provincia"], prop["pais"])
        if key in seen:
            continue
        seen.add(key)
        destinos.append(
            {
                "id_destino": str(
                    uuid5(
                        NAMESPACE_DNS,
                        f"destino:{prop['ciudad']}|{prop['estado_provincia']}|{prop['pais']}",
                    )
                ),
                "ciudad": prop["ciudad"],
                "ciudad_lower": ciudad_lower,
                "estado_provincia": prop["estado_provincia"],
                "pais": prop["pais"],
            }
        )

    return destinos
