
from fastapi import FastAPI
import threading
from api.health import router as health_router
from modules.consumers.reserva_confirmada_consumer import start_consumer

def create_app():
    app = FastAPI(title="Notification Service")
    app.include_router(health_router)

    @app.on_event("startup")
    def startup_event():
        consumer_thread = threading.Thread(target=start_consumer, daemon=True)
        consumer_thread.start()

    return app
