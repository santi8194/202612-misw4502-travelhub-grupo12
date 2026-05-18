"""
Pruebas unitarias para mapeadores de eventos de reserva y schema de integración.
"""
import uuid
import datetime

from modulos.reserva.dominio.eventos import ReservaPendiente, ReservaConfirmadaEvt, ReservaCanceladaEvt
from modulos.reserva.infraestructura.mapeadores import MapeadorEventosReserva
from modulos.reserva.infraestructura.schema.v1.eventos import (
    EventoReservaCreada,
    ReservaCreadaPayload,
    EventoReservaConfirmada,
    ReservaConfirmadaPayload,
    EventoReservaCancelada,
    ReservaCanceladaPayload,
)


# --- Pruebas de MapeadorEventosReserva ---

def test_mapeador_convierte_reserva_pendiente_a_evento_integracion():
    """Verifica que ReservaPendiente se mapea a EventoReservaCreada."""
    id_reserva = uuid.uuid4()
    id_usuario = uuid.uuid4()
    id_categoria = uuid.uuid4()
    
    evento_dominio = ReservaPendiente(
        id_reserva=id_reserva,
        id_usuario=id_usuario,
        id_categoria=id_categoria,
    )
    
    mapeador = MapeadorEventosReserva()
    evento_integracion = mapeador.entidad_a_dto(evento_dominio)
    
    assert isinstance(evento_integracion, EventoReservaCreada)
    assert evento_integracion.type == "ReservaCreadaIntegracionEvt"
    assert evento_integracion.specversion == "v1"
    assert evento_integracion.data.id_reserva == str(id_reserva)
    assert evento_integracion.data.id_usuario == str(id_usuario)
    assert evento_integracion.data.id_categoria == str(id_categoria)


def test_mapeador_convierte_reserva_confirmada_evt_a_evento_integracion():
    """Verifica que ReservaConfirmadaEvt se mapea a EventoReservaConfirmada."""
    id_reserva = uuid.uuid4()
    id_cliente = uuid.uuid4()
    fecha_actualizacion = datetime.datetime(2026, 4, 1, 10, 30, 0)
    
    evento_dominio = ReservaConfirmadaEvt(
        id_reserva=id_reserva,
        id_cliente=id_cliente,
        email_cliente="test@example.com",
        fecha_actualizacion=fecha_actualizacion,
        emailCliente="cliente@test.com",
        codigo_reserva="TH-RES-100",
        categoria="cat-1",
        fecha_check_in="2026-04-10",
        fecha_check_out="2026-04-12",
        huespedes=3,
        moneda="COP",
    )
    
    mapeador = MapeadorEventosReserva()
    evento_integracion = mapeador.entidad_a_dto(evento_dominio)
    
    assert isinstance(evento_integracion, EventoReservaConfirmada)
    assert evento_integracion.type == "ReservaConfirmadaEvt"
    assert evento_integracion.specversion == "v1"
    assert evento_integracion.data.id_reserva == str(id_reserva)
    assert evento_integracion.data.emailCliente == "cliente@test.com"
    assert evento_integracion.data.codigo_reserva == "TH-RES-100"
    assert evento_integracion.data.categoria == "cat-1"
    assert evento_integracion.data.fecha_check_in == "2026-04-10"
    assert evento_integracion.data.fecha_check_out == "2026-04-12"
    assert evento_integracion.data.huespedes == 3
    assert evento_integracion.data.moneda == "COP"


def test_mapeador_convierte_reserva_cancelada_evt_a_evento_integracion():
    """Verifica que ReservaCanceladaEvt se mapea a EventoReservaCancelada."""
    id_reserva = uuid.uuid4()
    fecha_actualizacion = datetime.datetime(2026, 4, 1, 10, 35, 0)

    evento_dominio = ReservaCanceladaEvt(
        id_reserva=id_reserva,
        fecha_actualizacion=fecha_actualizacion,
        emailCliente="cliente@test.com",
        codigo_reserva="TH-RES-200",
        categoria="cat-2",
        fecha_check_in="2026-05-01",
        fecha_check_out="2026-05-03",
        huespedes=2,
        moneda="COP",
        motivo_cancelacion="Rechazo manual",
    )

    mapeador = MapeadorEventosReserva()
    evento_integracion = mapeador.entidad_a_dto(evento_dominio)

    assert isinstance(evento_integracion, EventoReservaCancelada)
    assert evento_integracion.type == "ReservaCanceladaEvt"
    assert evento_integracion.specversion == "v1"
    assert evento_integracion.data.id_reserva == str(id_reserva)
    assert evento_integracion.data.emailCliente == "cliente@test.com"
    assert evento_integracion.data.codigo_reserva == "TH-RES-200"
    assert evento_integracion.data.categoria == "cat-2"
    assert evento_integracion.data.fecha_check_in == "2026-05-01"
    assert evento_integracion.data.fecha_check_out == "2026-05-03"
    assert evento_integracion.data.huespedes == 2
    assert evento_integracion.data.moneda == "COP"
    assert evento_integracion.data.motivo_cancelacion == "Rechazo manual"


