from fastapi import FastAPI
from api.router import router

def create_app():
    app = FastAPI(title="Catalog Service")
    app.include_router(router, prefix="/catalog")
    return app