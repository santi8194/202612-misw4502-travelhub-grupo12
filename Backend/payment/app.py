import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any

import pika
from fastapi import FastAPI, Header, HTTPException, Request
from starlette.middleware.cors import CORSMiddleware

from modules.payments.infrastructure.database import SessionLocal
from modules.payments.infrastructure.models import PaymentModel
from models import (
    AcceptanceTokensResponse,
    CardTokenizationRequest,
    CardTokenizationResponse,
    CreateCardPaymentRequest,
    CreatePaymentRequest,
    PaymentCheckoutResponse,
    PaymentResponse,
)
from wompi_client import (
    WompiAPIError,
    build_checkout_data,
    create_card_transaction,
    create_payment_source,
    fetch_acceptance_tokens,
    fetch_transaction,
    map_wompi_status,
    tokenize_card,
    verify_event,
)

SERVICE_NAME = "payment"
FINAL_STATES = {"APPROVED", "REJECTED", "CANCELLED"}
EVENTS_EXCHANGE = "travelhub.events.exchange"

app = FastAPI(title="TravelHub Payment Service")
logger = logging.getLogger(SERVICE_NAME)
logging.basicConfig(level=logging.INFO)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

payments_by_id: dict[str, dict[str, Any]] = {}
payment_id_by_reference: dict[str, str] = {}


def healthcheck() -> str:
    return "ok"


def get_payment_for_reserva(id_reserva: str) -> dict[str, Any] | None:
    payment = get_payment_model_by_reserva(id_reserva)
    return payment_model_to_dict(payment) if payment else None


def mark_payment_refunded_by_reserva(id_reserva: str) -> dict[str, Any] | None:
    payment_model = get_payment_model_by_reserva(id_reserva)
    if not payment_model:
        return None

    payment = payment_model_to_dict(payment_model)
    payment["estado"] = "REFUNDED"
    payment["updated_at"] = utc_now()
    save_payment(payment)
    return payment


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": healthcheck(), "service": SERVICE_NAME}


@app.get("/payments/acceptance-tokens", response_model=AcceptanceTokensResponse)
def get_acceptance_tokens() -> dict[str, Any]:
    return handle_wompi_call(fetch_acceptance_tokens)


@app.post("/payments", response_model=PaymentCheckoutResponse, status_code=201)
def create_payment(request: CreatePaymentRequest) -> dict[str, Any]:
    id_pago = str(uuid.uuid4())
    reference = f"PAY-{id_pago}"
    amount_in_cents = int(round(request.monto * 100))
    currency = request.moneda.upper()

    checkout = build_checkout_data(reference, amount_in_cents, currency)
    now = utc_now()
    payment = {
        "id_pago": id_pago,
        "id_reserva": request.id_reserva,
        "referencia": reference,
        "estado": "PENDING",
        "monto": request.monto,
        "moneda": currency,
        "wompi_transaction_id": None,
        "checkout": checkout,
        "created_at": now,
        "updated_at": now,
        "event_published": False,
    }

    save_payment(payment)

    if os.getenv("PAYMENT_AUTO_APPROVE", "false").lower() == "true":
        payment["estado"] = "APPROVED"
        payment["updated_at"] = utc_now()
        maybe_publish_final_event(payment)

    return payment


@app.post("/payments/cards/tokenize", response_model=CardTokenizationResponse)
def tokenize_card_payment_method(request: CardTokenizationRequest) -> dict[str, Any]:
    return handle_wompi_call(tokenize_card, request.model_dump())


