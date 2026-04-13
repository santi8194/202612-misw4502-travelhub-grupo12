import datetime
import uuid

from modulos.reserva.dominio.eventos import (
    FallaActualizacionLocalEvt,
    ReservaCancelada,
    ReservaConfirmada,
    ReservaConfirmadaEvt,
    ReservaIniciada,
    ReservaPendiente,
)
from seedwork.dominio.eventos import EventoDominio


def test_eventos_de_reserva_heredan_de_evento_dominio_y_guardan_payload():
    id_reserva = uuid.uuid4()
    id_usuario = uuid.uuid4()
    id_categoria = uuid.uuid4()

    iniciado = ReservaIniciada(
        id_reserva=id_reserva,
        id_usuario=id_usuario,
        id_categoria=id_categoria,
        fecha_creacion=datetime.datetime(2026, 4, 1, 10, 0, 0),
    )
    pendiente = ReservaPendiente(id_reserva=id_reserva, id_usuario=id_usuario, id_categoria=id_categoria)
    confirmada = ReservaConfirmada(id_reserva=id_reserva, fecha_actualizacion=datetime.datetime.now())
    cancelada = ReservaCancelada(id_reserva=id_reserva, fecha_actualizacion=datetime.datetime.now())

    assert isinstance(iniciado, EventoDominio)
    assert isinstance(pendiente, EventoDominio)
    assert isinstance(confirmada, EventoDominio)
    assert isinstance(cancelada, EventoDominio)
    assert iniciado.id_reserva == id_reserva
    assert iniciado.id_usuario == id_usuario
    assert pendiente.id_categoria == id_categoria


def test_eventos_locales_guardan_id_y_fecha():
    id_reserva = uuid.uuid4()
    ts = datetime.datetime(2026, 4, 2, 9, 30, 0)

    evt_ok = ReservaConfirmadaEvt(id_reserva=id_reserva, fecha_actualizacion=ts)
    evt_fail = FallaActualizacionLocalEvt(id_reserva=id_reserva, fecha_actualizacion=ts)

    assert isinstance(evt_ok, EventoDominio)
    assert isinstance(evt_fail, EventoDominio)
    assert evt_ok.id_reserva == id_reserva
    assert evt_fail.id_reserva == id_reserva
    assert evt_ok.fecha_actualizacion == ts
    assert evt_fail.fecha_actualizacion == ts
