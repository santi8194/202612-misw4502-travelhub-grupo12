"""Mock PMS — Simulador de sistema externo de gestión hotelera.

Este servicio simula un PMS (Property Management System) externo para
pruebas locales de integración. Expone dos endpoints:

- GET  /api/inventory/changes?since={iso_timestamp}  → Polling de deltas
- POST /force-webhook                                  → Fuerza un push a pms-integration

IMPORTANTE: Este servicio es exclusivo para desarrollo local.
            No se despliega en Kubernetes / producción.
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock-pms")

app = FastAPI(title="Mock PMS", description="Simulador local de PMS externo para TravelHub")

# URL del servicio pms-integration (en docker-compose la alcanza por nombre de servicio)
PMS_INTEGRATION_URL = os.getenv("PMS_INTEGRATION_URL", "http://pms-integration:8001")

# Archivo de inventario simulado
DATA_FILE = Path(__file__).parent / "data" / "inventory_100.json"


def _load_inventory() -> list[dict]:
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
        return data["inventory"] if isinstance(data, dict) else data


@app.get("/health")
def health():
    return {"status": "ok", "service": "mock-pms"}


@app.get("/api/inventory/changes")
def get_inventory_changes(
    since: Optional[str] = Query(
        default=None,
        description="ISO 8601 timestamp. Solo devuelve cambios posteriores a esta fecha."
    )
):
    """Endpoint de polling. pms-integration lo llama cada 2 minutos.

    Filtra los registros cuyo `last_modified` sea posterior al timestamp `since`.
    Si `since` es None, devuelve todos los registros (primera llamada).
    """
    inventory = _load_inventory()

    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
            changes = [
                item for item in inventory
                if datetime.fromisoformat(
                    item["last_modified"].replace("Z", "+00:00")
                ) > since_dt
            ]
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Formato de 'since' inválido: {since}")
    else:
        changes = inventory

    logger.info(f"[POLL] Respondiendo {len(changes)} cambios (since={since})")
    return {
        "provider": "mock-pms",
        "queried_at": datetime.now(timezone.utc).isoformat(),
        "changes": changes,
    }


@app.post("/force-webhook")
async def force_webhook(hotel_code: str = "CAT-HOTEL-01", cupos: int = 0):
    """Dispara manualmente un webhook hacia pms-integration.

    Útil para simular en Postman que un hotel marca una habitación como ocupada.
    El payload usa el formato que el adaptador MockPMS espera.

    Parámetros:
        hotel_code: código de hotel del inventario (ej: CAT-HOTEL-01)
        cupos: cupos disponibles a reportar (0 = habitación llena)
    """
    inventory = _load_inventory()

    # Buscar el item del hotel indicado
    item = next((i for i in inventory if i["hotel_code"] == hotel_code), None)
    if not item:
        raise HTTPException(status_code=404, detail=f"Hotel code '{hotel_code}' no encontrado en inventario")

    webhook_payload = {
        "hotel_code": item["hotel_code"],
        "room_type_code": item["room_type_code"],
        "date": item["date"],
        "available_units": cupos,
        "last_modified": datetime.now(timezone.utc).isoformat(),
    }

    webhook_url = f"{PMS_INTEGRATION_URL}/api/webhooks/inventory"
    logger.info(f"[WEBHOOK] Disparando hacia {webhook_url}: {webhook_payload}")

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(
                webhook_url,
                json=webhook_payload,
                headers={"X-PMS-Provider": "mock", "Content-Type": "application/json"},
            )
            return JSONResponse(
                status_code=200,
                content={
                    "status": "webhook_dispatched",
                    "target_url": webhook_url,
                    "payload_sent": webhook_payload,
                    "pms_integration_response": response.status_code,
                },
            )
        except httpx.ConnectError:
            raise HTTPException(
                status_code=503,
                detail=f"No se pudo conectar con pms-integration en {webhook_url}",
            )
