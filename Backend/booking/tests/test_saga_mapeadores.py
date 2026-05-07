"""
Pruebas unitarias para los mapeadores de saga: MapeadorSagaLogDTO y MapeadorSagaInstanceDTO.
"""
import uuid
import datetime

from modulos.saga_reservas.dominio.entidades import SagaInstance, SagaExecutionLog
from modulos.saga_reservas.dominio.objetos_valor import EstadoSaga, TipoMensajeSaga
from modulos.saga_reservas.infraestructura.dto import SagaInstanceDTO, SagaExecutionLogDTO
from modulos.saga_reservas.infraestructura.mapeadores import (
    MapeadorSagaLogDTO,
    MapeadorSagaInstanceDTO,
)


# --- Pruebas de MapeadorSagaLogDTO ---

def test_mapeador_log_convierte_log_a_dto():
    """Verifica que log_a_dto convierte SagaExecutionLog a SagaExecutionLogDTO."""
    log_id = uuid.uuid4()
    instancia_id = uuid.uuid4()
    payload = {"dato": "valor"}
    fecha = datetime.datetime(2026, 4, 1, 10, 0, 0)
    
    log = SagaExecutionLog(
        id=log_id,
        id_instancia=instancia_id,
        tipo_mensaje=TipoMensajeSaga.EVENTO_RECIBIDO,
        accion="TestEvento",
        payload_snapshot=payload,
    )
    log.fecha_registro = fecha
    
    mapeador = MapeadorSagaLogDTO()
    dto = mapeador.log_a_dto(log, str(instancia_id))
    
    assert dto.id == str(log_id)
    assert dto.id_instancia == str(instancia_id)
    assert dto.tipo_mensaje == "EVENTO_RECIBIDO"
    assert dto.accion == "TestEvento"
    assert dto.payload_snapshot == payload
    assert dto.fecha_registro == fecha


def test_mapeador_log_convierte_dto_a_log():
    """Verifica que dto_a_log convierte SagaExecutionLogDTO a SagaExecutionLog."""
    log_id = uuid.uuid4()
    instancia_id = uuid.uuid4()
    payload = {"dato": "valor"}
    fecha = datetime.datetime(2026, 4, 1, 10, 0, 0)
    
    dto = SagaExecutionLogDTO(
        id=str(log_id),
        id_instancia=str(instancia_id),
        tipo_mensaje="COMANDO_EMITIDO",
        accion="TestComando",
        payload_snapshot=payload,
        fecha_registro=fecha,
    )
    
    mapeador = MapeadorSagaLogDTO()
    log = mapeador.dto_a_log(dto)
    
    assert log.id == log_id
    assert log.id_instancia == instancia_id
    assert log.tipo_mensaje == TipoMensajeSaga.COMANDO_EMITIDO
    assert log.accion == "TestComando"
    assert log.payload_snapshot == payload
    assert log.fecha_registro == fecha


def test_mapeador_log_maneja_tipo_mensaje_compensacion():
    """Verifica que el mapeador maneja correctamente el tipo COMPENSACION_EMITIDA."""
    log_id = uuid.uuid4()
    instancia_id = uuid.uuid4()
    
    log = SagaExecutionLog(
        id=log_id,
        id_instancia=instancia_id,
        tipo_mensaje=TipoMensajeSaga.COMPENSACION_EMITIDA,
        accion="ReversarPagoCmd",
        payload_snapshot={},
    )
    
    mapeador = MapeadorSagaLogDTO()
    dto = mapeador.log_a_dto(log, str(instancia_id))
    
    assert dto.tipo_mensaje == "COMPENSACION_EMITIDA"
    
    # Convertir de vuelta
    log_recuperado = mapeador.dto_a_log(dto)
    assert log_recuperado.tipo_mensaje == TipoMensajeSaga.COMPENSACION_EMITIDA


# --- Pruebas de MapeadorSagaInstanceDTO ---

def test_mapeador_instance_obtener_tipo_retorna_saga_instance():
    """Verifica que obtener_tipo retorna la clase SagaInstance."""
    mapeador = MapeadorSagaInstanceDTO()
    tipo = mapeador.obtener_tipo()
    
    assert tipo == SagaInstance


def test_mapeador_instance_convierte_entidad_a_dto():
    """Verifica que entidad_a_dto convierte SagaInstance a SagaInstanceDTO."""
    saga_id = uuid.uuid4()
    reserva_id = uuid.uuid4()
    fecha_creacion = datetime.datetime(2026, 4, 1, 10, 0, 0)
    fecha_actualizacion = datetime.datetime(2026, 4, 1, 10, 5, 0)
    
    saga = SagaInstance(
        id=saga_id,
        id_reserva=reserva_id,
        id_flujo="RESERVA_ESTANDAR",
        version_ejecucion=1,
    )
    saga.estado_global = EstadoSaga.EN_PROCESO
    saga.fecha_creacion = fecha_creacion
    saga.ultima_actualizacion = fecha_actualizacion
    
    # Agregar logs al historial
    saga.avanzar_paso(1, "TestEvento1", {"key": "value1"})
    saga.avanzar_paso(2, "TestEvento2", {"key": "value2"})
    
    mapeador = MapeadorSagaInstanceDTO()
    dto = mapeador.entidad_a_dto(saga)
    
    assert dto.id == str(saga_id)
    assert dto.id_reserva == str(reserva_id)
    assert dto.id_flujo == "RESERVA_ESTANDAR"
    assert dto.version_ejecucion == 1
    assert dto.estado_global == "EN_PROCESO"
    assert dto.paso_actual == 2
    assert dto.fecha_creacion == fecha_creacion
    # No verificar ultima_actualizacion porque se actualiza automáticamente
    assert len(dto.historial) == 2


