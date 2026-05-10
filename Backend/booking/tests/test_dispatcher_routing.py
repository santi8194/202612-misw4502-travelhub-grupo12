"""
Pruebas unitarias para DespachadorRabbitMQ: routing registry, obtener_routing, publicar_evento.
"""
import uuid
from unittest.mock import MagicMock, patch
from dataclasses import dataclass

from seedwork.infraestructura.dispatchers import DespachadorRabbitMQ
from seedwork.aplicacion.comandos import Comando
from modulos.saga_reservas.dominio.comandos import ProcesarPagoCmd


# --- Pruebas de ROUTING_REGISTRY ---

def test_routing_registry_tiene_comandos_conocidos():
    """Verifica que ROUTING_REGISTRY contiene los comandos principales."""
    registry = DespachadorRabbitMQ.ROUTING_REGISTRY
    
    assert "ProcesarPagoCmd" in registry
    assert "ConfirmarReservaPmsCmd" in registry
    assert "ReversarPagoCmd" in registry
    assert "CancelarReservaPmsCmd" in registry
    assert "SolicitarAprobacionManualCmd" in registry


def test_routing_registry_tiene_eventos_conocidos():
    """Verifica que ROUTING_REGISTRY contiene los eventos principales."""
    registry = DespachadorRabbitMQ.ROUTING_REGISTRY
    
    assert "ReservaCreadaIntegracionEvt" in registry
    assert "PagoExitosoEvt" in registry
    assert "PagoRechazadoEvt" in registry
    assert "ConfirmacionPmsExitosaEvt" in registry
    assert "ReservaRechazadaPmsEvt" in registry
    assert "ReservaConfirmadaEvt" in registry
    assert "VoucherEnviadoEvt" in registry


def test_routing_registry_todos_tienen_exchange_valido():
    """Verifica que todos los registros tienen un exchange válido."""
    registry = DespachadorRabbitMQ.ROUTING_REGISTRY
    
    for tipo, (exchange, key) in registry.items():
        assert exchange.startswith("travelhub."), f"Exchange inválido para {tipo}: {exchange}"
        assert len(key) > 0, f"Routing key vacía para {tipo}"
        assert "." in key, f"Routing key sin jerarquía para {tipo}: {key}"


# --- Pruebas de _obtener_routing ---

def test_obtener_routing_retorna_routing_para_procesar_pago_cmd():
    """Verifica que _obtener_routing retorna el routing correcto para ProcesarPagoCmd."""
    dispatcher = DespachadorRabbitMQ(mapeador_eventos=None)
    
    exchange, key = dispatcher._obtener_routing("ProcesarPagoCmd")
    
    assert exchange == "travelhub.commands.exchange"
    assert key == "cmd.payment.procesar-pago"


def test_obtener_routing_retorna_routing_para_confirmar_reserva_pms_cmd():
    """Verifica que _obtener_routing retorna el routing correcto para ConfirmarReservaPmsCmd."""
    dispatcher = DespachadorRabbitMQ(mapeador_eventos=None)
    
    exchange, key = dispatcher._obtener_routing("ConfirmarReservaPmsCmd")
    
    assert exchange == "travelhub.commands.exchange"
    assert key == "cmd.pms.confirmar-reserva"


def test_obtener_routing_retorna_routing_para_pago_exitoso_evt():
    """Verifica que _obtener_routing retorna el routing correcto para PagoExitosoEvt."""
    dispatcher = DespachadorRabbitMQ(mapeador_eventos=None)
    
    exchange, key = dispatcher._obtener_routing("PagoExitosoEvt")
    
    assert exchange == "travelhub.events.exchange"
    assert key == "evt.pago.exitoso"


def test_obtener_routing_retorna_routing_para_reserva_confirmada_evt():
    """Verifica que _obtener_routing retorna el routing correcto para ReservaConfirmadaEvt."""
    dispatcher = DespachadorRabbitMQ(mapeador_eventos=None)
    
    exchange, key = dispatcher._obtener_routing("ReservaConfirmadaEvt")
    
    assert exchange == "travelhub.events.exchange"
    assert key == "evt.reserva.confirmada"


def test_obtener_routing_usa_fallback_para_comando_local_desconocido():
    """Verifica que _obtener_routing usa fallback para comandos locales desconocidos."""
    dispatcher = DespachadorRabbitMQ(mapeador_eventos=None)
    
    exchange, key = dispatcher._obtener_routing("MiComandoLocalCmd")
    
    assert exchange == "travelhub.commands.exchange"
    assert key.startswith("cmd.")


