import datetime
import uuid
from unittest.mock import MagicMock

import pytest

from modulos.reserva.aplicacion.comandos import (
	CancelarReservaLocalCmd,
	ConfirmarReservaLocalCmd,
	CrearReservaHold,
	FormalizarReserva,
)
from modulos.reserva.aplicacion.handlers import (
	CancelarReservaLocalHandler,
	ConfirmarReservaLocalHandler,
	CrearReservaHoldHandler,
	FormalizarReservaHandler,
)
from modulos.reserva.dominio.entidades import Reserva, Usuario
from modulos.reserva.dominio.eventos import FallaActualizacionLocalEvt, ReservaConfirmadaEvt
from modulos.reserva.dominio.objetos_valor import EstadoReserva, Pax


def _uow_mock():
	uow = MagicMock()
	uow.__enter__ = MagicMock(return_value=uow)
	uow.__exit__ = MagicMock(return_value=None)
	return uow


def _reserva_en_hold() -> Reserva:
	reserva = Reserva(id=str(uuid.uuid4()))
	reserva.crear_reserva(
		id_categoria=uuid.uuid4(),
		fecha_check_in=datetime.date(2026, 4, 10),
		fecha_check_out=datetime.date(2026, 4, 11),
		ocupacion=Pax(adultos=2, ninos=0, infantes=0),
		usuario=Usuario(id=str(uuid.uuid4()), nombre="Ana", email="ana@test.com"),
	)
	return reserva


def test_crear_reserva_hold_handler_ok_persiste_y_commit():
	repositorio = MagicMock()
	uow = _uow_mock()
	handler = CrearReservaHoldHandler(repositorio=repositorio, uow=uow)

	comando = CrearReservaHold(
		id_usuario=uuid.uuid4(),
		id_categoria=uuid.uuid4(),
		fecha_check_in="2026-04-01",
		fecha_check_out="2026-04-03",
		ocupacion={"adultos": 2, "ninos": 1, "infantes": 0},
		usuario_nombre="Carlos",
		usuario_email="carlos@test.com",
	)

	id_reserva = handler.handle(comando)

	assert id_reserva is not None
	repositorio.agregar.assert_called_once()
	uow.agregar_eventos.assert_called_once()
	uow.commit.assert_called_once()


def test_crear_reserva_hold_handler_con_estado_explicito():
	repositorio = MagicMock()
	uow = _uow_mock()
	handler = CrearReservaHoldHandler(repositorio=repositorio, uow=uow)

	comando = CrearReservaHold(
		id_usuario=uuid.uuid4(),
		id_categoria=uuid.uuid4(),
		estado="HOLD",
		fecha_check_in="2026-04-01",
		fecha_check_out="2026-04-03",
	)

	handler.handle(comando)

	reserva_guardada = repositorio.agregar.call_args[0][0]
	assert reserva_guardada.estado == EstadoReserva.HOLD


def test_formalizar_handler_ok_actualiza_y_commit():
	repositorio = MagicMock()
	uow = _uow_mock()
	reserva = _reserva_en_hold()
	repositorio.obtener_por_id.return_value = reserva
	handler = FormalizarReservaHandler(repositorio=repositorio, uow=uow)

	ok = handler.handle(FormalizarReserva(id_reserva=uuid.UUID(reserva.id)))

	assert ok is True
	repositorio.actualizar.assert_called_once_with(reserva)
	uow.agregar_eventos.assert_called_once()
	uow.commit.assert_called_once()


def test_formalizar_handler_no_encontrada_lanza_error():
	repositorio = MagicMock()
	uow = _uow_mock()
	repositorio.obtener_por_id.return_value = None
	handler = FormalizarReservaHandler(repositorio=repositorio, uow=uow)

	with pytest.raises(ValueError, match="No se encontró la reserva"):
		handler.handle(FormalizarReserva(id_reserva=uuid.uuid4()))


def test_confirmar_handler_ok_emite_evento_local():
	repositorio = MagicMock()
	uow = _uow_mock()
	reserva = _reserva_en_hold()
	reserva.formalizar_y_pagar()
	repositorio.obtener_por_id.return_value = reserva
	handler = ConfirmarReservaLocalHandler(repositorio=repositorio, uow=uow)

	evento = handler.handle(ConfirmarReservaLocalCmd(id_reserva=uuid.UUID(reserva.id)))

	assert isinstance(evento, ReservaConfirmadaEvt)
	repositorio.actualizar.assert_called_once_with(reserva)
	uow.commit.assert_called_once()


def test_confirmar_handler_no_encontrada_lanza_error():
	repositorio = MagicMock()
	uow = _uow_mock()
	repositorio.obtener_por_id.return_value = None
	handler = ConfirmarReservaLocalHandler(repositorio=repositorio, uow=uow)

	with pytest.raises(ValueError, match="No se encontró la reserva"):
		handler.handle(ConfirmarReservaLocalCmd(id_reserva=uuid.uuid4()))


def test_cancelar_handler_ok_emite_evento_falla_local():
	repositorio = MagicMock()
	uow = _uow_mock()
	reserva = _reserva_en_hold()
	repositorio.obtener_por_id.return_value = reserva
	handler = CancelarReservaLocalHandler(repositorio=repositorio, uow=uow)

	evento = handler.handle(CancelarReservaLocalCmd(id_reserva=uuid.UUID(reserva.id)))

	assert isinstance(evento, FallaActualizacionLocalEvt)
	repositorio.actualizar.assert_called_once_with(reserva)
	uow.commit.assert_called_once()


def test_cancelar_handler_no_encontrada_lanza_error():
	repositorio = MagicMock()
	uow = _uow_mock()
	repositorio.obtener_por_id.return_value = None
	handler = CancelarReservaLocalHandler(repositorio=repositorio, uow=uow)

	with pytest.raises(ValueError, match="No se encontró la reserva"):
		handler.handle(CancelarReservaLocalCmd(id_reserva=uuid.uuid4()))
