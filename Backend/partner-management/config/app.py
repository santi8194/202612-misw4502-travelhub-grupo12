def create_app():
    """
    Función de fábrica (Factory) que crea e inicializa la aplicación FastAPI.
    """
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    import threading
    from modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer import start_consumer
    from modules.partner.infrastructure.api import router as partner_router

    # Instanciamos la API y le damos un título
    app = FastAPI(title="PartnerManagement Service")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(partner_router)

    # Endpoint de verificación de salud (health check). Muy util en Docker/Kubernetes.
    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    # Evento que se ejecuta automáticamente cuando FastAPI termina de iniciar
    @app.on_event("startup")
    def startup_event():
        # Iniciamos el consumidor de RabbitMQ en un "Hilo" (Thread) en segundo plano
        # Esto permite que la API de FastAPI (puerto 8000) pueda seguir aceptando peticiones
        # mientras el consumidor se queda ejecutando por detrás escuchando los mensajes.
        consumer_thread = threading.Thread(target=start_consumer, daemon=True)
        consumer_thread.start()

    return app

