import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from modules.partner.infrastructure.publishers.aprobacion_publisher import (
    publish_reserva_aprobada,
)

router = APIRouter(prefix="/partner", tags=["partner"])


class AprobarReservaRequest(BaseModel):
    id_usuario_admin: str


@router.post("/reserva/{id_reserva}/aprobar", status_code=200)
def aprobar_reserva(id_reserva: str, body: AprobarReservaRequest):
    """
    Endpoint llamado desde el portal del hotel para aprobar manualmente una reserva.
    Publica un evento de integración ReservaAprobadaManualEvt con formato CloudEvents 1.0.
    """
    try:
        publish_reserva_aprobada(
            id_reserva=id_reserva,
            id_usuario_admin=body.id_usuario_admin,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail="No se pudo publicar el evento") from exc

    return {
        "message": "Reserva aprobada. Evento publicado.",
        "id_reserva": id_reserva,
        "id_usuario_admin": body.id_usuario_admin,
    }