@app.post("/payments/cards", response_model=PaymentResponse, status_code=201)
def create_card_payment(request: CreateCardPaymentRequest, http_request: Request) -> dict[str, Any]:
    id_pago = str(uuid.uuid4())
    reference = f"PAY-{id_pago}"
    amount_in_cents = int(round(request.monto * 100))
    currency = request.moneda.upper()

    payment_source_id = request.payment_source_id
    if payment_source_id is None:
        source_payload = handle_wompi_call(
            create_payment_source,
            card_token=request.card_token or "",
            customer_email=request.customer_email,
            acceptance_token=request.acceptance_token,
            accept_personal_auth=request.accept_personal_auth,
        )
        payment_source_id = source_payload.get("data", {}).get("id")
        if payment_source_id is None:
            raise HTTPException(status_code=502, detail="Wompi no retornó un payment_source_id válido")

    transaction_payload = handle_wompi_call(
        create_card_transaction,
        amount_in_cents=amount_in_cents,
        currency=currency,
        customer_email=request.customer_email,
        acceptance_token=request.acceptance_token,
        accept_personal_auth=request.accept_personal_auth,
        reference=reference,
        payment_source_id=payment_source_id,
        installments=request.installments,
        redirect_url=request.redirect_url,
        ip_address=extract_client_ip(http_request),
        recurrent=request.recurrent,
    )

    transaction = transaction_payload.get("data", {})
    transaction_state = map_wompi_status(transaction.get("status"))
    now = utc_now()
    payment = {
        "id_pago": id_pago,
        "id_reserva": request.id_reserva,
        "referencia": reference,
        "estado": transaction_state,
        "monto": request.monto,
        "moneda": currency,
        "wompi_transaction_id": transaction.get("id"),
        "created_at": now,
        "updated_at": now,
        "event_published": False,
    }

    save_payment(payment)

    if transaction_state in {"APPROVED", "REJECTED"}:
        maybe_publish_final_event(payment)

    return payment


@app.get("/payments", response_model=list[PaymentResponse])
def list_payments() -> list[dict[str, Any]]:
    db = SessionLocal()
    try:
        return [payment_model_to_dict(payment) for payment in db.query(PaymentModel).all()]
    finally:
        db.close()


@app.get("/payments/by-reserva/{id_reserva}", response_model=PaymentResponse)
def get_payment_by_reserva(id_reserva: str) -> dict[str, Any]:
    payment = get_payment_for_reserva(id_reserva)
    if payment:
        return payment
    raise HTTPException(status_code=404, detail="Pago no encontrado para la reserva")


@app.get("/payments/{id_pago}", response_model=PaymentResponse)
def get_payment(id_pago: str) -> dict[str, Any]:
    payment_model = get_payment_model_by_id(id_pago)
    payment = payment_model_to_dict(payment_model) if payment_model else None
    if not payment:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    return payment


@app.get("/payments/transactions/{transaction_id}")
def get_transaction_status(transaction_id: str) -> dict[str, Any]:
    return handle_wompi_call(fetch_transaction, transaction_id)


@app.post("/webhook")
async def receive_webhook(
    request: Request,
    x_event_checksum: str | None = Header(default=None),
) -> dict[str, Any]:
    payload = await request.json()

    if not verify_event(payload, x_event_checksum):
        raise HTTPException(status_code=401, detail="Firma de webhook invalida")

    event_name = payload.get("event")
    transaction = payload.get("data", {}).get("transaction", {})
    reference = transaction.get("reference")
    wompi_status = transaction.get("status")

    if event_name != "transaction.updated":
        return {"message": "Evento ignorado", "event": event_name}

    if not reference:
        raise HTTPException(status_code=400, detail="Webhook sin referencia de pago")

    payment_model = get_payment_model_by_reference(reference)
    if not payment_model:
        raise HTTPException(status_code=404, detail="Pago no encontrado para la referencia")

    payment = payment_model_to_dict(payment_model)
    new_status = map_wompi_status(wompi_status)
    old_status = payment["estado"]

    if old_status in FINAL_STATES:
        maybe_publish_final_event(payment)
        return {"message": "Pago ya estaba finalizado", "estado": old_status}

    payment["estado"] = new_status
    payment["wompi_transaction_id"] = transaction.get("id")
    payment["updated_at"] = utc_now()
    save_payment(payment)

    if new_status in {"APPROVED", "REJECTED"}:
        maybe_publish_final_event(payment)

    return {
        "message": "Webhook procesado",
        "id_pago": payment["id_pago"],
        "estado": payment["estado"],
    }


