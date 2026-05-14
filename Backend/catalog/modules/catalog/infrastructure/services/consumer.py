"""
Consumer de RabbitMQ para Catalog.

Escucha eventos de inventario del PMS y los procesa con idempotencia.
"""

import json
from config.rabbitmq import create_connection
from modules.catalog.infrastructure.services.handlers import handle_pms_inventory_updated

EVENTS_EXCHANGE = "travelhub.events.exchange"
QUEUE_NAME = "catalog.pms.inventory.queue"
ROUTING_KEY_PMS_INVENTORY = "pms.inventory.updated"


def callback(ch, method, properties, body):
    """
    Callback para procesar mensajes de RabbitMQ.
    
    Maneja eventos PMSInventoryUpdated con idempotencia y control de errores.
    """
    
    try:
        data = json.loads(body.decode())
        
        print(f"[CATALOG] Evento recibido: {data.get('type', 'unknown')}")
        print(f"[CATALOG] Routing key: {method.routing_key}")
        
        if method.routing_key == ROUTING_KEY_PMS_INVENTORY:
            handle_pms_inventory_updated(data)
            print(f"[CATALOG] Evento PMSInventoryUpdated procesado exitosamente")
        else:
            print(f"[CATALOG] Routing key no reconocida: {method.routing_key}")
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except ValueError as e:
        print(f"[CATALOG] Error de validación procesando evento: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
    except Exception as e:
        print(f"[CATALOG] Error procesando evento: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def start_consumer():
    """
    Inicia el consumer de RabbitMQ para eventos de inventario PMS.
    
    Se suscribe a la cola catalog.pms.inventory.queue con binding
    a pms.inventory.updated en el exchange de eventos.
    """
    
    try:
        connection = create_connection()
        channel = connection.channel()
        
        channel.exchange_declare(
            exchange=EVENTS_EXCHANGE,
            exchange_type="topic",
            durable=True
        )
        
        channel.queue_declare(
            queue=QUEUE_NAME,
            durable=True
        )
        
        channel.queue_bind(
            exchange=EVENTS_EXCHANGE,
            queue=QUEUE_NAME,
            routing_key=ROUTING_KEY_PMS_INVENTORY
        )
        
        channel.basic_qos(prefetch_count=1)
        
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=callback
        )
        
        print(f"[CATALOG] Escuchando en cola: {QUEUE_NAME}")
        print(f"[CATALOG] Binding: {ROUTING_KEY_PMS_INVENTORY}")
        channel.start_consuming()
        
    except KeyboardInterrupt:
        print("[CATALOG] Consumer detenido por usuario")
        if connection and connection.is_open:
            connection.close()
    except Exception as e:
        print(f"[CATALOG] Error en consumer: {e}")
        raise