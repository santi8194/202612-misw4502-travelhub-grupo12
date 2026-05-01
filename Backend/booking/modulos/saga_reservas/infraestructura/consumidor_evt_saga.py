import logging

logger = logging.getLogger(__name__)

import pika
import json
import os
import sys
# Agregar el directorio Booking al path para poder importar módulos propios en ejecución standalone
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

import argparse
import uuid
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importar contexto de base de datos y orquestador
from config.db import db
from modulos.saga_reservas.aplicacion.orquestador import OrquestadorSagaReservas
from modulos.saga_reservas.infraestructura.repositorios import RepositorioSagas
from config.uow import UnidadTrabajoHibrida


def configurar_logging():
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        stream=sys.stdout,
        force=True,
    )
    logger.info("[SAGA WORKER] Logging configurado con nivel %s", level_name)

def get_db_session():
    # Obtienemos la sesión de BD de SQLAlchemy configurada
    # Ya que corremos fuera de Flask de forma aislada
    db_mode = (os.getenv('BOOKING_DB_MODE', '') or '').strip().lower()
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME')

    if db_mode == 'sqlite':
        instance_path = os.getenv('BOOKING_INSTANCE_PATH', '/src/instance')
        db_path = os.path.join(instance_path, 'booking.db')
        connection_url = f'sqlite:///{db_path}'
    elif db_mode == 'postgres':
        if not all([db_user, db_password, db_host, db_name]):
            raise RuntimeError('BOOKING_DB_MODE=postgres requires DB_USER, DB_PASSWORD, DB_HOST and DB_NAME')
        connection_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    elif all([db_user, db_password, db_host, db_name]):
        connection_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    else:
        instance_path = os.getenv('BOOKING_INSTANCE_PATH', '/src/instance')
        db_path = os.path.join(instance_path, 'booking.db')
        connection_url = f'sqlite:///{db_path}'
        
    engine = create_engine(connection_url)
    Session = sessionmaker(bind=engine)
    return Session()

def procesar_mensaje(ch, method, properties, body):
    try:
        mensaje = json.loads(body)
        logger.info(f"\n[SAGA WORKER] Mensaje Recibido: {method.routing_key}")
        
        from api import create_app
        logger.info("[SAGA WORKER] Creando Flask App en memoria...")
        app = create_app()
        
        with app.app_context():
            logger.info("[SAGA WORKER] Entró al app context")
            repo_sagas = RepositorioSagas() # Usa db.session por defecto
            uow = UnidadTrabajoHibrida()
            logger.info("[SAGA WORKER] UoW inicializado")
            orquestador = OrquestadorSagaReservas(repositorio=repo_sagas, uow=uow)

            # Validar tipo de evento esperado (por convención o por key)
            if method.routing_key == "evt.reserva.creada":
                
                # Extraer payload base
                payload = mensaje.get('data', {})
                id_reserva = payload.get('id_reserva') or mensaje.get('id_reserva')
                id_usuario = payload.get('id_usuario') or payload.get('id_cliente') or mensaje.get('id_usuario', str(uuid.uuid4()))
                monto = payload.get('monto') or mensaje.get('monto', 1500.0)
                id_categoria = payload.get('id_categoria') or mensaje.get('id_categoria')
                fecha_reserva = payload.get('fecha_reserva') or mensaje.get('fecha_reserva')
                
                if not id_reserva:
                     logger.info("[SAGA WORKER] Ignorando evento: id_reserva vacío")
                     ch.basic_ack(delivery_tag=method.delivery_tag)
                     return

                logger.info(f"[SAGA WORKER] Iniciando Saga para reserva: {id_reserva} (Fecha: {fecha_reserva})")
                     
                logger.info(f"[SAGA WORKER] Llamando orquestador con id_reserva: {id_reserva}")
                res = orquestador.iniciar_saga(
                    id_reserva=uuid.UUID(str(id_reserva)),
                    id_usuario=uuid.UUID(str(id_usuario)),
                    monto=float(monto),
                    id_categoria=uuid.UUID(str(id_categoria)) if id_categoria else None,
                    fecha_reserva=fecha_reserva
                )
                logger.info(f"[SAGA WORKER] Orquestador terminó con resultado: {res}")
                     
            else:
                # Es un evento de respuesta de otro microservicio
                payload = mensaje.get('data', {}) or mensaje
                id_reserva = payload.get('id_reserva') or mensaje.get('id_reserva')
                
                if not id_reserva:
                    logger.info(f"[SAGA WORKER] Ignorando evento {method.routing_key}: No contiene id_reserva")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return
                
                data = json.loads(body.decode())
                evento_tipo = data["type"] if "type" in data else method.routing_key
                logger.info(f"[SAGA WORKER] Procesando evento de respuesta {evento_tipo} para reserva: {id_reserva}")
                
                # Pasar al orquestador
                orquestador.manejar_evento_respuesta(
                    id_reserva=uuid.UUID(str(id_reserva)),
                    evento_recibido=evento_tipo,
                    payload_recibido=payload
                )

        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info("[SAGA WORKER] Mensaje procesado y Acknowledge enviado.")
        
    except Exception as e:
        logger.error(f"[SAGA WORKER] Error procesando mensaje {method.routing_key}: {e}")
        # Rechazamos el mensaje sin requeue en caso de error fatal de sintaxis
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def _crear_parametros_rabbitmq():
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
    rabbitmq_port = int(os.getenv('RABBITMQ_PORT', 5672))
    rabbitmq_user = os.getenv('RABBITMQ_USER', 'guest')
    rabbitmq_pass = os.getenv('RABBITMQ_PASS', 'guest')

    return pika.ConnectionParameters(
        host=rabbitmq_host,
        port=rabbitmq_port,
        credentials=pika.PlainCredentials(rabbitmq_user, rabbitmq_pass),
        heartbeat=int(os.getenv('RABBITMQ_HEARTBEAT', '30')),
        blocked_connection_timeout=int(os.getenv('RABBITMQ_BLOCKED_TIMEOUT', '30')),
    )


