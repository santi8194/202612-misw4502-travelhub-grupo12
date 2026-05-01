import json
import time
from config.rabbitmq import create_connection

from modules.pms.infrastructure.services.handlers import handle_confirm_reservation, handle_cancel_reservation

COMMANDS_EXCHANGE = "travelhub.commands.exchange"
QUEUE_NAME = "pms.commands.queue"
ROUTING_KEY_CONFIRM = "cmd.pms.confirmar-reserva"
ROUTING_KEY_CANCEL = "cmd.pms.cancelar-reserva"
RETRY_DELAY_SECONDS = 5


def callback(ch, method, properties, body):

    data = json.loads(body.decode())

    print("[PMS] Command received:", data)
    print("[PMS] Routing key:", method.routing_key)
    try:

        if method.routing_key == "cmd.pms.confirmar-reserva":
            handle_confirm_reservation(data)

        elif method.routing_key == "cmd.pms.cancelar-reserva":
            handle_cancel_reservation(data)

        else:
            print("Comando no reconocido")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:

        print("Error procesando comando:", e)

        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def _configure_consumer_channel(channel):

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
        routing_key=ROUTING_KEY_CONFIRM
    )

    channel.queue_bind(
        exchange=COMMANDS_EXCHANGE,
        queue=QUEUE_NAME,
        routing_key=ROUTING_KEY_CANCEL
    )

    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=callback
    )

    print("Listening on queue:", QUEUE_NAME)


def start_consumer():
    while True:
        connection = None
        channel = None
        try:
            connection = create_connection(max_attempts=None, retry_delay=RETRY_DELAY_SECONDS)
            channel = connection.channel()
            _configure_consumer_channel(channel)
            channel.start_consuming()
            print("[PMS] Consumer stopped unexpectedly, reconnecting...")
        except Exception as exc:
            print(f"[PMS] Consumer error: {exc}. Retrying in {RETRY_DELAY_SECONDS} seconds...")
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