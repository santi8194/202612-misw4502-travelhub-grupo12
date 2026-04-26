import os
import sys
import threading

from sqlalchemy import inspect, text

from config.app import create_app
from modules.catalog.infrastructure import models
from modules.catalog.infrastructure.database import Base, engine, IS_SQLITE
from modules.catalog.infrastructure.services.consumer import start_consumer
from modules.catalog.infrastructure.seed import run_seed

app = create_app()


def _recreate_sqlite_if_legacy_schema() -> None:
    """Recrea schema SQLite local cuando detecta columnas nuevas faltantes.

    Esto evita fallos al arrancar después de cambios de modelo sobre una DB
    local persistida en volúmenes Docker.
    """
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    if "categorias_habitacion" not in tables:
        return

    current_columns = {
        column["name"] for column in inspector.get_columns("categorias_habitacion")
    }
    required_columns = {
        "tarifa_fin_de_semana_monto",
        "tarifa_fin_de_semana_moneda",
        "tarifa_fin_de_semana_cargo_servicio",
        "tarifa_temporada_alta_monto",
        "tarifa_temporada_alta_moneda",
        "tarifa_temporada_alta_cargo_servicio",
    }

    if not required_columns.issubset(current_columns):
        print("[CATALOG] Legacy SQLite schema detected, recreating local database schema...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)


def _ensure_legacy_schema_compatibility() -> None:
    """Corrige diferencias simples de esquema en bases legadas."""
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    if "propiedades" not in tables:
        return

    property_columns = {column["name"] for column in inspector.get_columns("propiedades")}
    has_estado_provincia = "estado_provincia" in property_columns

    with engine.begin() as connection:
        if not has_estado_provincia:
            print("[CATALOG] Legacy schema detected (missing propiedades.estado_provincia), applying compatibility fix...")
            if IS_SQLITE:
                Base.metadata.drop_all(bind=connection)
                Base.metadata.create_all(bind=connection)
                return

            connection.execute(
                text("ALTER TABLE propiedades ADD COLUMN estado_provincia VARCHAR")
            )

        connection.execute(
            text(
                "UPDATE propiedades "
                "SET estado_provincia = ciudad "
                "WHERE estado_provincia IS NULL OR estado_provincia = ''"
            )
        )

# Crear tablas locales solo cuando se usa SQLite de desarrollo.
# Se omite durante pytest para evitar que PgUUID falle al compilar en SQLite.
if IS_SQLITE and "pytest" not in sys.modules:
    Base.metadata.create_all(bind=engine)
    _recreate_sqlite_if_legacy_schema()

_ensure_legacy_schema_compatibility()

# Evita efectos colaterales durante colección de pruebas en CI/pytest.
# En SQLite local, el entrypoint ya ejecuta `local_seed` determinístico y
# compatible con Search; evitar `run_seed` para no mezclar IDs aleatorios.
if "pytest" not in sys.modules and not IS_SQLITE:
    run_seed()

ENABLE_EVENTS = os.getenv("ENABLE_EVENTS", "false").lower() == "true"


@app.on_event("startup")
def start_rabbitmq_consumer():
    if not ENABLE_EVENTS:
        print("[CATALOG] ENABLE_EVENTS=false, skipping RabbitMQ consumer")
        return

    thread = threading.Thread(target=start_consumer)
    thread.daemon = True
    thread.start()
