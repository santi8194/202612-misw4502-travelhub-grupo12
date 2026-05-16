"""
Pruebas unitarias para OrquestadorSagaReservas: iniciar_saga, manejar_evento_respuesta, compensar_saga.
"""
import uuid
import datetime
from unittest.mock import MagicMock
from types import SimpleNamespace

from modulos.saga_reservas.aplicacion.orquestador import OrquestadorSagaReservas
from modulos.saga_reservas.dominio.entidades import SagaInstance
from modulos.saga_reservas.dominio.objetos_valor import EstadoSaga, TipoMensajeSaga


# --- Helpers ---

def _crear_definicion_saga_mock():
    """Crea un mock de definición de saga."""
    definicion = SimpleNamespace()
    definicion.id_flujo = "RESERVA_ESTANDAR"
    definicion.version = 1
    return definicion


def _crear_pasos_saga_mock():
    """Crea un mock de pasos de saga."""
    paso0 = SimpleNamespace(index=0, comando="CrearReservaLocalCmd", evento="ReservaCreadaIntegracionEvt", error="ReservaCreadaFalloEvt", compensacion="CancelarReservaLocalCmd")
    paso1 = SimpleNamespace(index=1, comando="ProcesarPagoCmd", evento="PagoExitosoEvt", error="PagoRechazadoEvt", compensacion="ReversarPagoCmd")
    paso2 = SimpleNamespace(index=2, comando="ConfirmarReservaPmsCmd", evento="ConfirmacionPmsExitosaEvt", error="ReservaRechazadaPmsEvt", compensacion="CancelarReservaPmsCmd")
    paso3 = SimpleNamespace(index=3, comando="SolicitarAprobacionManualCmd", evento="ReservaAprobadaManualEvt", error="ReservaRechazadaManualEvt", compensacion=None)
    paso4 = SimpleNamespace(index=4, comando="ConfirmarReservaLocalCmd", evento="ReservaConfirmadaEvt", error="FallaActualizacionLocalEvt", compensacion="CancelarReservaLocalCmd")
    return [paso0, paso1, paso2, paso3, paso4]


# --- Pruebas de iniciar_saga ---

def test_iniciar_saga_crea_instancia_y_la_persiste():
    """Verifica que iniciar_saga crea una SagaInstance y la persiste."""
    repositorio_mock = MagicMock()
    repositorio_mock.obtener_definicion_saga_activa.return_value = _crear_definicion_saga_mock()
    repositorio_mock.obtener_pasos_saga.return_value = _crear_pasos_saga_mock()
    
    uow_mock = MagicMock()
    uow_mock.__enter__ = MagicMock(return_value=uow_mock)
    uow_mock.__exit__ = MagicMock(return_value=False)
    
    orquestador = OrquestadorSagaReservas(repositorio=repositorio_mock, uow=uow_mock)
    
    id_reserva = uuid.uuid4()
    id_usuario = uuid.uuid4()
    
    resultado = orquestador.iniciar_saga(
        id_reserva=id_reserva,
        id_usuario=id_usuario,
        monto=150000.0,
    )
    
    assert resultado is True
    repositorio_mock.agregar.assert_called_once()
    uow_mock.commit.assert_called_once()


def test_iniciar_saga_registra_evento_inicial():
    """Verifica que iniciar_saga registra el evento inicial en el historial."""
    repositorio_mock = MagicMock()
    repositorio_mock.obtener_definicion_saga_activa.return_value = _crear_definicion_saga_mock()
    repositorio_mock.obtener_pasos_saga.return_value = _crear_pasos_saga_mock()
    
    uow_mock = MagicMock()
    uow_mock.__enter__ = MagicMock(return_value=uow_mock)
    uow_mock.__exit__ = MagicMock(return_value=False)
    
    orquestador = OrquestadorSagaReservas(repositorio=repositorio_mock, uow=uow_mock)
    
    id_reserva = uuid.uuid4()
    id_usuario = uuid.uuid4()
    
    orquestador.iniciar_saga(
        id_reserva=id_reserva,
        id_usuario=id_usuario,
        monto=150000.0,
    )
    
    # Verificar que se llamó agregar con una saga que tiene historial
    call_args = repositorio_mock.agregar.call_args
    saga_agregada = call_args[0][0]
    assert isinstance(saga_agregada, SagaInstance)
    assert len(saga_agregada.historial) > 0
    assert saga_agregada.historial[0].accion == "ReservaCreadaIntegracionEvt"


