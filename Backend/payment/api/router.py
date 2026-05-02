from modules.payments.infrastructure.repository import PaymentRepository
from modules.payments.infrastructure.services.event_bus import EventBus
from fastapi import APIRouter
from pydantic import BaseModel
from modules.payments.application.commands.process_payment import ProcessPayment
from modules.payments.application.commands.refund_payment import RefundPayment
from modules.payments.application.queries.get_payments_by_reservation import GetPaymentsByReservation

router = APIRouter()
repository = PaymentRepository()
event_bus = EventBus()

class PaymentRequest(BaseModel):
    id_reserva: str
    monto: float

class RefundRequest(BaseModel):
    id_pago: str

@router.post("/procesar_pago")
def procesar_pago(request: PaymentRequest):
    command = ProcessPayment(repository, event_bus)
    return command.execute(
        request.id_reserva,
        request.monto,
    )

@router.post("/reversar_pago")
def refund_payment(request: RefundRequest):
    command = RefundPayment(repository, event_bus)
    return command.execute(request.id_pago)

@router.get("/payments/by-reserva/{id_reserva}")
def get_payments_by_reserva(id_reserva: str):
    query = GetPaymentsByReservation(repository)
    return query.execute(id_reserva)

@router.get("/health")
def health_check():
    return {"status": "Payment Service running"}