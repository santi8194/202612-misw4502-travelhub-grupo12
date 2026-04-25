"""Seed inicial del catálogo usando MISMA data del seed local pero via commands."""

from decimal import Decimal
from uuid import UUID, uuid5, NAMESPACE_DNS

from sqlalchemy.exc import IntegrityError

from modules.catalog.infrastructure.repository import PropertyRepository
from modules.catalog.infrastructure.services.event_bus import EventBus
from modules.catalog.application.commands.create_property import CreateProperty
from modules.catalog.application.commands.register_category_housing import RegisterCategoryHousing
from modules.catalog.application.commands.update_pricing import UpdatePricing


def _build_property_id(property_name: str) -> UUID:
    return uuid5(NAMESPACE_DNS, f"catalog:propiedad:{property_name}")


def _build_category_id(search_category_name: str) -> UUID:
    return uuid5(NAMESPACE_DNS, f"categoria:{search_category_name}")


# 👇 MISMA DATA (resumida aquí pero debes copiarla EXACTA desde el otro archivo)
from modules.catalog.infrastructure.local_seed import SEED_ROWS


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
