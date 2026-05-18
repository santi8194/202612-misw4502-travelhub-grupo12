
import os
import smtplib
from email.message import EmailMessage


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _send_email(to_email: str, subject: str, body: str) -> bool:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    smtp_from = os.getenv("SMTP_FROM") or smtp_user or "no-reply@travelhub.local"
    smtp_use_tls = _as_bool(os.getenv("SMTP_USE_TLS", "true"), default=True)
    smtp_use_ssl = _as_bool(os.getenv("SMTP_USE_SSL", "false"), default=False)
    smtp_timeout = int(os.getenv("SMTP_TIMEOUT", "20"))

    if not smtp_host:
        print(
            f"[EmailService] DRY-RUN (SMTP_HOST no configurado). "
            f"To={to_email} Subject={subject}"
        )
        return True

    message = EmailMessage()
    message["From"] = smtp_from
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        if smtp_use_ssl:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=smtp_timeout) as server:
                if smtp_user and smtp_pass:
                    server.login(smtp_user, smtp_pass)
                server.send_message(message)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=smtp_timeout) as server:
                if smtp_use_tls:
                    server.starttls()
                if smtp_user and smtp_pass:
                    server.login(smtp_user, smtp_pass)
                server.send_message(message)

        print(f"[EmailService] Email enviado a {to_email} con asunto '{subject}'")
        return True
    except Exception as exc:
        print(f"[EmailService] Error enviando email a {to_email}: {exc}")
        return False


def _append_detail(lines: list[str], label: str, value):
    if value is None:
        return
    text = str(value).strip()
    if text:
        lines.append(f"- {label}: {text}")


def send_voucher_email(
    email: str,
    reserva_id: str,
    codigo_reserva: str | None = None,
    hotel: str | None = None,
    categoria: str | None = None,
    fecha_check_in: str | None = None,
    fecha_check_out: str | None = None,
    huespedes: int | None = None,
    monto_total: float | None = None,
    moneda: str | None = None,
):
    print(f"Sending voucher email to {email} for reservation {reserva_id}")
    subject = f"TravelHub - Confirmacion de reserva {reserva_id}"

    lines = [
        "Hola,",
        "",
        "Tu reserva fue confirmada exitosamente.",
        "",
        "Detalles de la reserva:",
    ]
    _append_detail(lines, "Id de reserva", reserva_id)
    _append_detail(lines, "Codigo de reserva", codigo_reserva)
    _append_detail(lines, "Hotel", hotel)
    _append_detail(lines, "Categoria", categoria)
    _append_detail(lines, "Check-in", fecha_check_in)
    _append_detail(lines, "Check-out", fecha_check_out)
    _append_detail(lines, "Huespedes", huespedes)

    if isinstance(monto_total, (int, float)):
        currency = (moneda or "COP").upper()
        lines.append(f"- Total: {monto_total:.2f} {currency}")

    lines.extend([
        "",
        "Conserva este correo como comprobante de tu reserva.",
        "Equipo TravelHub",
    ])

    body = "\n".join(lines)
    return _send_email(email, subject, body)


def send_reservation_status_email(
    email: str,
    reserva_id: str,
    estado: str,
    codigo_reserva: str | None = None,
    monto_reembolso: float | None = None,
    moneda_reembolso: str | None = None,
    detalle_reembolso: str | None = None,
    hotel: str | None = None,
    categoria: str | None = None,
    fecha_check_in: str | None = None,
    fecha_check_out: str | None = None,
    huespedes: int | None = None,
    motivo_cancelacion: str | None = None,
):
    status = (estado or "").strip().upper()

    if status == "CONFIRMADA":
        print(
            f"Sending CONFIRMATION email to {email} "
            f"for reservation {reserva_id} "
            f"with confirmation code {codigo_reserva or 'N/A'}"
        )
        subject = f"TravelHub - Reserva confirmada {reserva_id}"
        lines = [
            "Hola,",
            "",
            "Tu reserva fue confirmada exitosamente.",
            "",
            "Detalles de la reserva:",
        ]
        _append_detail(lines, "Id de reserva", reserva_id)
        _append_detail(lines, "Codigo de confirmacion", codigo_reserva or "N/A")
        _append_detail(lines, "Hotel", hotel)
        _append_detail(lines, "Categoria", categoria)
        _append_detail(lines, "Check-in", fecha_check_in)
        _append_detail(lines, "Check-out", fecha_check_out)
        _append_detail(lines, "Huespedes", huespedes)
        lines.extend(["", "Equipo TravelHub"])
        body = "\n".join(lines)
        return _send_email(email, subject, body)

    if status == "CANCELADA":
        refund_amount = f"{monto_reembolso:.2f}" if isinstance(monto_reembolso, (int, float)) else "0.00"
        refund_currency = (moneda_reembolso or "COP").upper()
        print(
            f"Sending CANCELLATION email to {email} "
            f"for reservation {reserva_id} "
            f"with refund {refund_amount} {refund_currency}. "
            f"Details: {detalle_reembolso or 'N/A'}"
        )
        subject = f"TravelHub - Reserva cancelada {reserva_id}"
        lines = [
            "Hola,",
            "",
            "Tu reserva fue cancelada.",
            "",
            "Detalles de la reserva:",
        ]
        _append_detail(lines, "Id de reserva", reserva_id)
        _append_detail(lines, "Hotel", hotel)
        _append_detail(lines, "Categoria", categoria)
        _append_detail(lines, "Check-in", fecha_check_in)
        _append_detail(lines, "Check-out", fecha_check_out)
        _append_detail(lines, "Huespedes", huespedes)
        _append_detail(lines, "Motivo de cancelacion", motivo_cancelacion)
        lines.append(f"- Reembolso estimado: {refund_amount} {refund_currency}")
        _append_detail(lines, "Detalle", detalle_reembolso or "N/A")
        lines.extend(["", "Equipo TravelHub"])
        body = "\n".join(lines)
        return _send_email(email, subject, body)

    raise ValueError(f"Unsupported reservation status for email: {estado}")
