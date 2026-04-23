from pydantic import BaseModel, Field


class CreatePaymentRequest(BaseModel):
    id_reserva: str = Field(..., min_length=1)
    monto: float = Field(..., gt=0)
    moneda: str = Field(default="COP", min_length=3, max_length=3)


class CheckoutData(BaseModel):
    public_key: str
    currency: str
    amount_in_cents: int
    reference: str
    signature_integrity: str


class PaymentResponse(BaseModel):
    id_pago: str
    id_reserva: str
    referencia: str
    estado: str
    monto: float
    moneda: str
    wompi_transaction_id: str | None = None
    checkout: CheckoutData

