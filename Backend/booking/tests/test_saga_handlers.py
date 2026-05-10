"""
Pruebas unitarias para los handlers de saga: IniciarSagaHandler, RespuestaSagaHandler, CompensarSagaHandler.
"""
import uuid
from unittest.mock import MagicMock

from modulos.reserva.dominio.eventos import ReservaPendiente
from modulos.saga_reservas.dominio.eventos import RechazarReservaCmd
from modulos.saga_reservas.aplicacion.handlers import (
    IniciarSagaHandler,
    RespuestaSagaHandler,
    CompensarSagaHandler,
)


# --- Pruebas de IniciarSagaHandler ---

def test_iniciar_saga_handler_llama_orquestador_iniciar_saga():
    """Verifica que IniciarSagaHandler invoca iniciar_saga del orquestador."""
    orquestador_mock = MagicMock()
    handler = IniciarSagaHandler(orquestador=orquestador_mock)
    
    id_reserva = uuid.uuid4()
    id_usuario = uuid.uuid4()
    id_categoria = uuid.uuid4()
    
    evento = ReservaPendiente(
        id_reserva=id_reserva,
        id_usuario=id_usuario,
        id_categoria=id_categoria,
    )
    
    handler.handle(evento)
    
    orquestador_mock.iniciar_saga.assert_called_once_with(
        id_reserva=id_reserva,
        id_usuario=id_usuario,
        id_categoria=id_categoria,
    )


def test_iniciar_saga_handler_extrae_correctamente_datos_del_evento():
    """Verifica que IniciarSagaHandler extrae correctamente los datos del evento."""
    orquestador_mock = MagicMock()
    handler = IniciarSagaHandler(orquestador=orquestador_mock)
    
    id_reserva = uuid.uuid4()
    id_usuario = uuid.uuid4()
    id_categoria = uuid.uuid4()
    
    evento = ReservaPendiente(
        id_reserva=id_reserva,
        id_usuario=id_usuario,
        id_categoria=id_categoria,
    )
    
    handler.handle(evento)
    
    call_args = orquestador_mock.iniciar_saga.call_args
    assert call_args.kwargs["id_reserva"] == id_reserva
    assert call_args.kwargs["id_usuario"] == id_usuario
    assert call_args.kwargs["id_categoria"] == id_categoria


# --- Pruebas de RespuestaSagaHandler ---

def test_respuesta_saga_handler_llama_manejar_evento_respuesta():
    """Verifica que RespuestaSagaHandler invoca manejar_evento_respuesta del orquestador."""
    orquestador_mock = MagicMock()
    handler = RespuestaSagaHandler(orquestador=orquestador_mock)
    
    id_reserva = uuid.uuid4()
    
    # Crear un evento mock con id_reserva
    evento_mock = MagicMock()
    evento_mock.id_reserva = id_reserva
    evento_mock.__class__.__name__ = "PagoExitosoEvt"
    evento_mock.token_pasarela = "tok_123"
    
    handler.handle(evento_mock)
    
    orquestador_mock.manejar_evento_respuesta.assert_called_once()
    call_args = orquestador_mock.manejar_evento_respuesta.call_args
    assert call_args.kwargs["id_reserva"] == id_reserva
    assert call_args.kwargs["evento_recibido"] == "PagoExitosoEvt"


def test_respuesta_saga_handler_ignora_eventos_sin_id_reserva():
    """Verifica que RespuestaSagaHandler ignora eventos sin id_reserva."""
    orquestador_mock = MagicMock()
    handler = RespuestaSagaHandler(orquestador=orquestador_mock)
    
    # Evento sin id_reserva
    evento_mock = MagicMock(spec=[])
    
    handler.handle(evento_mock)
    
    orquestador_mock.manejar_evento_respuesta.assert_not_called()


def test_respuesta_saga_handler_elimina_campos_base_del_payload():
    """Verifica que RespuestaSagaHandler elimina campos base del framework antes de pasar el payload."""
    orquestador_mock = MagicMock()
    handler = RespuestaSagaHandler(orquestador=orquestador_mock)
    
    id_reserva = uuid.uuid4()
    
    # Crear un evento con campos base y campos de negocio
    evento_mock = MagicMock()
    evento_mock.id_reserva = id_reserva
    evento_mock.id = uuid.uuid4()
    evento_mock.fecha_creacion = "2026-04-01"
    evento_mock.correlacion_id = "corr-123"
    evento_mock.token_pasarela = "tok_456"
    evento_mock.__class__.__name__ = "PagoExitosoEvt"
    
    handler.handle(evento_mock)
    
    call_args = orquestador_mock.manejar_evento_respuesta.call_args
    payload = call_args.kwargs["payload_recibido"]
    
    # Los campos base no deben estar en el payload
    assert "id_reserva" not in payload
    assert "id" not in payload
    assert "fecha_creacion" not in payload
    assert "correlacion_id" not in payload
    
    # Los campos de negocio sí deben estar
    assert payload["token_pasarela"] == "tok_456"


# --- Pruebas de CompensarSagaHandler ---

def test_compensar_saga_handler_llama_compensar_saga():
    """Verifica que CompensarSagaHandler invoca compensar_saga del orquestador."""
    orquestador_mock = MagicMock()
    handler = CompensarSagaHandler(orquestador=orquestador_mock)
    
    id_reserva = uuid.uuid4()
    comando = RechazarReservaCmd(id_reserva=id_reserva)
    
    handler.handle(comando)
    
    orquestador_mock.compensar_saga.assert_called_once_with(
        id_reserva=id_reserva,
        evento_fallo="RechazarReservaManualCmd",
    )


def test_compensar_saga_handler_extrae_correctamente_id_reserva():
    """Verifica que CompensarSagaHandler extrae correctamente el id_reserva del comando."""
    orquestador_mock = MagicMock()
    handler = CompensarSagaHandler(orquestador=orquestador_mock)
    
    id_reserva = uuid.uuid4()
    comando = RechazarReservaCmd(id_reserva=id_reserva)
    
    handler.handle(comando)
    
    call_args = orquestador_mock.compensar_saga.call_args
    assert call_args.kwargs["id_reserva"] == id_reserva
    assert call_args.kwargs["evento_fallo"] == "RechazarReservaManualCmd"