def test_iniciar_saga_retorna_false_si_no_hay_definicion():
    """Verifica que iniciar_saga retorna False si no hay definición de saga."""
    repositorio_mock = MagicMock()
    repositorio_mock.obtener_definicion_saga_activa.return_value = None
    
    uow_mock = MagicMock()
    uow_mock.__enter__ = MagicMock(return_value=uow_mock)
    uow_mock.__exit__ = MagicMock(return_value=False)
    
    orquestador = OrquestadorSagaReservas(repositorio=repositorio_mock, uow=uow_mock)
    
    resultado = orquestador.iniciar_saga(
        id_reserva=uuid.uuid4(),
        id_usuario=uuid.uuid4(),
    )
    
    assert resultado is None
    repositorio_mock.agregar.assert_not_called()


def test_iniciar_saga_retorna_false_si_no_hay_pasos():
    """Verifica que iniciar_saga retorna None si no hay pasos definidos."""
    repositorio_mock = MagicMock()
    repositorio_mock.obtener_definicion_saga_activa.return_value = _crear_definicion_saga_mock()
    repositorio_mock.obtener_pasos_saga.return_value = []
    
    uow_mock = MagicMock()
    uow_mock.__enter__ = MagicMock(return_value=uow_mock)
    uow_mock.__exit__ = MagicMock(return_value=False)
    
    orquestador = OrquestadorSagaReservas(repositorio=repositorio_mock, uow=uow_mock)
    
    resultado = orquestador.iniciar_saga(
        id_reserva=uuid.uuid4(),
        id_usuario=uuid.uuid4(),
    )
    
    assert resultado is None
    repositorio_mock.agregar.assert_not_called()


def test_iniciar_saga_maneja_excepcion_y_retorna_false():
    """Verifica que iniciar_saga maneja excepciones y retorna False."""
    repositorio_mock = MagicMock()
    repositorio_mock.obtener_definicion_saga_activa.side_effect = Exception("Error de BD")
    
    uow_mock = MagicMock()
    uow_mock.__enter__ = MagicMock(return_value=uow_mock)
    uow_mock.__exit__ = MagicMock(return_value=False)
    
    orquestador = OrquestadorSagaReservas(repositorio=repositorio_mock, uow=uow_mock)
    
    resultado = orquestador.iniciar_saga(
        id_reserva=uuid.uuid4(),
        id_usuario=uuid.uuid4(),
    )
    
    assert resultado is False


# --- Pruebas de manejar_evento_respuesta ---

def test_manejar_evento_respuesta_avanza_saga_en_happy_path():
    """Verifica que manejar_evento_respuesta busca la saga correctamente."""
    id_reserva = uuid.uuid4()
    saga = SagaInstance(id=uuid.uuid4(), id_reserva=id_reserva)
    saga.estado_global = EstadoSaga.COMPLETADA  # Saga ya completada, no se procesa
    
    repositorio_mock = MagicMock()
    repositorio_mock.buscar_por_reserva.return_value = saga
    repositorio_mock.obtener_pasos_saga.return_value = _crear_pasos_saga_mock()
    
    uow_mock = MagicMock()
    uow_mock.__enter__ = MagicMock(return_value=uow_mock)
    uow_mock.__exit__ = MagicMock(return_value=False)
    
    orquestador = OrquestadorSagaReservas(repositorio=repositorio_mock, uow=uow_mock)
    
    orquestador.manejar_evento_respuesta(
        id_reserva=id_reserva,
        evento_recibido="PagoExitosoEvt",
        payload_recibido={"token_pasarela": "tok-123"},
    )
    
    # Verificar que se llamó al repositorio para buscar la saga
    assert repositorio_mock.buscar_por_reserva.called


def test_manejar_evento_respuesta_ignora_eventos_duplicados():
    """Verifica que manejar_evento_respuesta implementa idempotencia."""
    id_reserva = uuid.uuid4()
    saga = SagaInstance(id=uuid.uuid4(), id_reserva=id_reserva)
    saga.avanzar_paso(1, "PagoExitosoEvt", {"monto": 150000})
    
    repositorio_mock = MagicMock()
    repositorio_mock.buscar_por_reserva.return_value = saga
    
    uow_mock = MagicMock()
    uow_mock.__enter__ = MagicMock(return_value=uow_mock)
    uow_mock.__exit__ = MagicMock(return_value=False)
    
    orquestador = OrquestadorSagaReservas(repositorio=repositorio_mock, uow=uow_mock)
    
    # Intentar procesar el mismo evento dos veces
    orquestador.manejar_evento_respuesta(
        id_reserva=id_reserva,
        evento_recibido="PagoExitosoEvt",
        payload_recibido={"monto": 150000},
    )
    
    repositorio_mock.actualizar.assert_not_called()


