
def send_voucher_email(email: str, reserva_id: str):
    print(f"Sending voucher email to {email} for reservation {reserva_id}")
    return True


def send_reservation_status_email(
    email: str,
    reserva_id: str,
    estado: str,
    codigo_reserva: str | None = None,
    monto_reembolso: float | None = None,
    moneda_reembolso: str | None = None,
    detalle_reembolso: str | None = None,
):
    status = (estado or "").strip().upper()

    if status == "CONFIRMADA":
        print(
            f"Sending CONFIRMATION email to {email} "
            f"for reservation {reserva_id} "
            f"with confirmation code {codigo_reserva or 'N/A'}"
        )
        return True

    if status == "CANCELADA":
        refund_amount = f"{monto_reembolso:.2f}" if isinstance(monto_reembolso, (int, float)) else "0.00"
        refund_currency = (moneda_reembolso or "COP").upper()
        print(
            f"Sending CANCELLATION email to {email} "
            f"for reservation {reserva_id} "
            f"with refund {refund_amount} {refund_currency}. "
            f"Details: {detalle_reembolso or 'N/A'}"
        )
        return True

    raise ValueError(f"Unsupported reservation status for email: {estado}")