def test_mapeador_retorna_none_para_eventos_no_mapeados():
    """Verifica que eventos sin mapeo retornan None."""
    from modulos.reserva.dominio.eventos import ReservaIniciada
    
    evento_no_mapeado = ReservaIniciada(
        id_reserva=uuid.uuid4(),
        id_usuario=uuid.uuid4(),
        id_categoria=uuid.uuid4(),
        fecha_creacion=datetime.datetime.now(),
    )
    
    mapeador = MapeadorEventosReserva()
    resultado = mapeador.entidad_a_dto(evento_no_mapeado)
    
    assert resultado is None


def test_mapeador_obtener_tipo_retorna_clase_correcta():
    """Verifica que obtener_tipo retorna la clase base EventoDominio."""
    from seedwork.dominio.eventos import EventoDominio
    
    mapeador = MapeadorEventosReserva()
    tipo = mapeador.obtener_tipo()
    
    assert tipo == EventoDominio.__class__


def test_mapeador_router_contiene_reserva_pendiente():
    """Verifica que router contiene ReservaPendiente."""
    from modulos.reserva.dominio.eventos import ReservaPendiente
    
    mapeador = MapeadorEventosReserva()
    
    assert ReservaPendiente in mapeador.router


def test_mapeador_router_contiene_reserva_confirmada():
    """Verifica que router contiene ReservaConfirmadaEvt."""
    from modulos.reserva.dominio.eventos import ReservaConfirmadaEvt
    
    mapeador = MapeadorEventosReserva()
    
    assert ReservaConfirmadaEvt in mapeador.router


def test_mapeador_router_contiene_reserva_cancelada():
    """Verifica que router contiene ReservaCanceladaEvt."""
    from modulos.reserva.dominio.eventos import ReservaCanceladaEvt

    mapeador = MapeadorEventosReserva()

    assert ReservaCanceladaEvt in mapeador.router


def test_mapeador_es_version_valida():
    """Verifica que es_version_valida funciona correctamente."""
    mapeador = MapeadorEventosReserva()
    
    assert mapeador.es_version_valida("v1") is True
    assert mapeador.es_version_valida("v2") is False


# --- Pruebas de Schema v1: ReservaCreadaPayload ---

def test_reserva_creada_payload_guarda_todos_los_campos():
    """Verifica que ReservaCreadaPayload almacena correctamente todos los campos."""
    id_reserva = str(uuid.uuid4())
    id_usuario = str(uuid.uuid4())
    id_categoria = str(uuid.uuid4())
    
    payload = ReservaCreadaPayload(
        id_reserva=id_reserva,
        id_usuario=id_usuario,
        id_categoria=id_categoria,
        estado="PENDIENTE",
        fecha_creacion="2026-04-01T10:00:00",
    )
    
    assert payload.id_reserva == id_reserva
    assert payload.id_usuario == id_usuario
    assert payload.id_categoria == id_categoria
    assert payload.estado == "PENDIENTE"
    assert payload.fecha_creacion == "2026-04-01T10:00:00"


def test_reserva_creada_payload_to_dict_serializa_correctamente():
    """Verifica que to_dict serializa ReservaCreadaPayload correctamente."""
    id_reserva = str(uuid.uuid4())
    id_usuario = str(uuid.uuid4())
    id_categoria = str(uuid.uuid4())
    
    payload = ReservaCreadaPayload(
        id_reserva=id_reserva,
        id_usuario=id_usuario,
        id_categoria=id_categoria,
        estado="PENDIENTE",
        fecha_creacion="2026-04-01T10:00:00",
    )
    
    resultado = payload.to_dict()
    
    assert resultado["id_reserva"] == id_reserva
    assert resultado["id_usuario"] == id_usuario
    assert resultado["id_categoria"] == id_categoria
    assert resultado["estado"] == "PENDIENTE"
    assert resultado["fecha_creacion"] == "2026-04-01T10:00:00"


# --- Pruebas de Schema v1: EventoReservaCreada ---

def test_evento_reserva_creada_guarda_todos_los_campos():
    """Verifica que EventoReservaCreada almacena correctamente todos los campos."""
    id_reserva = str(uuid.uuid4())
    id_usuario = str(uuid.uuid4())
    id_categoria = str(uuid.uuid4())
    
    payload = ReservaCreadaPayload(
        id_reserva=id_reserva,
        id_usuario=id_usuario,
        id_categoria=id_categoria,
        estado="PENDIENTE",
        fecha_creacion="2026-04-01T10:00:00",
    )
    
    evento = EventoReservaCreada(
        id=str(uuid.uuid4()),
        type="ReservaCreadaIntegracionEvt",
        datacontenttype="application/json",
        service_name="booking",
        data=payload,
    )
    
    assert evento.type == "ReservaCreadaIntegracionEvt"
    assert evento.specversion == "v1"
    assert evento.datacontenttype == "application/json"
    assert evento.service_name == "booking"
    assert evento.data == payload


