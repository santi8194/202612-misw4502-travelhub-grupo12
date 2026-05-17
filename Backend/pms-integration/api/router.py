from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
from modules.pms.infrastructure.repository import ReservationRepository
from modules.pms.infrastructure.services.event_bus import EventBus
from modules.pms.application.commands.confirm_reservation import ConfirmReservation
from modules.pms.application.commands.cancel_reservation import CancelReservation
from modules.pms.application.commands.sync_inventory import SyncInventory
from modules.pms.application.adapters import get_adapter

router = APIRouter()
repository = ReservationRepository()
event_bus = EventBus()


class ReservationRequest(BaseModel):
    id_reserva: str
    id_categoria: str
    id_usuario: str
    fecha_check_in: str
    fecha_check_out: str


class CancelRequest(BaseModel):
    id_reserva: str


@router.post("/confirmar-reserva")
def confirm_reservation(request: ReservationRequest):

    command = ConfirmReservation(repository, event_bus)

    return command.execute(
        request.id_reserva,
        request.id_categoria,
        request.id_usuario,
        request.fecha_check_in,
        request.fecha_check_out,
    )


@router.post("/cancelar-reserva")
def cancel_reservation(request: CancelRequest):

    command = CancelReservation(repository, event_bus)

    return command.execute(request.id_reserva)


class InventoryWebhookPayload(BaseModel):
    """Payload del webhook de inventario del PMS."""
    hotel_code: str
    room_type_code: str
    date: str
    total_units: int
    available_units: int
    last_modified: str


@router.post("/webhooks/inventory")
def receive_inventory_webhook(
    payload: InventoryWebhookPayload,
    x_pms_provider: Optional[str] = Header(default="mock", alias="X-PMS-Provider")
):
    """
    Endpoint webhook para recibir actualizaciones de inventario del PMS.
    
    Headers:
        X-PMS-Provider: Identificador del proveedor PMS (mock, opera, mews, etc.)
    
    Body:
        Payload con los datos del cambio de inventario en formato del PMS
    
    Returns:
        HTTP 202 Accepted con mensaje de confirmación
    """
    try:
        adapter = get_adapter(x_pms_provider)
        
        dto = adapter.normalize_webhook(payload.dict())
        
        sync_command = SyncInventory(event_bus)
        sync_command.execute(dto)
        
        return {
            "status": "accepted",
            "message": "Inventory update queued for processing",
            "provider": x_pms_provider
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"[WEBHOOK] Error procesando webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")