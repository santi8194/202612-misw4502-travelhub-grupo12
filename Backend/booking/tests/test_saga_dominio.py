"""
Pruebas unitarias para el dominio de sagas: entidades, eventos, comandos y objetos de valor.
"""
import uuid
import datetime

from modulos.saga_reservas.dominio.entidades import SagaInstance, SagaExecutionLog
from modulos.saga_reservas.dominio.objetos_valor import EstadoSaga, TipoMensajeSaga
from modulos.saga_reservas.dominio.comandos import (
    ProcesarPagoCmd,
    ConfirmarReservaPmsCmd,
    SolicitarAprobacionManualCmd,
    MarcarSagaEsperandoVoucherCmd,
    CancelarReservaPmsCmd,
    ReversarPagoCmd,
    RechazarReservaCmd,
)
from modulos.saga_reservas.dominio.eventos import (
    PagoExitosoEvt,
    ConfirmacionPmsExitosaEvt,
    ReservaRechazadaPmsEvt,
    ReservaAprobadaManualEvt,
    ReservaRechazadaManualEvt,
    VoucherEnviadoEvt,
)


# --- Pruebas de SagaInstance ---

def test_saga_instance_se_crea_con_estado_inicial():
    """Verifica que una saga se inicializa con estado EN_PROCESO y paso 0."""
    id_saga = uuid.uuid4()
    id_reserva = uuid.uuid4()
    
    saga = SagaInstance(id=id_saga, id_reserva=id_reserva)
    
    assert saga.id == id_saga
    assert saga.id_reserva == id_reserva
    assert saga.estado_global == EstadoSaga.EN_PROCESO
    assert saga.paso_actual == 0
    assert saga.id_flujo == "RESERVA_ESTANDAR"
    assert saga.version_ejecucion == 1
    assert len(saga.historial) == 0


def test_avanzar_paso_actualiza_index_y_registra_log():
    """Verifica que avanzar_paso actualiza el paso actual y registra un log."""
    saga = SagaInstance(id=uuid.uuid4(), id_reserva=uuid.uuid4())
    
    saga.avanzar_paso(1, "ReservaCreadaIntegracionEvt", {"key": "value"})
    
    assert saga.paso_actual == 1
    assert len(saga.historial) == 1
    
    ultimo_log = saga.historial[-1]
    assert ultimo_log.accion == "ReservaCreadaIntegracionEvt"
    assert ultimo_log.tipo_mensaje == TipoMensajeSaga.EVENTO_RECIBIDO
    assert ultimo_log.payload_snapshot == {"key": "value"}
    assert ultimo_log.id_instancia == saga.id


def test_iniciar_compensacion_cambia_estado_a_compensando():
    """Verifica que iniciar_compensacion cambia el estado a COMPENSANDO."""
    saga = SagaInstance(id=uuid.uuid4(), id_reserva=uuid.uuid4())
    
    saga.iniciar_compensacion("PagoRechazadoEvt", {"motivo": "Saldo Insuficiente"})
    
    assert saga.estado_global == EstadoSaga.COMPENSANDO
    assert len(saga.historial) == 1
    assert saga.historial[-1].accion == "PagoRechazadoEvt"
    assert saga.historial[-1].payload_snapshot["motivo"] == "Saldo Insuficiente"


def test_iniciar_compensacion_sin_payload_usa_default():
    """Verifica que iniciar_compensacion sin payload usa valores por defecto."""
    id_reserva = uuid.uuid4()
    saga = SagaInstance(id=uuid.uuid4(), id_reserva=id_reserva)
    
    saga.iniciar_compensacion("ErrorGenerico")
    
    assert saga.estado_global == EstadoSaga.COMPENSANDO
    assert saga.historial[-1].payload_snapshot["id_reserva"] == str(id_reserva)
    assert "motivo" in saga.historial[-1].payload_snapshot


def test_registrar_comando_emitido():
    """Verifica que registrar_comando_emitido agrega un log de tipo COMANDO_EMITIDO."""
    saga = SagaInstance(id=uuid.uuid4(), id_reserva=uuid.uuid4())
    
    saga.registrar_comando_emitido("ProcesarPagoCmd", {"monto": 100})
    
    assert len(saga.historial) == 1
    assert saga.historial[-1].tipo_mensaje == TipoMensajeSaga.COMANDO_EMITIDO
    assert saga.historial[-1].accion == "ProcesarPagoCmd"
    assert saga.historial[-1].payload_snapshot["monto"] == 100


