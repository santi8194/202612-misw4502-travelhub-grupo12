from modules.payments.application.commands.process_payment import ProcessPayment
from modules.payments.application.commands.refund_payment import RefundPayment
from modules.payments.domain.events import PaymentRefunded
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