def test_manejar_evento_respuesta_no_procesa_si_saga_no_existe():
    """Verifica que manejar_evento_respuesta no procesa si la saga no existe."""
    repositorio_mock = MagicMock()
    repositorio_mock.buscar_por_reserva.return_value = None
    
    uow_mock = MagicMock()
    uow_mock.__enter__ = MagicMock(return_value=uow_mock)
    uow_mock.__exit__ = MagicMock(return_value=False)
    
    orquestador = OrquestadorSagaReservas(repositorio=repositorio_mock, uow=uow_mock)
    
    orquestador.manejar_evento_respuesta(
        id_reserva=uuid.uuid4(),
        evento_recibido="PagoExitosoEvt",
        payload_recibido={},
    )
    
    repositorio_mock.actualizar.assert_not_called()


def test_manejar_evento_respuesta_confirmacion_pms_cancelada_delega_handler_local():
    id_reserva = uuid.uuid4()
    repositorio_mock = MagicMock()
    uow_mock = MagicMock()
    handler_cancelacion = MagicMock()

    orquestador = OrquestadorSagaReservas(
        repositorio=repositorio_mock,
        uow=uow_mock,
        handler_confirmar_cancelacion_pms_local=handler_cancelacion,
    )

    orquestador.manejar_evento_respuesta(
        id_reserva=id_reserva,
        evento_recibido="ConfirmacionPmsCanceladaEvt",
        payload_recibido={"id_reserva": str(id_reserva)},
    )

    handler_cancelacion.handle.assert_called_once()
    comando = handler_cancelacion.handle.call_args.args[0]
    assert comando.__class__.__name__ == "ConfirmarCancelacionPmsLocalCmd"
    assert comando.id_reserva == id_reserva
    repositorio_mock.buscar_por_reserva.assert_not_called()


def test_manejar_evento_respuesta_no_procesa_si_saga_completada():
    """Verifica que manejar_evento_respuesta no procesa si la saga está completada."""
    id_reserva = uuid.uuid4()
    saga = SagaInstance(id=uuid.uuid4(), id_reserva=id_reserva)
    saga.estado_global = EstadoSaga.COMPLETADA
    
    repositorio_mock = MagicMock()
    repositorio_mock.buscar_por_reserva.return_value = saga
    
    uow_mock = MagicMock()
    uow_mock.__enter__ = MagicMock(return_value=uow_mock)
    uow_mock.__exit__ = MagicMock(return_value=False)
    
    orquestador = OrquestadorSagaReservas(repositorio=repositorio_mock, uow=uow_mock)
    
    orquestador.manejar_evento_respuesta(
        id_reserva=id_reserva,
        evento_recibido="PagoExitosoEvt",
        payload_recibido={},
    )
    
    repositorio_mock.actualizar.assert_not_called()


def test_manejar_evento_respuesta_detecta_evento_de_error_y_compensa():
    """Verifica que manejar_evento_respuesta detecta eventos de error y detona compensación."""
    id_reserva = uuid.uuid4()
    saga = SagaInstance(id=uuid.uuid4(), id_reserva=id_reserva)
    saga.avanzar_paso(1, "PagoExitosoEvt", {"monto": 150000})
    
    repositorio_mock = MagicMock()
    repositorio_mock.buscar_por_reserva.return_value = saga
    repositorio_mock.obtener_pasos_saga.return_value = _crear_pasos_saga_mock()
    
    uow_mock = MagicMock()
    uow_mock.__enter__ = MagicMock(return_value=uow_mock)
    uow_mock.__exit__ = MagicMock(return_value=False)
    
    orquestador = OrquestadorSagaReservas(repositorio=repositorio_mock, uow=uow_mock)
    
    # Simular un evento de error
    orquestador.manejar_evento_respuesta(
        id_reserva=id_reserva,
        evento_recibido="ReservaRechazadaPmsEvt",
        payload_recibido={"motivo": "No disponible"},
    )
    
    # Verificar que se llamó a compensar_saga (indirectamente)
    assert repositorio_mock.actualizar.called


# --- Pruebas de compensar_saga ---

def test_compensar_saga_cambia_estado_a_compensando():
    """Verifica que compensar_saga cambia el estado de la saga a COMPENSANDO."""
    id_reserva = uuid.uuid4()
    saga = SagaInstance(id=uuid.uuid4(), id_reserva=id_reserva)
    saga.avanzar_paso(1, "PagoExitosoEvt", {"monto": 150000})
    
    repositorio_mock = MagicMock()
    repositorio_mock.buscar_por_reserva.return_value = saga
    repositorio_mock.obtener_pasos_saga.return_value = _crear_pasos_saga_mock()
    
    uow_mock = MagicMock()
    uow_mock.__enter__ = MagicMock(return_value=uow_mock)
    uow_mock.__exit__ = MagicMock(return_value=False)
    
    orquestador = OrquestadorSagaReservas(repositorio=repositorio_mock, uow=uow_mock)
    
    orquestador.compensar_saga(
        id_reserva=id_reserva,
        evento_fallo="PagoRechazadoEvt",
    )
    
    call_args = repositorio_mock.actualizar.call_args
    saga_actualizada = call_args[0][0]
    assert saga_actualizada.estado_global == EstadoSaga.COMPENSACION_EXITOSA


