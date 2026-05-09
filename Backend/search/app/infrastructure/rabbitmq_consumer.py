"""
Consumer de RabbitMQ para Search.

Escucha eventos de Catalog y actualiza el índice de búsqueda.
"""

import json
import pika
import os
from typing import Callable

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
ENABLE_EVENTS = os.getenv("ENABLE_EVENTS", "false").lower() == "true"

EVENTS_EXCHANGE = "travelhub.events.exchange"
QUEUE_NAME = "search.catalog.events.queue"
ROUTING_KEYS = [
    "catalog.inventory.updated",
    "catalog.category.pricing.updated"
]


def create_connection():
    """Crea una conexión a RabbitMQ."""
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300
    )
    return pika.BlockingConnection(parameters)


class RabbitMQConsumer:
    """
    Consumer de RabbitMQ para eventos de Catalog.
    
    Escucha eventos de inventario y precios, y delega el procesamiento
    a handlers específicos.
    """
    
    def __init__(self, event_handler: Callable):
        """
        Inicializa el consumer.
        
        Args:
            event_handler: Función que procesa los eventos recibidos
        """
        self.event_handler = event_handler
        self.connection = None
        self.channel = None
    
    def _callback(self, ch, method, properties, body):
        """
        Callback para procesar mensajes de RabbitMQ.
        
        Args:
            ch: Canal de RabbitMQ
            method: Método del mensaje
            properties: Propiedades del mensaje
            body: Cuerpo del mensaje
        """
        try:
            data = json.loads(body.decode())
            
            print(f"[SEARCH] Evento recibido: {data.get('type', 'unknown')}")
            print(f"[SEARCH] Routing key: {method.routing_key}")
            
            self.event_handler(data, method.routing_key)
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f"[SEARCH] Evento procesado exitosamente")
            
        except ValueError as e:
            print(f"[SEARCH] Error de validación: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
        except Exception as e:
            print(f"[SEARCH] Error procesando evento: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start(self):
        """
        Inicia el consumer de RabbitMQ.
        
        Se suscribe a la cola search.catalog.events.queue con bindings
        a catalog.inventory.updated y catalog.category.pricing.updated.
        """
        if not ENABLE_EVENTS:
            print("[SEARCH] Consumer deshabilitado (ENABLE_EVENTS=false)")
            return
        
        try:
            self.connection = create_connection()
            self.channel = self.connection.channel()
            
            self.channel.exchange_declare(
                exchange=EVENTS_EXCHANGE,
                exchange_type="topic",
                durable=True
            )
            
            self.channel.queue_declare(
                queue=QUEUE_NAME,
                durable=True
            )
            
            for routing_key in ROUTING_KEYS:
                self.channel.queue_bind(
                    exchange=EVENTS_EXCHANGE,
                    queue=QUEUE_NAME,
                    routing_key=routing_key
                )
                print(f"[SEARCH] Binding: {routing_key}")
            
            self.channel.basic_qos(prefetch_count=1)
            
            self.channel.basic_consume(
                queue=QUEUE_NAME,
                on_message_callback=self._callback
            )
            
            print(f"[SEARCH] Escuchando en cola: {QUEUE_NAME}")
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            print("[SEARCH] Consumer detenido por usuario")
            self.stop()
        except Exception as e:
            print(f"[SEARCH] Error en consumer: {e}")
            raise
    
    def stop(self):
        """Detiene el consumer y cierra la conexión."""
        if self.channel and self.channel.is_open:
            self.channel.stop_consuming()
        if self.connection and self.connection.is_open:
            self.connection.close()
        print("[SEARCH] Consumer detenido")
