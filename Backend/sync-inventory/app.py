from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.bootstrap import ServiceContainer, build_container
from src.config import Settings
from src.controllers.health_controller import router as health_router
from src.controllers.sync_controller import router as sync_router

SERVICE_NAME = "sync-inventory"


def healthcheck() -> str:
    return "ok"


def create_app(
    settings: Settings | None = None,
    container: ServiceContainer | None = None,
) -> FastAPI:
    resolved_container = container or build_container(settings=settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.container = resolved_container
        await resolved_container.scheduler.start()
        try:
            yield
        finally:
            await resolved_container.scheduler.stop()
            close = getattr(resolved_container.inventory_publisher, "close", None)
            if close is not None:
                await close()

    app = FastAPI(
        title="SyncInventory",
        version="1.0.0",
        description=(
            "Servicio de integracion que simula PMS externos, transforma datos "
            "y envia comandos de sincronizacion al InventoryService."
        ),
        lifespan=lifespan,
    )
    app.include_router(health_router)
    app.include_router(sync_router)
    return app


app = create_app()
