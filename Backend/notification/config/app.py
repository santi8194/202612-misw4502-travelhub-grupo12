
from fastapi import FastAPI
import threading
from api.health import router as health_router
from api.notifications import router as notifications_router
from api.reservation_notifications import router as reservation_notifications_router
from modules.consumers.reserva_confirmada_consumer import start_consumer
from config.firebase import initialize_firebase

def create_app():
    initialize_firebase()
    app = FastAPI(title="Notification Service")
    app.include_router(health_router)
    app.include_router(notifications_router)
    app.include_router(reservation_notifications_router)

    @app.on_event("startup")
    def startup_event():
        consumer_thread = threading.Thread(target=start_consumer, daemon=True)
        consumer_thread.start()

    return app
