import os
import threading

from config.app import create_app
from modules.catalog.infrastructure import models
from modules.catalog.infrastructure.services.consumer import start_consumer
from data.seed import run_seed

app = create_app()
# Crear todas las tablas al inicio (idempotente: no recrea las existentes).
Base.metadata.create_all(bind=engine)

# Poblar la BD con las propiedades y categorías de demostración si no existen.
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
