from fastapi.testclient import TestClient

from api import router as router_module
from config.app import create_app
from modules.pms.application.commands.cancel_reservation import CancelReservation
from modules.pms.application.commands.confirm_reservation import ConfirmReservation


class _Bus:
    def __init__(self):
        self.events = []

    def publish_event(self, routing_key, event_type, payload):
        self.events.append((routing_key, event_type, payload))


class _Repo:
    def __init__(self, existing=None, active=None, save_error=None):
        self.existing = existing
        self.active = active
        self.save_error = save_error
        self.saved = []
        self.updated = []

    def obtain_by_reservation_id(self, reservation_id):
        return self.existing

    def obtain_active_by_category_and_range(self, id_categoria, fecha_check_in, fecha_check_out):
        return self.active

    def save(self, reservation):
        if self.save_error:
            raise self.save_error
        self.saved.append(reservation)

    def update(self, reservation):
        self.updated.append(reservation)


class _Reservation:
    def __init__(self, reservation_id="r-1", id_categoria="cat-1", state="CONFIRMED"):
        self.id = "pms-1"
        self.reservation_id = reservation_id
        self.id_categoria = id_categoria
        self.id_usuario = "user-1"
        self.hotel_code = "HOT-001"
        self.room_type_code = "RM001"
        self.hotel_id = "Hotel Test"
        self.fecha_check_in = "2026-11-01"
        self.fecha_check_out = "2026-11-02"
        self.state = state
        self.version = 1


def _client() -> TestClient:
    return TestClient(create_app())


def test_confirm_reservation_returns_existing_message(monkeypatch):
    repo = _Repo(existing=_Reservation(reservation_id="res-1"))
    bus = _Bus()

    monkeypatch.setattr(
        "modules.pms.application.commands.confirm_reservation.ConfirmReservation._resolve_category",
        lambda self, _: {"hotel_code": "HOT-001", "hotel_id": "Hotel Test", "room_type_code": "RM001"},
    )

    result = ConfirmReservation(repo, bus).execute("res-1", "cat-1", "usr-1", "2026-11-01", "2026-11-02")

    assert result["message"] == "Reservation already processed"
    assert bus.events == []


def test_confirm_reservation_blocks_active_booking_and_publishes_failure(monkeypatch):
    repo = _Repo(active=_Reservation(state="CONFIRMED"))
    bus = _Bus()

    monkeypatch.setattr(
        "modules.pms.application.commands.confirm_reservation.ConfirmReservation._resolve_category",
        lambda self, _: {"hotel_code": "HOT-001", "hotel_id": "Hotel Test", "room_type_code": "RM001"},
    )

    result = ConfirmReservation(repo, bus).execute("res-2", "cat-9", "usr-2", "2026-11-01", "2026-11-03")

    assert result["message"] == "Category is already actively booked for this date range"
    assert result["state"] == "CONFIRMED"
    assert bus.events[0][1] == "ReservaRechazadaPmsEvt"


def test_confirm_reservation_success(monkeypatch):
    created = _Reservation(reservation_id="res-3", id_categoria="cat-3", state="CONFIRMED")
    repo = _Repo()
    bus = _Bus()

    monkeypatch.setattr(
        "modules.pms.application.commands.confirm_reservation.ConfirmReservation._resolve_category",
        lambda self, _: {"hotel_code": "HOT-001", "hotel_id": "Hotel Test", "room_type_code": "RM001"},
    )
    monkeypatch.setattr(
        "modules.pms.application.commands.confirm_reservation.Reservation.create",
        lambda *args, **kwargs: created,
    )

    result = ConfirmReservation(repo, bus).execute("res-3", "cat-3", "usr-3", "2026-11-05", "2026-11-07")

    assert result["id_reserva"] == "res-3"
    assert result["fecha_check_in"] == "2026-11-05"
    assert result["fecha_check_out"] == "2026-11-07"
    assert result["id_categoria"] == "cat-3"
    assert result["id_usuario"] == "usr-3"
    assert len(repo.saved) == 1
    assert bus.events[0][1] == "ConfirmacionPmsExitosaEvt"


def test_confirm_reservation_fails_when_id_usuario_is_missing(monkeypatch):
    repo = _Repo()
    bus = _Bus()

    monkeypatch.setattr(
        "modules.pms.application.commands.confirm_reservation.ConfirmReservation._resolve_category",
        lambda self, _: {"hotel_code": "HOT-001", "hotel_id": "Hotel Test", "room_type_code": "RM001"},
    )

    try:
        ConfirmReservation(repo, bus).execute("res-4", "cat-4", None, "2026-11-06", "2026-11-07")
    except ValueError as exc:
        assert "id_usuario" in str(exc)
    else:
        assert False, "Se esperaba ValueError por id_usuario faltante"


