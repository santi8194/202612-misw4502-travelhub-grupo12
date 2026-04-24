"""Seed inicial del catálogo de propiedades.

Crea las propiedades y categorías de los hoteles de demostración cuyo UUID
coincide con el campo partner_id que el auth-service asigna a los usuarios
admin@hotel1.com y admin@hotel2.com.

Este módulo es idempotente: si los datos ya existen no se vuelven a insertar.
"""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from modules.catalog.infrastructure.repository import PropertyRepository
from modules.catalog.infrastructure.services.event_bus import EventBus
from modules.catalog.application.commands.create_property import CreateProperty
from modules.catalog.application.commands.register_category_housing import RegisterCategoryHousing
from modules.catalog.application.commands.update_pricing import UpdatePricing

# ── UUIDs que el auth-service asigna como partner_id ──────────────────────────
HOTEL1_ID = UUID("cc0e8400-e29b-41d4-a716-446655440001")
HOTEL2_ID = UUID("cc0e8400-e29b-41d4-a716-446655440002")

# ── Definición de las propiedades de demostración ─────────────────────────────
PROPIEDADES = [
    {
        "id_propiedad": HOTEL1_ID,
        "nombre": "Hotel Ciudad TravelHub",
        "estrellas": 4,
        "ciudad": "Bogotá",
        "estado_provincia": "Cundinamarca",
        "pais": "Colombia",
        "latitud": 4.6534,
        "longitud": -74.0836,
        "porcentaje_impuesto": Decimal("19.00"),
    },
    {
        "id_propiedad": HOTEL2_ID,
        "nombre": "Hotel Sierra TravelHub",
        "estrellas": 5,
        "ciudad": "Medellín",
        "estado_provincia": "Antioquia",
        "pais": "Colombia",
        "latitud": 6.2442,
        "longitud": -75.5812,
        "porcentaje_impuesto": Decimal("19.00"),
    },
]

# ── Categorías de habitación por propiedad ────────────────────────────────────
CATEGORIAS_HOTEL1 = [
    {
        "codigo_mapeo_pms": "H1-STD",
        "nombre_comercial": "Habitación Estándar",
        "descripcion": "Habitación cómoda con todas las comodidades básicas.",
        "monto_precio_base": Decimal("280000"),
        "cargo_servicio": Decimal("0"),
        "moneda_precio_base": "COP",
        "capacidad_pax": 2,
        "dias_anticipacion": 3,
        "porcentaje_penalidad": Decimal("20.00"),
        "foto_portada_url": "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800",
        "tarifa_fin_de_semana": Decimal("336000"),
        "tarifa_temporada_alta": Decimal("392000"),
    },
    {
        "codigo_mapeo_pms": "H1-DEL",
        "nombre_comercial": "Suite Deluxe",
        "descripcion": "Suite espaciosa con vista a la ciudad y jacuzzi.",
        "monto_precio_base": Decimal("450000"),
        "cargo_servicio": Decimal("0"),
        "moneda_precio_base": "COP",
        "capacidad_pax": 2,
        "dias_anticipacion": 5,
        "porcentaje_penalidad": Decimal("30.00"),
        "foto_portada_url": "https://images.unsplash.com/photo-1618773928121-c32242e63f39?w=800",
        "tarifa_fin_de_semana": Decimal("540000"),
        "tarifa_temporada_alta": Decimal("630000"),
    },
    {
        "codigo_mapeo_pms": "H1-EJE",
        "nombre_comercial": "Suite Ejecutiva",
        "descripcion": "Suite ejecutiva con sala de reuniones y bar privado.",
        "monto_precio_base": Decimal("620000"),
        "cargo_servicio": Decimal("0"),
        "moneda_precio_base": "COP",
        "capacidad_pax": 3,
        "dias_anticipacion": 7,
        "porcentaje_penalidad": Decimal("40.00"),
        "foto_portada_url": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800",
        "tarifa_fin_de_semana": Decimal("744000"),
        "tarifa_temporada_alta": Decimal("868000"),
    },
    {
        "codigo_mapeo_pms": "H1-PRE",
        "nombre_comercial": "Suite Presidencial",
        "descripcion": "La mejor suite del hotel con terraza panorámica.",
        "monto_precio_base": Decimal("980000"),
        "cargo_servicio": Decimal("0"),
        "moneda_precio_base": "COP",
        "capacidad_pax": 4,
        "dias_anticipacion": 10,
        "porcentaje_penalidad": Decimal("50.00"),
        "foto_portada_url": "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800",
        "tarifa_fin_de_semana": Decimal("1176000"),
        "tarifa_temporada_alta": Decimal("1372000"),
    },
]

