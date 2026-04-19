from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.router import router

def create_app():
    app = FastAPI(title="Catalog Service")

    # Política CORS para permitir llamadas desde el frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)
    app.include_router(router, prefix="/catalog")
    return app