def test_confirm_reservation_fails_when_check_out_is_not_after_check_in(monkeypatch):
    repo = _Repo()
    bus = _Bus()

    monkeypatch.setattr(
        "modules.pms.application.commands.confirm_reservation.ConfirmReservation._resolve_category",
        lambda self, _: {"hotel_code": "HOT-001", "hotel_id": "Hotel Test", "room_type_code": "RM001"},
    )

    try:
        ConfirmReservation(repo, bus).execute("res-5", "cat-5", "usr-5", "2026-11-10", "2026-11-10")
    except ValueError as exc:
        assert "fecha_check_out" in str(exc)
    else:
        assert False, "Se esperaba ValueError por rango de fechas invalido"


def test_confirm_reservation_handles_unexpected_error_and_publishes_failure(monkeypatch):
    repo = _Repo(save_error=RuntimeError("db down"))
    bus = _Bus()

    monkeypatch.setattr(
        "modules.pms.application.commands.confirm_reservation.ConfirmReservation._resolve_category",
        lambda self, _: {"hotel_code": "HOT-001", "hotel_id": "Hotel Test", "room_type_code": "RM001"},
    )
    monkeypatch.setattr(
        "modules.pms.application.commands.confirm_reservation.Reservation.create",
        lambda *args, **kwargs: _Reservation(reservation_id="res-6", id_categoria="cat-6"),
    )

    result = ConfirmReservation(repo, bus).execute("res-6", "cat-6", "usr-6", "2026-11-06", "2026-11-08")

    assert result["event_generated"] == "ReservaRechazadaPmsEvt"
    assert result["motivo"] == "db down"
    assert bus.events[0][1] == "ReservaRechazadaPmsEvt"


def test_cancel_reservation_not_found():
    repo = _Repo(existing=None)
    bus = _Bus()

    result = CancelReservation(repo, bus).execute("missing")

    assert result == {"message": "Reservation not found"}


def test_cancel_reservation_already_cancelled():
    repo = _Repo(existing=_Reservation(state="CANCELLED"))
    bus = _Bus()

    result = CancelReservation(repo, bus).execute("res-7")

    assert result == {"message": "Reservation is already cancelled"}


def test_cancel_reservation_success_updates_and_publishes():
    reservation = _Reservation(reservation_id="res-8", id_categoria="cat-8", state="CONFIRMED")
    repo = _Repo(existing=reservation)
    bus = _Bus()

    result = CancelReservation(repo, bus).execute("res-8")

    assert result["state"] == "CANCELLED"
    assert result["event_generated"] == "ConfirmacionPmsCanceladaEvt"
    assert len(repo.updated) == 1
    assert bus.events[0][1] == "ConfirmacionPmsCanceladaEvt"


def test_router_health_endpoint():
    response = _client().get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "pms-integration"}


def test_router_cancelar_reserva_delegates_command(monkeypatch):
    class FakeCancelReservation:
        def __init__(self, repository, event_bus):
            pass

        def execute(self, reservation_id):
            return {"reservation_id": reservation_id, "state": "CANCELLED"}

    monkeypatch.setattr(router_module, "CancelReservation", FakeCancelReservation)

    response = _client().post("/api/cancelar-reserva", json={"id_reserva": "res-10"})

    assert response.status_code == 200
    assert response.json() == {"reservation_id": "res-10", "state": "CANCELLED"}


def test_router_confirmar_reserva_delegates_command(monkeypatch):
    class FakeConfirmReservation:
        def __init__(self, repository, event_bus):
            pass

        def execute(self, id_reserva, id_categoria, id_usuario, fecha_check_in, fecha_check_out):
            return {
                "id_reserva": id_reserva,
                "id_categoria": id_categoria,
                "id_usuario": id_usuario,
                "fecha_check_in": fecha_check_in,
                "fecha_check_out": fecha_check_out,
                "event_generated": "ConfirmacionPmsExitosaEvt",
            }

    monkeypatch.setattr(router_module, "ConfirmReservation", FakeConfirmReservation)

    response = _client().post(
        "/api/confirmar-reserva",
        json={
            "id_reserva": "res-11",
            "id_categoria": "cat-11",
            "id_usuario": "usr-11",
            "fecha_check_in": "2026-12-01",
            "fecha_check_out": "2026-12-03",
        },
    )

    assert response.status_code == 200
    assert response.json()["event_generated"] == "ConfirmacionPmsExitosaEvt"
