"""Seed inicial del catálogo usando MISMA data del seed local pero via commands."""

from decimal import Decimal
from uuid import UUID, uuid5, NAMESPACE_DNS

from sqlalchemy.exc import IntegrityError

from modules.catalog.infrastructure.database import SessionLocal
from modules.catalog.infrastructure.models import ConfiguracionImpuestosPaisModel
from modules.catalog.infrastructure.repository import PropertyRepository
from modules.catalog.infrastructure.services.event_bus import EventBus
from modules.catalog.infrastructure.local_seed import SEED_ROWS, SEED_TAXES
from modules.catalog.application.commands.create_property import CreateProperty
from modules.catalog.application.commands.register_category_housing import RegisterCategoryHousing
from modules.catalog.application.commands.update_pricing import UpdatePricing


def _build_property_id(property_name: str) -> UUID:
    return uuid5(NAMESPACE_DNS, f"catalog:propiedad:{property_name}")


def _build_category_id(search_category_name: str) -> UUID:
    return uuid5(NAMESPACE_DNS, f"categoria:{search_category_name}")


def _codigos_existentes(repository: PropertyRepository, id_propiedad: UUID) -> set[str]:
    propiedad = repository.obtain(id_propiedad)
    if not propiedad:
        return set()
    return {cat.codigo_mapeo_pms for cat in propiedad.categorias_habitacion}


