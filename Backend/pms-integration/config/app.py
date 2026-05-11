from fastapi import FastAPI
from api.router import router

def create_app():
    app = FastAPI(title="PMS Integration Service")

    @app.get("/health")
    def health_check():
        return {"status": "ok", "service": "pms-integration"}

    app.include_router(router, prefix="/api")
    return app