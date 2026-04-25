"""
Proposito del archivo: Punto de entrada principal para el microservicio de autenticacion.
Rol dentro del microservicio: Inicializa la aplicacion FastAPI, configura middlewares (CORS) y registra los enrutadores principales de la API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import auth
from config.config import settings
from infrastructure.database import IS_SQLITE, init_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Microservicio de Autenticacion para la plataforma hotelera.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["auth"])


@app.on_event("startup")
def startup() -> None:
    """Inicializa el esquema local cuando el servicio corre con SQLite."""
    if IS_SQLITE:
        init_db()


@app.get("/health")
@app.get("/auth/health")
def health_check():
    """Endpoint de salud para readiness/liveness probes."""
    return {"status": "ok"}


@app.get("/")
def root():
    """Endpoint de bienvenida y comprobacion de salud basica."""
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
