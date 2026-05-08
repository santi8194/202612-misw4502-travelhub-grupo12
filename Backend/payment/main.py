import threading
import os

from app import app
from modules.payments.infrastructure.services.consumer import start_consumer


def is_rabbit_enabled() -> bool:
    return os.getenv("ENABLE_RABBIT", "true").lower() in {"1", "true", "yes", "on"}

@app.on_event("startup")
def start_rabbitmq_consumer():
    if not is_rabbit_enabled():
        print("ENABLE_RABBIT=false, skipping RabbitMQ consumer startup.")
        return

    thread = threading.Thread(target=start_consumer)
    thread.daemon = True
    thread.start()
