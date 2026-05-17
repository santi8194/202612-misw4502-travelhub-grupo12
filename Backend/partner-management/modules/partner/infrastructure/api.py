import os
import uuid
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from modules.partner.infrastructure.publishers.aprobacion_publisher import (
    publish_reserva_aprobada,
    publish_reserva_rechazada,
)

router = APIRouter(prefix="/partner", tags=["partner"])

BOOKING_SERVICE_URL = os.getenv("BOOKING_SERVICE_URL", "http://booking:8000/api")


def _validar_estado_pendiente(id_reserva: str) -> None:
    """Consulta booking y lanza 409 si la reserva no está en PENDIENTE o HOLD."""
    try:
        resp = httpx.get(f"{BOOKING_SERVICE_URL}/reserva/{id_reserva}", timeout=5)
        if resp.status_code == 200:
            estado = resp.json().get("estado", "").upper()
            if estado not in ("PENDIENTE", "HOLD"):
                raise HTTPException(
                    status_code=409,
                    detail=f"Solo se pueden gestionar reservas en estado PENDIENTE o HOLD. Estado actual: {estado}",
                )
    except HTTPException:
        raise
    except Exception:
        # Si booking no está disponible se permite continuar (publicación optimista)
        pass


class AprobarReservaRequest(BaseModel):
    id_usuario_admin: str


class RechazarReservaRequest(BaseModel):
    motivo: str
    id_usuario_admin: str


@router.post("/reserva/{id_reserva}/aprobar", status_code=200)
def aprobar_reserva(id_reserva: str, body: AprobarReservaRequest):
    """
    Aprueba manualmente una reserva en estado PENDIENTE.
    Publica ReservaAprobadaManualEvt con formato CloudEvents 1.0.
    """
    _validar_estado_pendiente(id_reserva)
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


@router.post("/reserva/{id_reserva}/rechazar", status_code=200)
def rechazar_reserva(id_reserva: str, body: RechazarReservaRequest):
    """
    Rechaza manualmente una reserva en estado PENDIENTE.
    Publica ReservaRechazadaManualEvt con formato CloudEvents 1.0.
    """
    _validar_estado_pendiente(id_reserva)
    try:
        publish_reserva_rechazada(
            id_reserva=id_reserva,
            motivo=body.motivo,
            id_usuario_admin=body.id_usuario_admin,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail="No se pudo publicar el evento") from exc

    return {
        "message": "Reserva rechazada. Evento publicado.",
        "id_reserva": id_reserva,
        "motivo": body.motivo,
        "id_usuario_admin": body.id_usuario_admin,
    }
