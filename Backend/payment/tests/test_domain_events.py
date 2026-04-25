from modules.payments.domain.events import PaymentRefundFailed


def test_payment_refund_failed_to_dict():
    event = PaymentRefundFailed("res-300", "already reversed")

    assert event.to_dict() == {
        "id_reserva": "res-300",
        "motivo": "already reversed",
    }
