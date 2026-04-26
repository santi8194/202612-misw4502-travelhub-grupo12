from pydantic import BaseModel, Field, model_validator


class CreatePaymentRequest(BaseModel):
    id_reserva: str = Field(..., min_length=1)
    monto: float = Field(..., gt=0)
    moneda: str = Field(default="COP", min_length=3, max_length=3)


class AcceptanceDocument(BaseModel):
    acceptance_token: str
    permalink: str
    type: str


class AcceptanceTokensResponse(BaseModel):
    acceptance: AcceptanceDocument
    personal_data_auth: AcceptanceDocument


class CheckoutData(BaseModel):
    public_key: str
    currency: str
    amount_in_cents: int
    reference: str
    signature_integrity: str


class CardTokenizationRequest(BaseModel):
    number: str = Field(..., min_length=13, max_length=19, pattern=r"^\d{13,19}$")
    exp_month: str = Field(..., pattern=r"^(0[1-9]|1[0-2])$")
    exp_year: str = Field(..., pattern=r"^\d{2}$")
    cvc: str = Field(..., pattern=r"^\d{3,4}$")
    card_holder: str = Field(..., min_length=5)


class CardTokenData(BaseModel):
    id: str
    status: str
    created_at: str | None = None
    brand: str | None = None
    name: str | None = None
    last_four: str | None = None
    bin: str | None = None
    exp_year: str | None = None
    exp_month: str | None = None
    card_holder: str | None = None
    expires_at: str | None = None


class CardTokenizationResponse(BaseModel):
    data: CardTokenData


class CreateCardPaymentRequest(BaseModel):
    id_reserva: str = Field(..., min_length=1)
    monto: float = Field(..., gt=0)
    moneda: str = Field(default="COP", min_length=3, max_length=3)
    customer_email: str = Field(..., min_length=3)
    acceptance_token: str = Field(..., min_length=1)
    accept_personal_auth: str = Field(..., min_length=1)
    card_token: str | None = None
    payment_source_id: int | None = None
    installments: int = Field(default=1, ge=1, le=36)
    redirect_url: str | None = None
    recurrent: bool | None = None

    @model_validator(mode="after")
    def validate_payment_origin(self) -> "CreateCardPaymentRequest":
        if not self.card_token and self.payment_source_id is None:
            raise ValueError("Debes enviar card_token o payment_source_id")
        return self


class PaymentResponse(BaseModel):
    id_pago: str
    id_reserva: str
    referencia: str
    estado: str
    monto: float
    moneda: str
    wompi_transaction_id: str | None = None
    payment_source_id: int | None = None
    payment_method_type: str | None = None
    customer_email: str | None = None
    status_message: str | None = None
    card_brand: str | None = None
    card_last_four: str | None = None
    checkout: CheckoutData | None = None
