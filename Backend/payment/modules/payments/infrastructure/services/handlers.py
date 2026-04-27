import uuid

from modules.payments.application.commands.process_payment import ProcessPayment
from modules.payments.application.commands.refund_payment import RefundPayment
from modules.payments.domain.events import PaymentRefunded, SuccessfulPayment
from modules.payments.infrastructure.repository import PaymentRepository
from modules.payments.infrastructure.services.event_bus import EventBus
import os


def payment_mode() -> str:
    return os.getenv("PAYMENT_MODE", "wompi").strip().lower()

def handle_process_payment(data):

    reservation_id = data["id_reserva"]
    amount = data["monto"]

    print(f"[PAYMENTS] Command received: ProcessPayment for reservation {reservation_id}")

    if payment_mode() == "wompi":
        print("[PAYMENTS] PAYMENT_MODE=wompi: waiting for Wompi webhook, command ignored")
        return {"message": "Waiting for Wompi webhook", "state": "PENDING"}

    repository = PaymentRepository()
    event_bus = EventBus()

    use_case = ProcessPayment(repository, event_bus)

    result = use_case.execute(
        reservation_id,
        amount,
    )

    print("[PAYMENTS] Result:", result)


def handle_refund_payment(data):

    reservation_id = data["id_reserva"]

    print(f"[PAYMENTS] Command received: RefundPayment for reservation {reservation_id}")

    if payment_mode() == "wompi":
        from app import mark_payment_refunded_by_reserva

        payment = mark_payment_refunded_by_reserva(reservation_id)
        if not payment:
            return {"error": "Payment not found"}

        event_bus = EventBus()
        event = PaymentRefunded(payment["id_pago"], reservation_id)
        event_bus.publish_event(event.routing_key, event.type, event.to_dict())
        result = {
            "reservation_id": reservation_id,
            "payment_id": payment["id_pago"],
            "state": payment["estado"],
            "event_generated": event.type,
        }
        print("[PAYMENTS] Result:", result)
        return result

    repository = PaymentRepository()
    event_bus = EventBus()

    use_case = RefundPayment(repository, event_bus)

    result = use_case.execute(reservation_id)

    print("[PAYMENTS] Result:", result)


def handle_auto_approve_payment(data):
    """
    Handles evt.reserva.creada when PAYMENT_AUTO_APPROVE=true.
    Publishes PagoExitosoEvt directly so the saga can advance without a Wompi webhook.
    """
    if os.getenv("PAYMENT_AUTO_APPROVE", "false").lower() != "true":
        return

    # Extract reservation data — payload is either nested under 'data' or flat
    payload = data.get("data", data)
    reservation_id = payload.get("id_reserva")

    if not reservation_id:
        print("[PAYMENTS] handle_auto_approve_payment: missing id_reserva, skipping")
        return

    payment_id = str(uuid.uuid4())
    print(f"[PAYMENTS] Auto-approving payment {payment_id} for reservation {reservation_id}")

    event_bus = EventBus()
    event = SuccessfulPayment(payment_id, reservation_id)
    event_bus.publish_event(event.routing_key, event.type, event.to_dict())

    print(f"[PAYMENTS] PagoExitosoEvt published for reservation {reservation_id}")
