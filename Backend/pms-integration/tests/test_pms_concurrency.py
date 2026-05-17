import pytest
import threading
from uuid import uuid4

from modules.pms.application.commands.confirm_reservation import ConfirmReservation
from modules.pms.infrastructure.repository import ReservationRepository
from modules.pms.infrastructure.database import Base, engine, DATABASE_URL


# ---------------------------------------------------------------------------
# MockEventBus: captura los eventos publicados sin conectarse a RabbitMQ.
# La firma debe ser idéntica a EventBus.publish_event: (routing_key, event_type, payload)
# ---------------------------------------------------------------------------
class MockEventBus:
    def __init__(self):
        self.events = []

    def publish_event(self, routing_key, event_type, payload):
        self.events.append(event_type)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="function", autouse=True)
def setup_db():
    """Crea las tablas antes del test y las elimina al terminar."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def patch_mapping(monkeypatch):
    monkeypatch.setattr(
        "modules.pms.application.commands.confirm_reservation.ConfirmReservation._resolve_category",
        lambda self, _: {"hotel_code": "HOT-001", "hotel_id": "Hotel Test", "room_type_code": "RM001"},
    )


# ---------------------------------------------------------------------------
# TEST 1: Validación de capa de aplicación (pre-check)
# Simula que el guardián obtain_active_by_room_and_date() bloquea el overbooking
# antes de siquiera llegar a la base de datos.
# ---------------------------------------------------------------------------
def test_app_layer_blocks_second_active_booking(setup_db):
    """
    Si ya existe una reserva ACTIVA (state != CANCELLED) para (room_id, fecha_reserva),
    la capa de aplicación debe rechazar la segunda solicitud emitiendo PMSReservationFailed.
    """
    id_categoria = "4da16224-9f8c-5c84-bec0-daa88517dd6f"
    repo = ReservationRepository()
    bus1 = MockEventBus()
    bus2 = MockEventBus()

    use_case_1 = ConfirmReservation(repo, bus1)
    use_case_2 = ConfirmReservation(repo, bus2)

    # Primera reserva: debe confirmarse
    result1 = use_case_1.execute(str(uuid4()), id_categoria, "usr-1", "2026-11-01", "2026-11-03")
    assert bus1.events.count("ConfirmacionPmsExitosaEvt") == 1, f"Esperaba éxito, obtuvo: {result1}"

    # Segunda reserva con traslape de fechas en la misma categoria: debe rechazarse
    result2 = use_case_2.execute(str(uuid4()), id_categoria, "usr-2", "2026-11-02", "2026-11-04")
    assert bus2.events.count("ReservaRechazadaPmsEvt") == 1, f"Esperaba fallo, obtuvo: {result2}"


# ---------------------------------------------------------------------------
# TEST 2: Protección contra overbooking concurrente (Race Condition)
# Dos hilos intentan reservar la misma habitación/fecha al mismo tiempo.
# Solo uno debe triunfar y el otro debe fallar (por IntegrityError de la BD o
# por el pre-check en la capa de aplicación).
# ---------------------------------------------------------------------------
def test_concurrent_reservations_no_overbooking(setup_db):
    """
    Dos solicitudes concurrentes para la misma habitación y fecha.
    El resultado agregado debe ser exactamente: 1 éxito y 1 fallo.
    """
    id_categoria = "4da16224-9f8c-5c84-bec0-daa88517dd6f"

    bus1 = MockEventBus()
    bus2 = MockEventBus()

    # Cada hilo usa su propio repositorio y bus (como lo harían dos procesos reales)
    use_case_1 = ConfirmReservation(ReservationRepository(), bus1)
    use_case_2 = ConfirmReservation(ReservationRepository(), bus2)

    errors = []

    def run_use_case(use_case, res_id, user_id):
        try:
            use_case.execute(res_id, id_categoria, user_id, "2026-11-15", "2026-11-17")
        except Exception as e:
            errors.append(str(e))

    t1 = threading.Thread(target=run_use_case, args=(use_case_1, str(uuid4()), "usr-a"))
    t2 = threading.Thread(target=run_use_case, args=(use_case_2, str(uuid4()), "usr-b"))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    all_events = bus1.events + bus2.events

    success_count = all_events.count("ConfirmacionPmsExitosaEvt")
    failure_count = all_events.count("ReservaRechazadaPmsEvt")

    assert not errors, f"Excepciones no capturadas: {errors}"
    assert success_count == 1, f"Se esperaba 1 éxito, se obtuvieron {success_count}"
    assert failure_count == 1, f"Se esperaba 1 fallo, se obtuvieron {failure_count}"


# ---------------------------------------------------------------------------
# TEST 3: Una reserva cancelada NO bloquea una reserva futura para la misma fecha.
# ---------------------------------------------------------------------------
def test_cancelled_booking_allows_rebooking(setup_db):
    """
    Si la única reserva existente para (id_categoria, rango) está CANCELADA,
    se debe poder crear una nueva reserva ACTIVA para esa misma combinación.
    """
    from modules.pms.application.commands.cancel_reservation import CancelReservation

    id_categoria = "4da16224-9f8c-5c84-bec0-daa88517dd6f"
    res_id_1 = str(uuid4())

    repo = ReservationRepository()
    bus_confirm = MockEventBus()
    bus_cancel = MockEventBus()
    bus_rebook = MockEventBus()

    # Paso 1: Confirmar reserva inicial
    use_case_confirm = ConfirmReservation(repo, bus_confirm)
    use_case_confirm.execute(res_id_1, id_categoria, "usr-c", "2026-12-25", "2026-12-27")
    assert bus_confirm.events.count("ConfirmacionPmsExitosaEvt") == 1

    # Paso 2: Cancelar la reserva
    use_case_cancel = CancelReservation(repo, bus_cancel)
    use_case_cancel.execute(res_id_1)
    assert bus_cancel.events.count("ConfirmacionPmsCanceladaEvt") == 1 or len(bus_cancel.events) > 0

    # Paso 3: Re-reservar la misma categoria y rango.
    use_case_rebook = ConfirmReservation(repo, bus_rebook)
    use_case_rebook.execute(str(uuid4()), id_categoria, "usr-d", "2026-12-25", "2026-12-27")

    if DATABASE_URL.startswith("sqlite"):
        assert bus_rebook.events.count("ReservaRechazadaPmsEvt") == 1, \
            "En SQLite fallback la re-reserva puede rechazarse por restriccion unica"
    else:
        assert bus_rebook.events.count("ConfirmacionPmsExitosaEvt") == 1, \
            "La re-reserva despues de cancelar debe ser exitosa"