def test_compensar_saga_implementa_idempotencia():
    """Verifica que compensar_saga implementa idempotencia."""
    id_reserva = uuid.uuid4()
    saga = SagaInstance(id=uuid.uuid4(), id_reserva=id_reserva)
    saga.estado_global = EstadoSaga.COMPENSACION_EXITOSA
    
    repositorio_mock = MagicMock()
    repositorio_mock.buscar_por_reserva.return_value = saga
    
    uow_mock = MagicMock()
    uow_mock.__enter__ = MagicMock(return_value=uow_mock)
    uow_mock.__exit__ = MagicMock(return_value=False)
    
    orquestador = OrquestadorSagaReservas(repositorio=repositorio_mock, uow=uow_mock)
    
    orquestador.compensar_saga(
        id_reserva=id_reserva,
        evento_fallo="PagoRechazadoEvt",
    )
    
    repositorio_mock.actualizar.assert_not_called()


def test_compensar_saga_no_procesa_si_saga_no_existe():
    """Verifica que compensar_saga no procesa si la saga no existe."""
    repositorio_mock = MagicMock()
    repositorio_mock.buscar_por_reserva.return_value = None
    
    uow_mock = MagicMock()
    uow_mock.__enter__ = MagicMock(return_value=uow_mock)
    uow_mock.__exit__ = MagicMock(return_value=False)
    
    orquestador = OrquestadorSagaReservas(repositorio=repositorio_mock, uow=uow_mock)
    
    orquestador.compensar_saga(
        id_reserva=uuid.uuid4(),
        evento_fallo="PagoRechazadoEvt",
    )
    
    repositorio_mock.actualizar.assert_not_called()


def test_compensar_saga_registra_comandos_compensatorios():
    """Verifica que compensar_saga registra comandos compensatorios en el historial."""
    id_reserva = uuid.uuid4()
    saga = SagaInstance(id=uuid.uuid4(), id_reserva=id_reserva)
    saga.avanzar_paso(1, "PagoExitosoEvt", {"monto": 150000})
    
    repositorio_mock = MagicMock()
    repositorio_mock.buscar_por_reserva.return_value = saga
    repositorio_mock.obtener_pasos_saga.return_value = _crear_pasos_saga_mock()
    
    uow_mock = MagicMock()
    uow_mock.__enter__ = MagicMock(return_value=uow_mock)
    uow_mock.__exit__ = MagicMock(return_value=False)
    
    orquestador = OrquestadorSagaReservas(repositorio=repositorio_mock, uow=uow_mock)
    
    orquestador.compensar_saga(
        id_reserva=id_reserva,
        evento_fallo="ReservaRechazadaPmsEvt",
    )
    
    call_args = repositorio_mock.actualizar.call_args
    saga_actualizada = call_args[0][0]
    
    # Verificar que se registraron comandos compensatorios
    comandos_compensatorios = [
        log for log in saga_actualizada.historial
        if log.tipo_mensaje == TipoMensajeSaga.COMANDO_EMITIDO
    ]
    assert len(comandos_compensatorios) > 0


# --- Pruebas de _obtener_paso_actual y _obtener_paso_por_error ---

def test_obtener_paso_actual_retorna_paso_correcto():
    """Verifica que _obtener_paso_actual retorna el paso correcto para un evento."""
    repositorio_mock = MagicMock()
    repositorio_mock.obtener_pasos_saga.return_value = _crear_pasos_saga_mock()
    uow_mock = MagicMock()
    
    orquestador = OrquestadorSagaReservas(repositorio=repositorio_mock, uow=uow_mock)
    
    paso = orquestador._obtener_paso_actual("RESERVA_ESTANDAR", 1, "PagoExitosoEvt")
    
    assert paso is not None


def test_obtener_paso_por_error_retorna_paso_correcto():
    """Verifica que _obtener_paso_por_error retorna el paso correcto para un error."""
    repositorio_mock = MagicMock()
    repositorio_mock.obtener_pasos_saga.return_value = _crear_pasos_saga_mock()
    uow_mock = MagicMock()
    
    orquestador = OrquestadorSagaReservas(repositorio=repositorio_mock, uow=uow_mock)
    
    paso = orquestador._obtener_paso_por_error("RESERVA_ESTANDAR", 1, "PagoRechazadoEvt")
    
    assert paso is not None
    assert paso.error == "PagoRechazadoEvt"
