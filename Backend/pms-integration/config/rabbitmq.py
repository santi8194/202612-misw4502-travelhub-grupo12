import pika
import time
from config.settings import settings

def create_connection(max_attempts=10, retry_delay=5):
    credentials = pika.PlainCredentials(
        settings.RABBITMQ_USER,
        settings.RABBITMQ_PASS
    )

    parameters = pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        credentials=credentials
    )

    attempt = 0
    while max_attempts is None or attempt < max_attempts:
        try:
            attempt += 1
            print(f"Connecting to RabbitMQ (attempt {attempt})...")
            return pika.BlockingConnection(parameters)
        except pika.exceptions.AMQPConnectionError:
            print(f"RabbitMQ not ready, retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

    raise Exception("Could not connect to RabbitMQ after retries")