def run_seed() -> None:
    repository = PropertyRepository()
    event_bus = EventBus()

    create_cmd = CreateProperty(repository, event_bus)
    register_cmd = RegisterCategoryHousing(repository, event_bus)
    pricing_cmd = UpdatePricing(repository, event_bus)

    session = SessionLocal()
    try:
        if session.query(ConfiguracionImpuestosPaisModel).count() == 0:
            for row in SEED_TAXES:
                session.add(ConfiguracionImpuestosPaisModel(
                    pais=row["pais"],
                    moneda=row["moneda"],
                    simbolo_moneda=row["simbolo"],
                    locale=row["locale"],
                    decimales=row["decimales"],
                    tasa_usd=Decimal(str(row["tasa_usd"])),
                    impuesto_nombre=row["impuesto"],
                    impuesto_tasa=Decimal(str(row["tasa"])),
                ))
            session.commit()
            print("[seed] Configuracion de impuestos insertada.")
    except Exception as exc:
        session.rollback()
        print(f"[seed] Error insertando impuestos: {exc}")
    finally:
        session.close()

    for index, row in enumerate(SEED_ROWS):
        property_id = _build_property_id(row.property_name)
        category_id = _build_category_id(row.search_category_name)

        # ── PROPIEDAD ───────────────────────────────────────────────
        result = create_cmd.execute(
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

        if result.get("message") == "Property already exists":
            print(f"[seed] Propiedad {row.property_name} ya existe.")
        else:
            print(f"[seed] Propiedad {row.property_name} creada.")

        # ── CATEGORÍA ───────────────────────────────────────────────
        codigo = f"CAT-{row.search_category_name.upper()}-{index + 1:02d}"

        existentes = _codigos_existentes(repository, property_id)
        if codigo in existentes:
            print(f"[seed]   Categoría {codigo} ya existe.")
            continue

        try:
            result = register_cmd.execute(
                id_propiedad=property_id,
                codigo_mapeo_pms=codigo,
                nombre_comercial=row.commercial_name,
                descripcion=row.description,
                monto_precio_base=row.price,
                cargo_servicio=row.service_fee,
                moneda_precio_base="COP",
                capacidad_pax=row.capacity,
                dias_anticipacion=row.cancel_days,
                porcentaje_penalidad=row.penalty_percent,
                foto_portada_url=row.media_urls[0],
            )

            if "error" in result:
                print(f"[seed] Error: {result['error']}")
                continue

            id_categoria = UUID(result["id_categoria"])

            # ── PRICING (MISMA INFO EXACTA) ───────────────────────────
            pricing_cmd.execute(
                id_propiedad=property_id,
                id_categoria=id_categoria,

                tarifa_base_monto=row.price,
                moneda="COP",
                cargo_servicio=row.service_fee,

                tarifa_fin_de_semana_monto=row.weekend_price,
                tarifa_fin_de_semana_moneda="COP",
                tarifa_fin_de_semana_cargo_servicio=row.weekend_fee,

                tarifa_temporada_alta_monto=row.high_season_price,
                tarifa_temporada_alta_moneda="COP",
                tarifa_temporada_alta_cargo_servicio=row.high_season_fee,
            )

            print(f"[seed]   Categoría {row.commercial_name} creada con tarifas completas.")

        except IntegrityError:
            print(f"[seed]   Categoría {codigo} ya existe (constraint).")

    _seed_temporadas(repository)


# ── Temporadas de precio ───────────────────────────────────────────────────────
# IDs de las propiedades derivados con la misma fórmula que usa run_seed().
HOTEL1_ID: UUID = _build_property_id("Hotel Boutique Las Palmas")
HOTEL2_ID: UUID = _build_property_id("Hostal El Viajero")

# UUIDs deterministas derivados del nombre de la temporada + hotel para que el
# seed sea idempotente sin necesidad de consultar la BD primero.

TEMPORADAS: list[dict] = [
    # Hotel 1 – Bogotá
    {
        "id_propiedad": HOTEL1_ID,
        "nombre": "Verano",
        "fecha_inicio": "2026-06-01",
        "fecha_fin": "2026-08-31",
        "porcentaje": "25.00",
    },
    {
        "id_propiedad": HOTEL1_ID,
        "nombre": "Navidad",
        "fecha_inicio": "2026-12-15",
        "fecha_fin": "2027-01-05",
        "porcentaje": "40.00",
    },
    {
        "id_propiedad": HOTEL1_ID,
        "nombre": "Mitad de año",
        "fecha_inicio": "2026-06-15",
        "fecha_fin": "2026-07-15",
        "porcentaje": "30.00",
    },
    # Hotel 2 – Medellín
    {
        "id_propiedad": HOTEL2_ID,
        "nombre": "Feria de las Flores",
        "fecha_inicio": "2026-07-28",
        "fecha_fin": "2026-08-10",
        "porcentaje": "35.00",
    },
    {
        "id_propiedad": HOTEL2_ID,
        "nombre": "Temporada Navideña",
        "fecha_inicio": "2026-12-20",
        "fecha_fin": "2027-01-06",
        "porcentaje": "45.00",
    },
    {
        "id_propiedad": HOTEL2_ID,
        "nombre": "Semana Santa",
        "fecha_inicio": "2027-03-28",
        "fecha_fin": "2027-04-06",
        "porcentaje": "30.00",
    },
]


def _seed_temporadas(repository: PropertyRepository) -> None:
    """Inserta temporadas de precio si no existen ya en la BD."""
    from modules.catalog.infrastructure.database import SessionLocal
    from modules.catalog.infrastructure.models import TemporadaModel
    from decimal import Decimal as Dec

    db = SessionLocal()
    try:
        for t in TEMPORADAS:
            id_temporada = uuid5(NAMESPACE_DNS, f"{t['id_propiedad']}-{t['nombre']}-{t['fecha_inicio']}")
            existe = db.query(TemporadaModel).filter(
                TemporadaModel.id_temporada == id_temporada
            ).first()
            if existe:
                print(f"[seed]   Temporada '{t['nombre']}' ({t['id_propiedad']}) ya existe, omitiendo.")
                continue
            db.add(TemporadaModel(
                id_temporada=id_temporada,
                id_propiedad=t["id_propiedad"],
                nombre=t["nombre"],
                fecha_inicio=t["fecha_inicio"],
                fecha_fin=t["fecha_fin"],
                porcentaje=Dec(t["porcentaje"]),
            ))
            print(f"[seed]   Temporada '{t['nombre']}' creada para propiedad {t['id_propiedad']}.")
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[seed] Error en seed de temporadas: {e}")
    finally:
        db.close()
