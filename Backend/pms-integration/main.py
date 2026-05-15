from config.app import create_app
from modules.pms.infrastructure.services.consumer import start_consumer
from modules.pms.infrastructure.services.poller import get_poller

import threading

app = create_app()

@app.on_event("startup")
def start_rabbitmq_consumer():

    thread = threading.Thread(target=start_consumer)
    thread.daemon = True
    thread.start()


@app.on_event("startup")
def start_inventory_poller():
    """Inicia el motor de polling de inventario."""
    poller = get_poller()
    poller.start()
    print("[STARTUP] Inventory poller iniciado")


@app.on_event("shutdown")
def stop_inventory_poller():
    """Detiene el motor de polling."""
    poller = get_poller()
    poller.stop()