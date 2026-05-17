from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from modules.services.email_service import send_reservation_status_email

router = APIRouter(prefix="/notifications", tags=["notifications"])


class ReservationStatusEmailRequest(BaseModel):
    id_reserva: str
    email_cliente: str
    estado: str
    codigo_reserva: str | None = None
    monto_reembolso: float | None = None
    moneda_reembolso: str | None = None
    detalle_reembolso: str | None = None


@router.post("/reservations/status-email")
def send_reservation_status_notification(payload: ReservationStatusEmailRequest):
    status = (payload.estado or "").strip().upper()

    if status not in {"CONFIRMADA", "CANCELADA"}:
        raise HTTPException(status_code=400, detail="estado debe ser CONFIRMADA o CANCELADA")

    try:
        send_reservation_status_email(
            email=payload.email_cliente,
            reserva_id=payload.id_reserva,
            estado=status,
            codigo_reserva=payload.codigo_reserva,
            monto_reembolso=payload.monto_reembolso,
            moneda_reembolso=payload.moneda_reembolso,
            detalle_reembolso=payload.detalle_reembolso,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "message": "Notification queued",
        "id_reserva": payload.id_reserva,
        "estado": status,
    }
