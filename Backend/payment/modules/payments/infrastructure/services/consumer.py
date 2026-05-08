import json
import time
from config.rabbitmq import create_connection
from modules.payments.infrastructure.services.handlers import handle_process_payment, handle_refund_payment, handle_auto_approve_payment

COMMANDS_EXCHANGE = "travelhub.commands.exchange"
EVENTS_EXCHANGE = "travelhub.events.exchange"
QUEUE_NAME = "payment.commands.queue"
EVENTS_QUEUE_NAME = "payment.events.auto.queue"
ROUTING_KEY_PROCESS_PAYMENT = "cmd.payment.procesar-pago"
ROUTING_KEY_REVERT_PAYMENT = "cmd.payment.reversar-pago"
ROUTING_KEY_RESERVA_CREADA = "evt.reserva.creada"
RETRY_DELAY_SECONDS = 5


def callback(ch, method, properties, body):
    
    data = json.loads(body.decode())

    print("[PAYMENTS] Message received on routing key:", method.routing_key)

    try:

        if method.routing_key == ROUTING_KEY_PROCESS_PAYMENT:
            handle_process_payment(data)

        elif method.routing_key == ROUTING_KEY_REVERT_PAYMENT:
            handle_refund_payment(data)

        elif method.routing_key == ROUTING_KEY_RESERVA_CREADA:
            handle_auto_approve_payment(data)

        else:
            print("[PAYMENTS] Message not recognized")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:

        print("[PAYMENTS] Error processing message:", e)

        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def _configure_consumer_channel(channel):
    # Commands exchange (direct)
    channel.exchange_declare(
        exchange=COMMANDS_EXCHANGE,
        exchange_type="direct",
        durable=True
    )

    channel.queue_declare(
        queue=QUEUE_NAME,
        durable=True
    )

    channel.queue_bind(
        exchange=COMMANDS_EXCHANGE,
        queue=QUEUE_NAME,
        routing_key=ROUTING_KEY_PROCESS_PAYMENT
    )

    channel.queue_bind(
        exchange=COMMANDS_EXCHANGE,
        queue=QUEUE_NAME,
        routing_key=ROUTING_KEY_REVERT_PAYMENT
    )

    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=callback
    )

    # Events exchange (topic) — listen for reserva.creada to auto-approve
    channel.exchange_declare(
        exchange=EVENTS_EXCHANGE,
        exchange_type="topic",
        durable=True
    )

    channel.queue_declare(
        queue=EVENTS_QUEUE_NAME,
        durable=True
    )

    channel.queue_bind(
        exchange=EVENTS_EXCHANGE,
        queue=EVENTS_QUEUE_NAME,
        routing_key=ROUTING_KEY_RESERVA_CREADA
    )

    channel.basic_consume(
        queue=EVENTS_QUEUE_NAME,
        on_message_callback=callback
    )

    print("Listening on queues:", QUEUE_NAME, "and", EVENTS_QUEUE_NAME)


def start_consumer():
    while True:
        connection = None
        channel = None
        try:
            connection = create_connection(max_attempts=None, retry_delay=RETRY_DELAY_SECONDS)
            channel = connection.channel()
            _configure_consumer_channel(channel)
            channel.start_consuming()
            print("[PAYMENTS] Consumer stopped unexpectedly, reconnecting...")
        except Exception as exc:
            print(f"[PAYMENTS] Consumer error: {exc}. Retrying in {RETRY_DELAY_SECONDS} seconds...")
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