def test_mapeador_instance_convierte_dto_a_entidad():
    """Verifica que dto_a_entidad convierte SagaInstanceDTO a SagaInstance."""
    saga_id = uuid.uuid4()
    reserva_id = uuid.uuid4()
    fecha_creacion = datetime.datetime(2026, 4, 1, 10, 0, 0)
    fecha_actualizacion = datetime.datetime(2026, 4, 1, 10, 5, 0)
    
    dto = SagaInstanceDTO(
        id=str(saga_id),
        id_reserva=str(reserva_id),
        id_flujo="RESERVA_ESTANDAR",
        version_ejecucion=1,
        estado_global="COMPLETADA",
        paso_actual=5,
        fecha_creacion=fecha_creacion,
        ultima_actualizacion=fecha_actualizacion,
    )
    
    # Agregar un log al DTO
    log_dto = SagaExecutionLogDTO(
        id=str(uuid.uuid4()),
        id_instancia=str(saga_id),
        tipo_mensaje="EVENTO_RECIBIDO",
        accion="TestEvento",
        payload_snapshot={"key": "value"},
        fecha_registro=fecha_creacion,
    )
    dto.historial.append(log_dto)
    
    mapeador = MapeadorSagaInstanceDTO()
    saga = mapeador.dto_a_entidad(dto)
    
    assert saga.id == saga_id
    assert saga.id_reserva == reserva_id
    assert saga.id_flujo == "RESERVA_ESTANDAR"
    assert saga.version_ejecucion == 1
    assert saga.estado_global == EstadoSaga.COMPLETADA
    assert saga.paso_actual == 5
    assert saga.fecha_creacion == fecha_creacion
    assert saga.ultima_actualizacion == fecha_actualizacion
    assert len(saga.historial) == 1
    assert saga.historial[0].accion == "TestEvento"


def test_mapeador_instance_ordena_historial_por_fecha():
    """Verifica que dto_a_entidad ordena el historial por fecha_registro."""
    saga_id = uuid.uuid4()
    reserva_id = uuid.uuid4()
    
    dto = SagaInstanceDTO(
        id=str(saga_id),
        id_reserva=str(reserva_id),
        id_flujo="RESERVA_ESTANDAR",
        version_ejecucion=1,
        estado_global="EN_PROCESO",
        paso_actual=2,
        fecha_creacion=datetime.datetime(2026, 4, 1, 10, 0, 0),
        ultima_actualizacion=datetime.datetime(2026, 4, 1, 10, 5, 0),
    )
    
    # Agregar logs en orden inverso
    log2 = SagaExecutionLogDTO(
        id=str(uuid.uuid4()),
        id_instancia=str(saga_id),
        tipo_mensaje="EVENTO_RECIBIDO",
        accion="Evento2",
        payload_snapshot={},
        fecha_registro=datetime.datetime(2026, 4, 1, 10, 2, 0),
    )
    log1 = SagaExecutionLogDTO(
        id=str(uuid.uuid4()),
        id_instancia=str(saga_id),
        tipo_mensaje="EVENTO_RECIBIDO",
        accion="Evento1",
        payload_snapshot={},
        fecha_registro=datetime.datetime(2026, 4, 1, 10, 1, 0),
    )
    dto.historial.extend([log2, log1])
    
    mapeador = MapeadorSagaInstanceDTO()
    saga = mapeador.dto_a_entidad(dto)
    
    # El historial debe estar ordenado por fecha
    assert len(saga.historial) == 2
    assert saga.historial[0].accion == "Evento1"
    assert saga.historial[1].accion == "Evento2"


def test_mapeador_instance_convierte_saga_sin_historial():
    """Verifica que el mapeador maneja correctamente sagas sin historial."""
    saga_id = uuid.uuid4()
    reserva_id = uuid.uuid4()
    
    saga = SagaInstance(id=saga_id, id_reserva=reserva_id)
    
    mapeador = MapeadorSagaInstanceDTO()
    dto = mapeador.entidad_a_dto(saga)
    
    assert len(dto.historial) == 0
    
    # Convertir de vuelta
    saga_recuperada = mapeador.dto_a_entidad(dto)
    assert len(saga_recuperada.historial) == 0


def test_mapeador_instance_maneja_todos_los_estados():
    """Verifica que el mapeador maneja correctamente todos los estados de saga."""
    estados = [
        EstadoSaga.EN_PROCESO,
        EstadoSaga.PAUSADA_ESPERANDO_HOTEL,
        EstadoSaga.COMPLETADA,
        EstadoSaga.COMPENSANDO,
        EstadoSaga.COMPENSACION_EXITOSA,
        EstadoSaga.COMPENSACION_FALLIDA,
    ]
    
    mapeador = MapeadorSagaInstanceDTO()
    
    for estado in estados:
        saga = SagaInstance(id=uuid.uuid4(), id_reserva=uuid.uuid4())
        saga.estado_global = estado
        
        dto = mapeador.entidad_a_dto(saga)
        assert dto.estado_global == estado.value
        
        saga_recuperada = mapeador.dto_a_entidad(dto)
        assert saga_recuperada.estado_global == estado