def test_obtener_routing_usa_fallback_para_comando_generico_desconocido():
    """Verifica que _obtener_routing usa fallback genérico para comandos desconocidos."""
    dispatcher = DespachadorRabbitMQ(mapeador_eventos=None)
    
    exchange, key = dispatcher._obtener_routing("MiComandoRaroCmd")
    
    assert exchange == "travelhub.commands.exchange"
    assert key.startswith("cmd.generico.")


def test_obtener_routing_usa_fallback_para_evento_desconocido():
    """Verifica que _obtener_routing usa fallback para eventos desconocidos."""
    dispatcher = DespachadorRabbitMQ(mapeador_eventos=None)
    
    exchange, key = dispatcher._obtener_routing("MiEventoRaroEvt")
    
    assert exchange == "travelhub.events.exchange"
    assert key.startswith("evt.generico.")


def test_obtener_routing_retorna_vacio_para_tipo_completamente_desconocido():
    """Verifica que _obtener_routing retorna vacío para tipos no reconocidos."""
    dispatcher = DespachadorRabbitMQ(mapeador_eventos=None)
    
    exchange, key = dispatcher._obtener_routing("ClaseRandom")
    
    assert exchange == ""
    assert key == ""


def test_obtener_routing_maneja_reserva_pendiente_como_evento():
    """Verifica que _obtener_routing maneja ReservaPendiente como evento."""
    dispatcher = DespachadorRabbitMQ(mapeador_eventos=None)
    
    exchange, key = dispatcher._obtener_routing("ReservaPendiente")
    
    assert exchange == "travelhub.events.exchange"
    assert key == "evt.reserva.pendiente"


# --- Pruebas de _get_channel y cerrar ---

@patch("seedwork.infraestructura.dispatchers.pika.BlockingConnection")
def test_get_channel_crea_conexion_si_no_existe(mock_connection_cls):
    """Verifica que _get_channel crea una conexión si no existe."""
    mock_connection = MagicMock()
    mock_connection.is_closed = False
    mock_channel = MagicMock()
    mock_connection.channel.return_value = mock_channel
    mock_connection_cls.return_value = mock_connection
    
    dispatcher = DespachadorRabbitMQ(mapeador_eventos=None)
    channel = dispatcher._get_channel()
    
    assert channel == mock_channel
    mock_connection_cls.assert_called_once()


@patch("seedwork.infraestructura.dispatchers.pika.BlockingConnection")
def test_get_channel_reutiliza_conexion_existente(mock_connection_cls):
    """Verifica que _get_channel reutiliza una conexión existente."""
    mock_connection = MagicMock()
    mock_connection.is_closed = False
    mock_channel = MagicMock()
    mock_connection.channel.return_value = mock_channel
    mock_connection_cls.return_value = mock_connection
    
    dispatcher = DespachadorRabbitMQ(mapeador_eventos=None)
    channel1 = dispatcher._get_channel()
    channel2 = dispatcher._get_channel()
    
    assert channel1 == channel2
    mock_connection_cls.assert_called_once()


@patch("seedwork.infraestructura.dispatchers.pika.BlockingConnection")
def test_cerrar_cierra_conexion_abierta(mock_connection_cls):
    """Verifica que cerrar cierra una conexión abierta."""
    mock_connection = MagicMock()
    mock_connection.is_closed = False
    mock_connection.is_open = True
    mock_channel = MagicMock()
    mock_connection.channel.return_value = mock_channel
    mock_connection_cls.return_value = mock_connection
    
    dispatcher = DespachadorRabbitMQ(mapeador_eventos=None)
    dispatcher._get_channel()
    dispatcher.cerrar()
    
    mock_connection.close.assert_called_once()


# --- Pruebas de publicar_evento con comandos ---

@patch("seedwork.infraestructura.dispatchers.pika.BlockingConnection")
def test_publicar_evento_publica_comando_correctamente(mock_connection_cls):
    """Verifica que publicar_evento publica un comando correctamente."""
    mock_connection = MagicMock()
    mock_connection.is_closed = False
    mock_channel = MagicMock()
    mock_connection.channel.return_value = mock_channel
    mock_connection_cls.return_value = mock_connection
    
    dispatcher = DespachadorRabbitMQ(mapeador_eventos=None)
    cmd = ProcesarPagoCmd(id_reserva=uuid.uuid4(), monto=200.0)
    
    dispatcher.publicar_evento(cmd)
    
    mock_channel.basic_publish.assert_called_once()
    call_kwargs = mock_channel.basic_publish.call_args[1]
    assert call_kwargs["exchange"] == "travelhub.commands.exchange"
    assert call_kwargs["routing_key"] == "cmd.payment.procesar-pago"