CATEGORIAS_HOTEL2 = [
    {
        "codigo_mapeo_pms": "H2-STD",
        "nombre_comercial": "Habitación Estándar",
        "descripcion": "Habitación cómoda con todas las comodidades básicas.",
        "monto_precio_base": Decimal("250000"),
        "cargo_servicio": Decimal("0"),
        "moneda_precio_base": "COP",
        "capacidad_pax": 2,
        "dias_anticipacion": 3,
        "porcentaje_penalidad": Decimal("20.00"),
        "foto_portada_url": "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800",
        "tarifa_fin_de_semana": Decimal("300000"),
        "tarifa_temporada_alta": Decimal("350000"),
    },
    {
        "codigo_mapeo_pms": "H2-DEL",
        "nombre_comercial": "Suite Deluxe",
        "descripcion": "Suite espaciosa con vista a la montaña y bañera de lujo.",
        "monto_precio_base": Decimal("420000"),
        "cargo_servicio": Decimal("0"),
        "moneda_precio_base": "COP",
        "capacidad_pax": 2,
        "dias_anticipacion": 5,
        "porcentaje_penalidad": Decimal("30.00"),
        "foto_portada_url": "https://images.unsplash.com/photo-1618773928121-c32242e63f39?w=800",
        "tarifa_fin_de_semana": Decimal("504000"),
        "tarifa_temporada_alta": Decimal("588000"),
    },
    {
        "codigo_mapeo_pms": "H2-EJE",
        "nombre_comercial": "Suite Ejecutiva",
        "descripcion": "Suite ejecutiva con sala privada y servicio de mayordomo.",
        "monto_precio_base": Decimal("590000"),
        "cargo_servicio": Decimal("0"),
        "moneda_precio_base": "COP",
        "capacidad_pax": 3,
        "dias_anticipacion": 7,
        "porcentaje_penalidad": Decimal("40.00"),
        "foto_portada_url": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800",
        "tarifa_fin_de_semana": Decimal("708000"),
        "tarifa_temporada_alta": Decimal("826000"),
    },
    {
        "codigo_mapeo_pms": "H2-PRE",
        "nombre_comercial": "Suite Presidencial",
        "descripcion": "La mejor suite del hotel con piscina privada y terraza.",
        "monto_precio_base": Decimal("900000"),
        "cargo_servicio": Decimal("0"),
        "moneda_precio_base": "COP",
        "capacidad_pax": 4,
        "dias_anticipacion": 10,
        "porcentaje_penalidad": Decimal("50.00"),
        "foto_portada_url": "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800",
        "tarifa_fin_de_semana": Decimal("1080000"),
        "tarifa_temporada_alta": Decimal("1260000"),
    },
]

SEED_DATA: list[tuple[dict, list[dict]]] = [
    (PROPIEDADES[0], CATEGORIAS_HOTEL1),
    (PROPIEDADES[1], CATEGORIAS_HOTEL2),
]


def _codigos_existentes(repository: PropertyRepository, id_propiedad: UUID) -> set[str]:
    """Retorna el conjunto de códigos PMS ya registrados en la propiedad."""
    propiedad = repository.obtain(id_propiedad)
    if not propiedad:
        return set()
    return {cat.codigo_mapeo_pms for cat in propiedad.categorias_habitacion}


def run_seed() -> None:
    """Ejecuta el seed; no lanza excepciones si los datos ya existen."""
    repository = PropertyRepository()
    event_bus = EventBus()
    create_cmd = CreateProperty(repository, event_bus)
    register_cmd = RegisterCategoryHousing(repository, event_bus)
    pricing_cmd = UpdatePricing(repository, event_bus)

    for prop_entry, categorias_data in SEED_DATA:
        id_propiedad: UUID = prop_entry["id_propiedad"]

        result = create_cmd.execute(
            id_propiedad=id_propiedad,
            nombre=prop_entry["nombre"],
            estrellas=prop_entry["estrellas"],
            ciudad=prop_entry["ciudad"],
            estado_provincia=prop_entry["estado_provincia"],
            pais=prop_entry["pais"],
            latitud=prop_entry["latitud"],
            longitud=prop_entry["longitud"],
            porcentaje_impuesto=prop_entry["porcentaje_impuesto"],
        )
        if "message" in result and result["message"] == "Property already exists":
            print(f"[seed] Propiedad {prop_entry['nombre']} ya existe, omitiendo creación.")
        else:
            print(f"[seed] Propiedad {prop_entry['nombre']} creada.")

        codigos_existentes = _codigos_existentes(repository, id_propiedad)

        for cat in categorias_data:
            if cat["codigo_mapeo_pms"] in codigos_existentes:
                print(f"[seed]   Categoría {cat['codigo_mapeo_pms']} ya existe, omitiendo.")
                continue

            try:
                result = register_cmd.execute(
                    id_propiedad=id_propiedad,
                    codigo_mapeo_pms=cat["codigo_mapeo_pms"],
                    nombre_comercial=cat["nombre_comercial"],
                    descripcion=cat["descripcion"],
                    monto_precio_base=cat["monto_precio_base"],
                    cargo_servicio=cat["cargo_servicio"],
                    moneda_precio_base=cat["moneda_precio_base"],
                    capacidad_pax=cat["capacidad_pax"],
                    dias_anticipacion=cat["dias_anticipacion"],
                    porcentaje_penalidad=cat["porcentaje_penalidad"],
                    foto_portada_url=cat["foto_portada_url"],
                )

                if "error" in result:
                    print(f"[seed]   Error registrando {cat['codigo_mapeo_pms']}: {result['error']}")
                    continue

                id_categoria = UUID(result["id_categoria"])
                print(f"[seed]   Categoría {cat['nombre_comercial']} registrada ({id_categoria}).")

                pricing_cmd.execute(
                    id_propiedad=id_propiedad,
                    id_categoria=id_categoria,
                    tarifa_base_monto=cat["monto_precio_base"],
                    moneda=cat["moneda_precio_base"],
                    cargo_servicio=cat["cargo_servicio"],
                    tarifa_fin_de_semana_monto=cat["tarifa_fin_de_semana"],
                    tarifa_temporada_alta_monto=cat["tarifa_temporada_alta"],
                )
                print(f"[seed]   Tarifas diferenciadas aplicadas a {cat['nombre_comercial']}.")

            except IntegrityError:
                print(f"[seed]   Categoría {cat['codigo_mapeo_pms']} ya existe (constraint), omitiendo.")