def test_evento_reserva_creada_to_dict_serializa_correctamente():
    """Verifica que to_dict serializa EventoReservaCreada correctamente."""
    id_reserva = str(uuid.uuid4())
    id_usuario = str(uuid.uuid4())
    id_categoria = str(uuid.uuid4())
    
    payload = ReservaCreadaPayload(
        id_reserva=id_reserva,
        id_usuario=id_usuario,
        id_categoria=id_categoria,
        estado="PENDIENTE",
        fecha_creacion="2026-04-01T10:00:00",
    )
    
    evento = EventoReservaCreada(
        id=str(uuid.uuid4()),
        type="ReservaCreadaIntegracionEvt",
        datacontenttype="application/json",
        service_name="booking",
        data=payload,
    )
    
    resultado = evento.to_dict()
    
    assert resultado["type"] == "ReservaCreadaIntegracionEvt"
    assert resultado["specversion"] == "v1"
    assert resultado["datacontenttype"] == "application/json"
    assert resultado["service_name"] == "booking"
    assert "id" in resultado
    assert "time" in resultado
    assert resultado["data"]["id_reserva"] == id_reserva


# --- Pruebas de Schema v1: ReservaConfirmadaPayload ---

def test_reserva_confirmada_payload_guarda_todos_los_campos():
    """Verifica que ReservaConfirmadaPayload almacena correctamente todos los campos."""
    id_reserva = str(uuid.uuid4())
    id_cliente = str(uuid.uuid4())
    email_cliente = "cliente@test.com"
    
    payload = ReservaConfirmadaPayload(
        id_reserva=id_reserva,
        id_cliente=id_cliente,
        emailCliente=email_cliente,
    )
    
    assert payload.id_reserva == id_reserva
    assert payload.id_cliente == id_cliente
    assert payload.emailCliente == email_cliente


def test_reserva_confirmada_payload_to_dict_serializa_correctamente():
    """Verifica que to_dict serializa ReservaConfirmadaPayload correctamente."""
    id_reserva = str(uuid.uuid4())
    id_cliente = str(uuid.uuid4())
    email_cliente = "cliente@test.com"
    
    payload = ReservaConfirmadaPayload(
        id_reserva=id_reserva,
        id_cliente=id_cliente,
        emailCliente=email_cliente,
    )
    
    resultado = payload.to_dict()
    
    assert resultado["id_reserva"] == id_reserva
    assert resultado["id_cliente"] == id_cliente
    assert resultado["emailCliente"] == email_cliente


# --- Pruebas de Schema v1: EventoReservaConfirmada ---

def test_evento_reserva_confirmada_guarda_todos_los_campos():
    """Verifica que EventoReservaConfirmada almacena correctamente todos los campos."""
    id_reserva = str(uuid.uuid4())
    id_cliente = str(uuid.uuid4())
    email_cliente = "cliente@test.com"
    
    payload = ReservaConfirmadaPayload(
        id_reserva=id_reserva,
        id_cliente=id_cliente,
        emailCliente=email_cliente,
    )
    
    evento = EventoReservaConfirmada(
        id=str(uuid.uuid4()),
        type="ReservaConfirmadaEvt",
        datacontenttype="application/json",
        service_name="booking",
        data=payload,
    )
    
    assert evento.type == "ReservaConfirmadaEvt"
    assert evento.specversion == "v1"
    assert evento.datacontenttype == "application/json"
    assert evento.service_name == "booking"
    assert evento.data == payload


def test_evento_reserva_confirmada_to_dict_serializa_correctamente():
    """Verifica que to_dict serializa EventoReservaConfirmada correctamente."""
    id_reserva = str(uuid.uuid4())
    id_cliente = str(uuid.uuid4())
    email_cliente = "cliente@test.com"
    
    payload = ReservaConfirmadaPayload(
        id_reserva=id_reserva,
        id_cliente=id_cliente,
        emailCliente=email_cliente,
    )
    
    evento = EventoReservaConfirmada(
        id=str(uuid.uuid4()),
        type="ReservaConfirmadaEvt",
        datacontenttype="application/json",
        service_name="booking",
        data=payload,
    )
    
    resultado = evento.to_dict()
    
    assert resultado["type"] == "ReservaConfirmadaEvt"
    assert resultado["specversion"] == "v1"
    assert resultado["datacontenttype"] == "application/json"
    assert resultado["service_name"] == "booking"
    assert "id" in resultado
    assert "time" in resultado
    assert resultado["data"]["id_reserva"] == id_reserva
    assert resultado["data"]["id_cliente"] == id_cliente
    assert resultado["data"]["emailCliente"] == email_cliente
