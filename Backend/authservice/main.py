"""
Propósito del archivo: Punto de entrada principal para el microservicio de autenticación.
Rol dentro del microservicio: Inicializa la aplicación FastAPI, configura middlewares (CORS) y registra los enrutadores principales de la API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import auth
from config.config import settings

# Inicialización de la aplicación FastAPI con metadata general
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Microservicio de Autenticación para la plataforma hotelera.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuración del middleware CORS para aceptar conexiones desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite cualquier origen (frontend, otros servicios)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permite cualquier encabezado personalizado
)

# Inclusión del enrutador de autenticación bajo el prefijo definido en la configuración
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["auth"])


# Endpoint /health para probes de Kubernetes
@app.get("/health")
def health_check():
    """
    Endpoint de salud para Kubernetes (readiness/liveness probe).
    Retorna 200 si el servicio está corriendo.
    """
    return {"status": "ok"}


@app.get("/")
def root():
    """
    Endpoint de bienvenida y comprobación de salud básica.

    Retorna:
    - dict: Mensaje de bienvenida indicando que el servicio está activo.
    """
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
