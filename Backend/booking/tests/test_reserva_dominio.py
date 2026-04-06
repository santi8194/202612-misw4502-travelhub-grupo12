import datetime
import uuid

import pytest

from modulos.reserva.dominio.entidades import Notificacion, Pago, Reserva, Resena, Usuario
from modulos.reserva.dominio.eventos import (
	ReservaCancelada,
	ReservaConfirmada,
	ReservaIniciada,
	ReservaPendiente,
)
from modulos.reserva.dominio.objetos_valor import EstadoReserva, Pax


def crear_reserva_en_hold() -> Reserva:
	reserva = Reserva(id=str(uuid.uuid4()))
	reserva.crear_reserva(
		id_categoria=uuid.uuid4(),
		fecha_check_in=datetime.date(2026, 4, 10),
		fecha_check_out=datetime.date(2026, 4, 12),
		ocupacion=Pax(adultos=2, ninos=1, infantes=0),
		usuario=Usuario(id=str(uuid.uuid4()), nombre="Ana", email="ana@test.com"),
	)
	return reserva


def test_crear_reserva_hold_emite_evento_iniciado():
	reserva = crear_reserva_en_hold()

	assert reserva.estado == EstadoReserva.HOLD
	assert len(reserva.eventos) == 1
	assert isinstance(reserva.eventos[0], ReservaIniciada)
	assert reserva.id_categoria is not None


def test_formalizar_desde_hold_pasa_a_pendiente_y_emite_evento():
	reserva = crear_reserva_en_hold()

	reserva.formalizar_y_pagar()

	assert reserva.estado == EstadoReserva.PENDIENTE
	assert isinstance(reserva.eventos[-1], ReservaPendiente)


def test_formalizar_con_hold_expirada_cancela_y_falla():
	reserva = crear_reserva_en_hold()
	reserva.fecha_creacion = datetime.datetime.now() - datetime.timedelta(minutes=16)

	with pytest.raises(ValueError, match="ha expirado"):
		reserva.formalizar_y_pagar()

	assert reserva.estado == EstadoReserva.EXPIRADA
	assert isinstance(reserva.eventos[-1], ReservaCancelada)


def test_formalizar_sin_hold_lanza_error():
	reserva = crear_reserva_en_hold()
	reserva.estado = EstadoReserva.CANCELADA

	with pytest.raises(ValueError, match="HOLD"):
		reserva.formalizar_y_pagar()


def test_confirmar_desde_pendiente_cambia_a_confirmada():
	reserva = crear_reserva_en_hold()
	reserva.formalizar_y_pagar()

	reserva.confirmar_reserva()

	assert reserva.estado == EstadoReserva.CONFIRMADA
	assert isinstance(reserva.eventos[-1], ReservaConfirmada)


def test_confirmar_fuera_de_pendiente_lanza_error():
	reserva = crear_reserva_en_hold()

	with pytest.raises(ValueError, match="PENDIENTE"):
		reserva.confirmar_reserva()


def test_cancelar_reserva_cambia_estado_y_emite_evento():
	reserva = crear_reserva_en_hold()

	reserva.cancelar_reserva()

	assert reserva.estado == EstadoReserva.CANCELADA
	assert isinstance(reserva.eventos[-1], ReservaCancelada)


def test_helpers_de_agregacion_y_actualizacion_estado():
	reserva = Reserva(id=str(uuid.uuid4()))
	usuario = Usuario(id=str(uuid.uuid4()), nombre="Juan", email="juan@test.com")
	pago = Pago(id=str(uuid.uuid4()), estado_pago="OK")
	notificacion = Notificacion(id=str(uuid.uuid4()), tipo="email", mensaje="ok")
	resena = Resena(id=str(uuid.uuid4()), id_usuario=uuid.uuid4(), calificacion=5)

	reserva.asignar_usuario(usuario)
	reserva.agregar_pago(pago)
	reserva.agregar_notificacion(notificacion)
	reserva.agregar_resena(resena)
	reserva.actualizar_estado(EstadoReserva.PENDIENTE)

	assert reserva.usuario == usuario
	assert reserva.pagos == [pago]
	assert reserva.notificaciones == [notificacion]
	assert reserva.resenas == [resena]
	assert reserva.estado == EstadoReserva.PENDIENTE
