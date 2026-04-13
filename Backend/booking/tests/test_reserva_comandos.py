import uuid

from modulos.reserva.aplicacion.comandos import (
    CancelarReservaLocalCmd,
    ConfirmarReservaLocalCmd,
    CrearReservaHold,
    FormalizarReserva,
)


def test_crear_reserva_hold_comando_guarda_todos_los_campos():
    id_usuario = uuid.uuid4()
    id_categoria = uuid.uuid4()

    cmd = CrearReservaHold(
        id_usuario=id_usuario,
        id_categoria=id_categoria,
        codigo_confirmacion_ota="OTA-001",
        codigo_localizador_pms="PMS-001",
        estado="HOLD",
        fecha_check_in="2026-04-01",
        fecha_check_out="2026-04-05",
        ocupacion={"adultos": 2, "ninos": 1, "infantes": 0},
        usuario_nombre="Ana",
        usuario_email="ana@test.com",
    )

    assert cmd.id_usuario == id_usuario
    assert cmd.id_categoria == id_categoria
    assert cmd.codigo_confirmacion_ota == "OTA-001"
    assert cmd.codigo_localizador_pms == "PMS-001"
    assert cmd.estado == "HOLD"
    assert cmd.fecha_check_in == "2026-04-01"
    assert cmd.fecha_check_out == "2026-04-05"
    assert cmd.ocupacion["adultos"] == 2
    assert cmd.usuario_nombre == "Ana"
    assert cmd.usuario_email == "ana@test.com"


def test_formalizar_confirmar_y_cancelar_comandos_guardan_id_reserva():
    id_reserva = uuid.uuid4()

    formalizar = FormalizarReserva(id_reserva=id_reserva)
    confirmar = ConfirmarReservaLocalCmd(id_reserva=id_reserva)
    cancelar = CancelarReservaLocalCmd(id_reserva=id_reserva)

    assert formalizar.id_reserva == id_reserva
    assert confirmar.id_reserva == id_reserva
    assert cancelar.id_reserva == id_reserva
