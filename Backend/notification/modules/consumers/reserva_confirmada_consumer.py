
import json
import pika
import time
from config.rabbitmq import create_connection
from modules.services.email_service import send_voucher_email, send_reservation_status_email
from modules.publishers.voucher_enviado_publisher import publish_voucher_enviado

EVENTS_EXCHANGE = "travelhub.events.exchange"
QUEUE_NAME = "notification.events.queue"
ROUTING_KEYS = ("evt.reserva.confirmada", "evt.reserva.cancelada")
RETRY_DELAY_SECONDS = 5

def callback(ch, method, properties, body):
    try:
        print("Evento recibido:", body)

        data = json.loads(body.decode())

        event_type = data.get("type")

        if event_type not in {"ReservaConfirmadaEvt", "ReservaCanceladaEvt"}:
            print("Evento ignorado:", event_type)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        payload = data.get("data", data)
        reserva_id = payload.get("id_reserva")
        email = payload.get("emailCliente")

        details = {
            "codigo_reserva": payload.get("codigo_reserva") or payload.get("codigoReserva"),
            "hotel": payload.get("hotel"),
            "categoria": payload.get("categoria"),
            "fecha_check_in": payload.get("fecha_check_in") or payload.get("fechaCheckIn"),
            "fecha_check_out": payload.get("fecha_check_out") or payload.get("fechaCheckOut"),
            "huespedes": payload.get("huespedes"),
            "monto_total": payload.get("monto_total") or payload.get("montoTotal"),
            "moneda": payload.get("moneda"),
            "motivo_cancelacion": payload.get("motivo_cancelacion") or payload.get("motivoCancelacion") or payload.get("motivo"),
        }
        details = {k: v for k, v in details.items() if v is not None}

        print(f"Procesando reserva {reserva_id} para {email}")

        if event_type == "ReservaConfirmadaEvt":
            send_voucher_email(email, reserva_id, **details)
            publish_voucher_enviado(reserva_id)
        elif event_type == "ReservaCanceladaEvt":
            send_reservation_status_email(
                email=email,
                reserva_id=reserva_id,
                estado="CANCELADA",
                detalle_reembolso="Cancelacion por compensacion de saga",
                **details,
            )

        ch.basic_ack(delivery_tag=method.delivery_tag)

        print(f"Evento recibido y procesado: {event_type} para reserva {reserva_id}", flush=True)

    except Exception as e:
        print("Error procesando evento:", e)

def _configure_consumer_channel(channel):
    print("Notification service started")
    print("Waiting for reservation status events...")

    # Declarar exchange de eventos
    channel.exchange_declare(
        exchange=EVENTS_EXCHANGE,
        exchange_type="topic",
        durable=True
    )

    # Declarar cola del servicio
    channel.queue_declare(
        queue=QUEUE_NAME,
        durable=True
    )

    # Vincular cola al exchange
    for routing_key in ROUTING_KEYS:
        channel.queue_bind(
            exchange=EVENTS_EXCHANGE,
            queue=QUEUE_NAME,
            routing_key=routing_key
        )

    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=callback,
        auto_ack=False
    )

    print("Waiting for events...")


def start_consumer():
    while True:
        connection = None
        channel = None
        try:
            connection = create_connection(max_attempts=None, retry_delay=RETRY_DELAY_SECONDS)
            channel = connection.channel()
            _configure_consumer_channel(channel)
            channel.start_consuming()
            print("[NOTIFICATION] Consumer stopped unexpectedly, reconnecting...")
        except Exception as exc:
            print(f"[NOTIFICATION] Consumer error: {exc}. Retrying in {RETRY_DELAY_SECONDS} seconds...")
            time.sleep(RETRY_DELAY_SECONDS)
        finally:
            try:
                if channel and channel.is_open:
                    channel.close()
            except Exception:
                pass

            try:
                if connection and connection.is_open:
                    connection.close()
            except Exception:
                pass