def maybe_publish_final_event(payment: dict[str, Any]) -> None:
    if payment.get("event_published"):
        return

    if payment["estado"] == "APPROVED":
        payment["event_published"] = publish_payment_event(payment, "PagoExitosoEvt", "evt.pago.exitoso")
    elif payment["estado"] == "REJECTED":
        payment["event_published"] = publish_payment_event(payment, "PagoRechazadoEvt", "evt.pago.rechazado")
    else:
        return

    save_payment(payment)


def save_payment(payment: dict[str, Any]) -> None:
    db = SessionLocal()
    try:
        model = PaymentModel(
            id=payment["id_pago"],
            reservation_id=payment["id_reserva"],
            reference=payment["referencia"],
            amount=payment["monto"],
            currency=payment["moneda"],
            state=payment["estado"],
            wompi_transaction_id=payment.get("wompi_transaction_id"),
            created_at=payment.get("created_at"),
            updated_at=payment.get("updated_at"),
            event_published=bool(payment.get("event_published")),
        )
        db.merge(model)
        db.commit()
    finally:
        db.close()

    payments_by_id[payment["id_pago"]] = payment
    payment_id_by_reference[payment["referencia"]] = payment["id_pago"]


def get_payment_model_by_id(payment_id: str) -> PaymentModel | None:
    db = SessionLocal()
    try:
        return db.query(PaymentModel).filter(PaymentModel.id == payment_id).first()
    finally:
        db.close()


def get_payment_model_by_reserva(reservation_id: str) -> PaymentModel | None:
    db = SessionLocal()
    try:
        return (
            db.query(PaymentModel)
            .filter(PaymentModel.reservation_id == reservation_id)
            .order_by(PaymentModel.created_at.desc().nullslast(), PaymentModel.id.desc())
            .first()
        )
    finally:
        db.close()


def get_payment_model_by_reference(reference: str) -> PaymentModel | None:
    db = SessionLocal()
    try:
        return db.query(PaymentModel).filter(PaymentModel.reference == reference).first()
    finally:
        db.close()


def payment_model_to_dict(payment: PaymentModel) -> dict[str, Any]:
    return {
        "id_pago": payment.id,
        "id_reserva": payment.reservation_id,
        "referencia": payment.reference or f"PAY-{payment.id}",
        "estado": payment.state,
        "monto": payment.amount,
        "moneda": payment.currency,
        "wompi_transaction_id": payment.wompi_transaction_id,
        "created_at": payment.created_at,
        "updated_at": payment.updated_at,
        "event_published": bool(payment.event_published),
    }


def publish_payment_event(payment: dict[str, Any], event_type: str, routing_key: str) -> bool:
    body = {
        "type": event_type,
        "data": {
            "id_reserva": payment["id_reserva"],
            "id_pago": payment["id_pago"],
            "referencia": payment["referencia"],
            "wompi_transaction_id": payment.get("wompi_transaction_id"),
            "estado": payment["estado"],
        },
    }

    try:
        host = os.getenv("RABBITMQ_HOST", "localhost")
        port = int(os.getenv("RABBITMQ_PORT", "5672"))
        user = os.getenv("RABBITMQ_USER", "guest")
        password = os.getenv("RABBITMQ_PASS", "guest")
        credentials = pika.PlainCredentials(user, password)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, port=port, credentials=credentials)
        )
        channel = connection.channel()
        channel.exchange_declare(exchange=EVENTS_EXCHANGE, exchange_type="topic", durable=True)
        channel.basic_publish(
            exchange=EVENTS_EXCHANGE,
            routing_key=routing_key,
            body=json.dumps(body),
            properties=pika.BasicProperties(content_type="application/json", type=event_type),
        )
        connection.close()
        logger.info("Evento de pago publicado: %s", event_type)
        return True
    except Exception as exc:
        logger.warning("No se pudo publicar evento de pago en RabbitMQ: %s", exc)
        return False


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def extract_client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    if request.client:
        return request.client.host

    return None


def handle_wompi_call(func: Any, *args: Any, **kwargs: Any) -> dict[str, Any]:
    try:
        return func(*args, **kwargs)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except WompiAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