def _configurar_canal(channel):
    exchange_name = 'travelhub.events.exchange'
    queue_name = 'saga_reservas.events.queue'
    routing_key = 'evt.#'

    channel.exchange_declare(exchange=exchange_name, exchange_type='topic', durable=True)
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=procesar_mensaje)

    logger.info(
        " [*] SAGA WORKER esperando eventos ('%s') en la cola '%s'. Para salir presione CTRL+C",
        routing_key,
        queue_name,
    )


def iniciar_consumidor():
    logger.info("[SAGA WORKER] Iniciando consumidor de RabbitMQ...")

    connection_params = _crear_parametros_rabbitmq()
    retry_delay = int(os.getenv('RABBITMQ_RETRY_DELAY_SECONDS', '5'))

    while True:
        connection = None
        channel = None
        try:
            connection = pika.BlockingConnection(connection_params)
            logger.info(
                "[SAGA WORKER] Conexion establecida con RabbitMQ en %s:%s",
                connection_params.host,
                connection_params.port,
            )

            channel = connection.channel()
            _configurar_canal(channel)
            channel.start_consuming()
            logger.warning("[SAGA WORKER] El consumidor finalizo inesperadamente, reiniciando...")
        except KeyboardInterrupt:
            logger.info('Worker detenido manualmente.')
            break
        except (
            pika.exceptions.AMQPConnectionError,
            pika.exceptions.ConnectionClosedByBroker,
            pika.exceptions.StreamLostError,
            OSError,
        ) as exc:
            logger.warning(
                "[SAGA WORKER] RabbitMQ no disponible o conexion perdida (%s:%s): %s. Reintentando en %s s...",
                connection_params.host,
                connection_params.port,
                exc,
                retry_delay,
            )
        except Exception:
            logger.exception(
                "[SAGA WORKER] Error inesperado en el consumidor. Reintentando en %s s...",
                retry_delay,
            )
        finally:
            try:
                if channel and channel.is_open:
                    channel.close()
            except Exception:
                logger.debug("[SAGA WORKER] No fue posible cerrar el canal RabbitMQ limpiamente.")

            try:
                if connection and connection.is_open:
                    connection.close()
            except Exception:
                logger.debug("[SAGA WORKER] No fue posible cerrar la conexion RabbitMQ limpiamente.")

        time.sleep(retry_delay)

if __name__ == '__main__':
    try:
        # Forcing unbuffered stdout for Docker logs
        sys.stdout.reconfigure(line_buffering=True)
        configurar_logging()
        iniciar_consumidor()
    except KeyboardInterrupt:
        logger.info('Worker detenido manualmente.')