def test_saga_instance_puede_tener_multiples_logs():
    """Verifica que una saga puede acumular múltiples logs en el historial."""
    saga = SagaInstance(id=uuid.uuid4(), id_reserva=uuid.uuid4())
    
    saga.avanzar_paso(1, "Evento1", {})
    saga.registrar_comando_emitido("Comando1", {})
    saga.avanzar_paso(2, "Evento2", {})
    
    assert len(saga.historial) == 3
    assert saga.historial[0].tipo_mensaje == TipoMensajeSaga.EVENTO_RECIBIDO
    assert saga.historial[1].tipo_mensaje == TipoMensajeSaga.COMANDO_EMITIDO
    assert saga.historial[2].tipo_mensaje == TipoMensajeSaga.EVENTO_RECIBIDO


# --- Pruebas de SagaExecutionLog ---

def test_saga_execution_log_guarda_datos_correctamente():
    """Verifica que SagaExecutionLog almacena correctamente todos los campos."""
    log_id = uuid.uuid4()
    instancia_id = uuid.uuid4()
    payload = {"dato": "valor"}
    
    log = SagaExecutionLog(
        id=log_id,
        id_instancia=instancia_id,
        tipo_mensaje=TipoMensajeSaga.EVENTO_RECIBIDO,
        accion="TestEvento",
        payload_snapshot=payload,
    )
    
    assert log.id == log_id
    assert log.id_instancia == instancia_id
    assert log.tipo_mensaje == TipoMensajeSaga.EVENTO_RECIBIDO
    assert log.accion == "TestEvento"
    assert log.payload_snapshot == payload
    assert isinstance(log.fecha_registro, datetime.datetime)


# --- Pruebas de Comandos (dataclasses) ---

def test_procesar_pago_cmd_guarda_campos():
    """Verifica que ProcesarPagoCmd almacena id_reserva y monto."""
    id_reserva = uuid.uuid4()
    cmd = ProcesarPagoCmd(id_reserva=id_reserva, monto=150.0)
    
    assert cmd.id_reserva == id_reserva
    assert cmd.monto == 150.0


def test_confirmar_reserva_pms_cmd_guarda_campos():
    """Verifica que ConfirmarReservaPmsCmd almacena todos los campos."""
    id_reserva = uuid.uuid4()
    id_habitacion = uuid.uuid4()
    cmd = ConfirmarReservaPmsCmd(
        id_reserva=id_reserva,
        id_habitacion=id_habitacion,
        fecha_reserva="2026-04-01"
    )
    
    assert cmd.id_reserva == id_reserva
    assert cmd.id_habitacion == id_habitacion
    assert cmd.fecha_reserva == "2026-04-01"


def test_solicitar_aprobacion_manual_cmd_guarda_campos():
    """Verifica que SolicitarAprobacionManualCmd almacena los campos."""
    id_reserva = uuid.uuid4()
    id_habitacion = uuid.uuid4()
    cmd = SolicitarAprobacionManualCmd(id_reserva=id_reserva, id_habitacion=id_habitacion)
    
    assert cmd.id_reserva == id_reserva
    assert cmd.id_habitacion == id_habitacion


def test_marcar_saga_esperando_voucher_cmd():
    """Verifica que MarcarSagaEsperandoVoucherCmd almacena id_reserva."""
    id_reserva = uuid.uuid4()
    cmd = MarcarSagaEsperandoVoucherCmd(id_reserva=id_reserva)
    
    assert cmd.id_reserva == id_reserva


def test_cancelar_reserva_pms_cmd_guarda_campos():
    """Verifica que CancelarReservaPmsCmd (compensación) almacena los campos."""
    id_reserva = uuid.uuid4()
    id_habitacion = uuid.uuid4()
    cmd = CancelarReservaPmsCmd(id_reserva=id_reserva, id_habitacion=id_habitacion)
    
    assert cmd.id_reserva == id_reserva
    assert cmd.id_habitacion == id_habitacion


