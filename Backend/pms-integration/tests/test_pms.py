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
    def __init__(self, existing=None, active=None, to_save=None, save_error=None):
        self.existing = existing
        self.active = active
        self.to_save = to_save
        self.save_error = save_error
        self.saved = []
        self.updated = []

    def obtain_by_reservation_id(self, reservation_id):
        if self.to_save is not None and getattr(self.to_save, "reservation_id", None) == reservation_id:
            return self.to_save
        return self.existing

    def obtain_active_by_room_and_date(self, room_id, fecha_reserva):
        return self.active

    def save(self, reservation):
        if self.save_error:
            raise self.save_error
        self.saved.append(reservation)

    def update(self, reservation):
        self.updated.append(reservation)


class _Reservation:
    def __init__(self, reservation_id="r-1", room_id="room-1", state="CONFIRMED"):
        self.id = "pms-1"
        self.reservation_id = reservation_id
        self.room_id = room_id
        self.room_type = "SUITE"
        self.guest_name = "User123"
        self.hotel_id = "HotelXYZ"
        self.fecha_reserva = "2026-11-01"
        self.state = state
        self.version = 1


def _client() -> TestClient:
    return TestClient(create_app())


def test_confirm_reservation_returns_existing_message():
    repo = _Repo(existing=_Reservation(reservation_id="res-1"))
    bus = _Bus()

    result = ConfirmReservation(repo, bus).execute("res-1", "room-1", "2026-11-01")

    assert result["message"] == "Reservation already processed"
    assert bus.events == []


def test_confirm_reservation_blocks_active_booking_and_publishes_failure():
    repo = _Repo(active=_Reservation(state="CONFIRMED"))
    bus = _Bus()

    result = ConfirmReservation(repo, bus).execute("res-2", "room-9", "2026-11-01")

    assert result["message"] == "Room is already actively booked for this date"
    assert result["state"] == "CONFIRMED"
    assert bus.events[0][1] == "ReservaRechazadaPmsEvt"


def test_confirm_reservation_success(monkeypatch):
    created = _Reservation(reservation_id="res-3", room_id="room-3", state="CONFIRMED")
    repo = _Repo()
    bus = _Bus()

    monkeypatch.setattr(
        "modules.pms.application.commands.confirm_reservation.Reservation.create",
        lambda *args, **kwargs: created,
    )

    result = ConfirmReservation(repo, bus).execute("res-3", "room-3", "2026-11-05")

    assert result["id_reserva"] == "res-3"
    assert result["fecha_reserva"] == "2026-11-05"
    assert len(repo.saved) == 1
    assert bus.events[0][1] == "ConfirmacionPmsExitosaEvt"


def test_confirm_reservation_handles_unexpected_error_and_publishes_failure(monkeypatch):
    repo = _Repo(save_error=RuntimeError("db down"))
    bus = _Bus()

    monkeypatch.setattr(
        "modules.pms.application.commands.confirm_reservation.Reservation.create",
        lambda *args, **kwargs: _Reservation(reservation_id="res-4", room_id="room-4"),
    )

    result = ConfirmReservation(repo, bus).execute("res-4", "room-4", "2026-11-06")

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

    result = CancelReservation(repo, bus).execute("res-5")

    assert result == {"message": "Reservation is already cancelled"}


def test_cancel_reservation_success_updates_and_publishes():
    reservation = _Reservation(reservation_id="res-6", room_id="room-6", state="CONFIRMED")
    repo = _Repo(existing=reservation)
    bus = _Bus()

    result = CancelReservation(repo, bus).execute("res-6")

    assert result["state"] == "CANCELLED"
    assert result["event_generated"] == "ConfirmacionPmsCanceladaEvt"
    assert len(repo.updated) == 1
    assert bus.events[0][1] == "ConfirmacionPmsCanceladaEvt"


def test_router_health_endpoint():
    response = _client().get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "PMS Integration Service running"}


def test_router_cancelar_reserva_delegates_command(monkeypatch):
    class FakeCancelReservation:
        def __init__(self, repository, event_bus):
            pass

        def execute(self, reservation_id):
            return {"reservation_id": reservation_id, "state": "CANCELLED"}

    monkeypatch.setattr(router_module, "CancelReservation", FakeCancelReservation)

    response = _client().post("/cancelar-reserva", json={"id_reserva": "res-10"})

    assert response.status_code == 200
    assert response.json() == {"reservation_id": "res-10", "state": "CANCELLED"}


def test_router_confirmar_reserva_delegates_command(monkeypatch):
    class FakeConfirmReservation:
        def __init__(self, repository, event_bus):
            pass

        def execute(self, id_reserva, id_habitacion, fecha_reserva):
            return {
                "id_reserva": id_reserva,
                "id_habitacion": id_habitacion,
                "fecha_reserva": fecha_reserva,
                "event_generated": "ConfirmacionPmsExitosaEvt",
            }

    monkeypatch.setattr(router_module, "ConfirmReservation", FakeConfirmReservation)

    response = _client().post(
        "/confirmar-reserva",
        json={
            "id_reserva": "res-11",
            "id_habitacion": "room-11",
            "fecha_reserva": "2026-12-01",
        },
    )

    assert response.status_code == 200
    assert response.json()["event_generated"] == "ConfirmacionPmsExitosaEvt"
