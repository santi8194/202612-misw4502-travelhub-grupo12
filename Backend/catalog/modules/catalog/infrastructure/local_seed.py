"""Seed local determinista para Catalog en SQLite.

Genera propiedades, categorias, inventario, media, amenidades y resenas.
Los ``id_categoria`` se calculan con la misma formula usada en Search local
para permitir mapeo directo por categoria.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from uuid import NAMESPACE_DNS, UUID, uuid5

from .database import Base, IS_SQLITE, SessionLocal, engine
from .models import (
    AmenidadModel,
    CategoriaHabitacionModel,
    InventarioModel,
    MediaModel,
    PropiedadModel,
    ResenaModel,
)


@dataclass(frozen=True)
class CatalogSeedRow:
    property_name: str
    stars: int
    city: str
    state: str
    country: str
    lat: float
    lng: float
    tax_percent: Decimal
    search_category_name: str
    commercial_name: str
    description: str

    price: Decimal
    service_fee: Decimal

    # NUEVO 👇
    weekend_price: Decimal
    weekend_fee: Decimal
    high_season_price: Decimal
    high_season_fee: Decimal

    capacity: int
    cancel_days: int
    penalty_percent: Decimal
    amenities: tuple[tuple[str, str, str], ...]
    media_urls: tuple[str, ...]


SEED_ROWS: tuple[CatalogSeedRow, ...] = (
    CatalogSeedRow(
        property_name="Hotel Boutique Las Palmas",
        stars=5,
        city="Cartagena",
        state="Bolivar",
        country="Colombia",
        lat=10.3910,
        lng=-75.5346,
        tax_percent=Decimal("19.00"),
        search_category_name="Hotel",
        commercial_name="Hotel Premium Vista Mar",
        description="Habitacion premium con balcon y amenities completas.",
        price=Decimal("450000"),
        service_fee=Decimal("25000"),
        weekend_price=Decimal("517500"),
        weekend_fee=Decimal("27500"),
        high_season_price=Decimal("585000"),
        high_season_fee=Decimal("30000"),
        capacity=4,
        cancel_days=5,
        penalty_percent=Decimal("35.00"),
        amenities=(
            ("wifi", "WiFi", "wifi"),
            ("pool", "Piscina", "pool"),
            ("spa", "Spa", "spa"),
        ),
        media_urls=(
            "https://cdn.travelhub.example/hotel-las-palmas-1.jpg",
            "https://cdn.travelhub.example/hotel-las-palmas-2.jpg",
        ),
    ),
    CatalogSeedRow(
        property_name="Hostal El Viajero",
        stars=3,
        city="Bogota",
        state="Cundinamarca",
        country="Colombia",
        lat=4.6097,
        lng=-74.0817,
        tax_percent=Decimal("19.00"),
        search_category_name="Hostal",
        commercial_name="Hostal Centro Compartido",
        description="Habitacion funcional para viajeros urbanos.",
        price=Decimal("85000"),
        service_fee=Decimal("5000"),
        weekend_price=Decimal("97750"),
        weekend_fee=Decimal("5500"),
        high_season_price=Decimal("110500"),
        high_season_fee=Decimal("6000"),
        capacity=2,
        cancel_days=2,
        penalty_percent=Decimal("20.00"),
        amenities=(
            ("wifi", "WiFi", "wifi"),
            ("kitchen", "Cocina compartida", "kitchen"),
            ("laundry", "Lavanderia", "laundry"),
        ),
        media_urls=(
            "https://cdn.travelhub.example/hostal-viajero-1.jpg",
            "https://cdn.travelhub.example/hostal-viajero-2.jpg",
        ),
    ),
    CatalogSeedRow(
        property_name="Cabana Montana Magica",
        stars=4,
        city="Medellin",
        state="Antioquia",
        country="Colombia",
        lat=6.2442,
        lng=-75.5812,
        tax_percent=Decimal("19.00"),
        search_category_name="Cabana",
        commercial_name="Cabana Familiar Bosque",
        description="Cabana privada rodeada de naturaleza.",
        price=Decimal("220000"),
        service_fee=Decimal("12000"),
        weekend_price=Decimal("253000"),
        weekend_fee=Decimal("13200"),
        high_season_price=Decimal("286000"),
        high_season_fee=Decimal("14400"),
        capacity=6,
        cancel_days=4,
        penalty_percent=Decimal("30.00"),
        amenities=(
            ("fireplace", "Chimenea", "fire"),
            ("bbq", "BBQ", "grill"),
            ("garden", "Jardin", "leaf"),
        ),
        media_urls=(
            "https://cdn.travelhub.example/cabana-magica-1.jpg",
            "https://cdn.travelhub.example/cabana-magica-2.jpg",
        ),
    ),
    CatalogSeedRow(
        property_name="Resort Playa Dorada",
        stars=5,
        city="Santa Marta",
        state="Magdalena",
        country="Colombia",
        lat=11.2408,
        lng=-74.1990,
        tax_percent=Decimal("19.00"),
        search_category_name="Resort",
        commercial_name="Suite Resort Todo Incluido",
        description="Suite all-inclusive con acceso a playa privada.",
        price=Decimal("680000"),
        service_fee=Decimal("35000"),
        weekend_price=Decimal("782000"),
        weekend_fee=Decimal("38500"),
        high_season_price=Decimal("884000"),
        high_season_fee=Decimal("42000"),
        capacity=8,
        cancel_days=7,
        penalty_percent=Decimal("40.00"),
        amenities=(
            ("private-beach", "Playa privada", "beach"),
            ("pool", "Piscina", "pool"),
            ("spa", "Spa", "spa"),
        ),
        media_urls=(
            "https://cdn.travelhub.example/resort-playa-dorada-1.jpg",
            "https://cdn.travelhub.example/resort-playa-dorada-2.jpg",
        ),
    ),
    CatalogSeedRow(
        property_name="Apartamento Centro Historico",
        stars=4,
        city="Cartagena",
        state="Bolivar",
        country="Colombia",
        lat=10.4236,
        lng=-75.5490,
        tax_percent=Decimal("19.00"),
        search_category_name="Apartamento",
        commercial_name="Apto Centro Historico Deluxe",
        description="Apartamento completo con cocina y balcon.",
        price=Decimal("320000"),
        service_fee=Decimal("18000"),
        weekend_price=Decimal("368000"),
        weekend_fee=Decimal("19800"),
        high_season_price=Decimal("416000"),
        high_season_fee=Decimal("21600"),
        capacity=5,
        cancel_days=3,
        penalty_percent=Decimal("25.00"),
        amenities=(
            ("wifi", "WiFi", "wifi"),
            ("kitchen", "Cocina", "kitchen"),
            ("balcony", "Balcon", "balcony"),
        ),
        media_urls=(
            "https://cdn.travelhub.example/apto-centro-historico-1.jpg",
            "https://cdn.travelhub.example/apto-centro-historico-2.jpg",
        ),
    ),
    CatalogSeedRow(
        property_name="Finca Cafetera La Esperanza",
        stars=4,
        city="Armenia",
        state="Quindio",
        country="Colombia",
        lat=4.5339,
        lng=-75.6811,
        tax_percent=Decimal("19.00"),
        search_category_name="Finca",
        commercial_name="Finca Cafetera Familiar",
        description="Finca rural con experiencia cafetera.",
        price=Decimal("195000"),
        service_fee=Decimal("9000"),
        weekend_price=Decimal("224250"),
        weekend_fee=Decimal("9900"),
        high_season_price=Decimal("253500"),
        high_season_fee=Decimal("10800"),
        capacity=10,
        cancel_days=4,
        penalty_percent=Decimal("30.00"),
        amenities=(
            ("coffee-tour", "Tour de cafe", "coffee"),
            ("pool", "Piscina", "pool"),
            ("nature", "Naturaleza", "leaf"),
        ),
        media_urls=(
            "https://cdn.travelhub.example/finca-esperanza-1.jpg",
            "https://cdn.travelhub.example/finca-esperanza-2.jpg",
        ),
    ),
)


def _build_category_id(search_category_name: str) -> UUID:
    return uuid5(NAMESPACE_DNS, f"categoria:{search_category_name}")


def _build_property_id(property_name: str) -> UUID:
    return uuid5(NAMESPACE_DNS, f"catalog:propiedad:{property_name}")


def run_local_seed() -> None:
    if not IS_SQLITE:
        print("[CATALOG] Local seed skipped (database is not SQLite).")
        return

    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        today = date.today()

        session.execute(CategoriaHabitacionModel.amenidades.property.secondary.delete())
        session.query(ResenaModel).delete()
        session.query(InventarioModel).delete()
        session.query(MediaModel).delete()
        session.query(CategoriaHabitacionModel).delete()
        session.query(PropiedadModel).delete()
        session.query(AmenidadModel).delete()

        amenidades_cache: dict[str, AmenidadModel] = {}

        for row_index, row in enumerate(SEED_ROWS):
            property_id = _build_property_id(row.property_name)
            category_id = _build_category_id(row.search_category_name)

            propiedad = PropiedadModel(
                id_propiedad=property_id,
                nombre=row.property_name,
                estrellas=row.stars,
                ciudad=row.city,
                estado_provincia=row.state,
                pais=row.country,
                latitud=row.lat,
                longitud=row.lng,
                porcentaje_impuesto=row.tax_percent,
            )
            session.add(propiedad)

            categoria = CategoriaHabitacionModel(
                id_categoria=category_id,
                id_propiedad=property_id,
                codigo_mapeo_pms=f"CAT-{row.search_category_name.upper()}-{row_index + 1:02d}",
                nombre_comercial=row.commercial_name,
                descripcion=row.description,
                precio_base_monto=row.price,
                precio_base_moneda="COP",
                precio_base_cargo_servicio=row.service_fee,

                tarifa_fin_de_semana_monto=row.weekend_price,
                tarifa_fin_de_semana_moneda="COP",
                tarifa_fin_de_semana_cargo_servicio=row.weekend_fee,

                tarifa_temporada_alta_monto=row.high_season_price,
                tarifa_temporada_alta_moneda="COP",
                tarifa_temporada_alta_cargo_servicio=row.high_season_fee,

                capacidad_pax=row.capacity,
                dias_anticipacion=row.cancel_days,
                porcentaje_penalidad=row.penalty_percent,
            )
            session.add(categoria)

            amenidad_models: list[AmenidadModel] = []
            for amenity_code, amenity_name, amenity_icon in row.amenities:
                amenity_id = f"amenity-{amenity_code}"
                amenidad = amenidades_cache.get(amenity_id)
                if amenidad is None:
                    amenidad = AmenidadModel(
                        id_amenidad=amenity_id,
                        nombre=amenity_name,
                        icono=amenity_icon,
                    )
                    session.add(amenidad)
                    amenidades_cache[amenity_id] = amenidad
                amenidad_models.append(amenidad)

            categoria.amenidades = amenidad_models
            categoria.media = [
                MediaModel(
                    id_media=f"media-{category_id}-{media_index + 1}",
                    id_categoria=category_id,
                    url_full=url,
                    tipo="FOTO_PORTADA" if media_index == 0 else "IMAGEN_GALERIA",
                    orden=media_index + 1,
                )
                for media_index, url in enumerate(row.media_urls)
            ]

            categoria.inventario = [
                InventarioModel(
                    id_inventario=f"inv-{category_id}-{day_offset + 1}",
                    id_categoria=category_id,
                    fecha=(today + timedelta(days=day_offset)).isoformat(),
                    cupos_totales=max(2, row.capacity + 1),
                    cupos_disponibles=max(1, row.capacity - (day_offset % 2)),
                )
                for day_offset in range(30)
            ]

            review = ResenaModel(
                id_resena=uuid5(NAMESPACE_DNS, f"resena:{property_id}"),
                id_propiedad=property_id,
                id_usuario=uuid5(NAMESPACE_DNS, f"usuario:{row.search_category_name}"),
                nombre_autor=f"Seed User {row.search_category_name}",
                avatar_url=None,
                calificacion=min(5, max(1, row.stars)),
                comentario=f"Resena seed para {row.property_name}.",
                fecha_creacion=datetime.now(timezone.utc),
            )
            session.add(review)

        session.commit()
        print(f"[CATALOG] Seed completado con {len(SEED_ROWS)} propiedades.")

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run_local_seed()