def test_reversar_pago_cmd_guarda_campos():
    """Verifica que ReversarPagoCmd (compensación) almacena los campos."""
    id_reserva = uuid.uuid4()
    cmd = ReversarPagoCmd(id_reserva=id_reserva, monto=200.0)
    
    assert cmd.id_reserva == id_reserva
    assert cmd.monto == 200.0


def test_rechazar_reserva_cmd():
    """Verifica que RechazarReservaCmd (detonante manual) almacena id_reserva."""
    id_reserva = uuid.uuid4()
    cmd = RechazarReservaCmd(id_reserva=id_reserva)
    
    assert cmd.id_reserva == id_reserva


# --- Pruebas de Eventos (dataclasses) ---

def test_pago_exitoso_evt_guarda_campos():
    """Verifica que PagoExitosoEvt almacena id_reserva y token."""
    id_reserva = uuid.uuid4()
    evt = PagoExitosoEvt(id_reserva=id_reserva, token_pasarela="tok_123")
    
    assert evt.id_reserva == id_reserva
    assert evt.token_pasarela == "tok_123"


def test_confirmacion_pms_exitosa_evt_guarda_campos():
    """Verifica que ConfirmacionPmsExitosaEvt almacena id_reserva y codigo_pms."""
    id_reserva = uuid.uuid4()
    evt = ConfirmacionPmsExitosaEvt(id_reserva=id_reserva, codigo_pms="PMS-001")
    
    assert evt.id_reserva == id_reserva
    assert evt.codigo_pms == "PMS-001"


def test_reserva_rechazada_pms_evt_guarda_campos():
    """Verifica que ReservaRechazadaPmsEvt almacena id_reserva y motivo."""
    id_reserva = uuid.uuid4()
    evt = ReservaRechazadaPmsEvt(id_reserva=id_reserva, motivo="No disponible")
    
    assert evt.id_reserva == id_reserva
    assert evt.motivo == "No disponible"


def test_reserva_aprobada_manual_evt():
    """Verifica que ReservaAprobadaManualEvt almacena id_reserva."""
    id_reserva = uuid.uuid4()
    evt = ReservaAprobadaManualEvt(id_reserva=id_reserva)
    
    assert evt.id_reserva == id_reserva


def test_reserva_rechazada_manual_evt_guarda_campos():
    """Verifica que ReservaRechazadaManualEvt almacena id_reserva y motivo."""
    id_reserva = uuid.uuid4()
    evt = ReservaRechazadaManualEvt(id_reserva=id_reserva, motivo="Rechazado por admin")
    
    assert evt.id_reserva == id_reserva
    assert evt.motivo == "Rechazado por admin"


def test_voucher_enviado_evt_guarda_campos():
    """Verifica que VoucherEnviadoEvt almacena id_reserva y email."""
    id_reserva = uuid.uuid4()
    evt = VoucherEnviadoEvt(id_reserva=id_reserva, email="cliente@test.com")
    
    assert evt.id_reserva == id_reserva
    assert evt.email == "cliente@test.com"


# --- Pruebas de Enums ---

def test_estado_saga_enum_tiene_todos_los_valores():
    """Verifica que EstadoSaga tiene todos los estados esperados."""
    assert EstadoSaga.EN_PROCESO.value == "EN_PROCESO"
    assert EstadoSaga.PAUSADA_ESPERANDO_HOTEL.value == "PAUSADA_ESPERANDO_HOTEL"
    assert EstadoSaga.COMPLETADA.value == "COMPLETADA"
    assert EstadoSaga.COMPENSANDO.value == "COMPENSANDO"
    assert EstadoSaga.COMPENSACION_EXITOSA.value == "COMPENSACION_EXITOSA"
    assert EstadoSaga.COMPENSACION_FALLIDA.value == "COMPENSACION_FALLIDA"


def test_tipo_mensaje_saga_enum_tiene_todos_los_valores():
    """Verifica que TipoMensajeSaga tiene todos los tipos esperados."""
    assert TipoMensajeSaga.COMANDO_EMITIDO.value == "COMANDO_EMITIDO"
    assert TipoMensajeSaga.EVENTO_RECIBIDO.value == "EVENTO_RECIBIDO"
    assert TipoMensajeSaga.COMPENSACION_EMITIDA.value == "COMPENSACION_EMITIDA"