@patch("seedwork.infraestructura.dispatchers.pika.BlockingConnection")
def test_publicar_evento_serializa_comando_con_uuid(mock_connection_cls):
    """Verifica que publicar_evento serializa correctamente UUIDs en comandos."""
    mock_connection = MagicMock()
    mock_connection.is_closed = False
    mock_channel = MagicMock()
    mock_connection.channel.return_value = mock_channel
    mock_connection_cls.return_value = mock_connection
    
    dispatcher = DespachadorRabbitMQ(mapeador_eventos=None)
    id_reserva = uuid.uuid4()
    cmd = ProcesarPagoCmd(id_reserva=id_reserva, monto=200.0)
    
    dispatcher.publicar_evento(cmd)
    
    import json
    call_kwargs = mock_channel.basic_publish.call_args[1]
    body = json.loads(call_kwargs["body"])
    assert body["id_reserva"] == str(id_reserva)
    assert body["monto"] == 200.0


# --- Pruebas de publicar_evento con eventos de dominio ---

@patch("seedwork.infraestructura.dispatchers.pika.BlockingConnection")
def test_publicar_evento_ignora_eventos_sin_mapeo(mock_connection_cls):
    """Verifica que publicar_evento ignora eventos de dominio sin mapeo a integración."""
    mock_connection = MagicMock()
    mock_connection.is_closed = False
    mock_channel = MagicMock()
    mock_connection.channel.return_value = mock_channel
    mock_connection_cls.return_value = mock_connection
    
    mapeador_mock = MagicMock()
    mapeador_mock.entidad_a_dto.return_value = None
    
    from modulos.reserva.dominio.eventos import ReservaIniciada
    import datetime
    
    dispatcher = DespachadorRabbitMQ(mapeador_eventos=mapeador_mock)
    evento = ReservaIniciada(
        id_reserva=uuid.uuid4(),
        id_usuario=uuid.uuid4(),
        id_categoria=uuid.uuid4(),
        fecha_creacion=datetime.datetime.now(),
    )
    
    dispatcher.publicar_evento(evento)
    
    mock_channel.basic_publish.assert_not_called()


@patch("seedwork.infraestructura.dispatchers.pika.BlockingConnection")
def test_publicar_evento_publica_evento_con_mapeo(mock_connection_cls):
    """Verifica que publicar_evento publica eventos de dominio con mapeo a integración."""
    mock_connection = MagicMock()
    mock_connection.is_closed = False
    mock_channel = MagicMock()
    mock_connection.channel.return_value = mock_channel
    mock_connection_cls.return_value = mock_connection
    
    evento_integracion_mock = MagicMock()
    evento_integracion_mock.type = "ReservaCreadaIntegracionEvt"
    evento_integracion_mock.to_dict.return_value = {"type": "ReservaCreadaIntegracionEvt", "data": {}}
    
    mapeador_mock = MagicMock()
    mapeador_mock.entidad_a_dto.return_value = evento_integracion_mock
    
    from modulos.reserva.dominio.eventos import ReservaPendiente
    
    dispatcher = DespachadorRabbitMQ(mapeador_eventos=mapeador_mock)
    evento = ReservaPendiente(
        id_reserva=uuid.uuid4(),
        id_usuario=uuid.uuid4(),
        id_categoria=uuid.uuid4(),
    )
    
    dispatcher.publicar_evento(evento)
    
    mock_channel.basic_publish.assert_called_once()
    call_kwargs = mock_channel.basic_publish.call_args[1]
    assert call_kwargs["exchange"] == "travelhub.events.exchange"
    assert call_kwargs["routing_key"] == "evt.reserva.creada"


# --- Pruebas de publicar_comando ---

@patch("seedwork.infraestructura.dispatchers.pika.BlockingConnection")
def test_publicar_comando_publica_con_routing_key_especifico(mock_connection_cls):
    """Verifica que publicar_comando publica con routing_key específico."""
    mock_connection = MagicMock()
    mock_connection.is_closed = False
    mock_channel = MagicMock()
    mock_connection.channel.return_value = mock_channel
    mock_connection_cls.return_value = mock_connection
    
    dispatcher = DespachadorRabbitMQ(mapeador_eventos=None)
    cmd = ProcesarPagoCmd(id_reserva=uuid.uuid4(), monto=150.0)
    
    dispatcher.publicar_comando(cmd, "cmd.custom.routing")
    
    mock_channel.basic_publish.assert_called_once()
    call_kwargs = mock_channel.basic_publish.call_args[1]
    assert call_kwargs["exchange"] == "travelhub.commands.exchange"
    assert call_kwargs["routing_key"] == "cmd.custom.routing"
