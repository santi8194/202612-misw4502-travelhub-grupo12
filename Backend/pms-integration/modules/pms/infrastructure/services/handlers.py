from modules.pms.application.commands.confirm_reservation import ConfirmReservation
from modules.pms.application.commands.cancel_reservation import CancelReservation

from modules.pms.infrastructure.repository import ReservationRepository
from modules.pms.infrastructure.services.event_bus import EventBus


def handle_confirm_reservation(data):

    reservation_id = data["id_reserva"]
    category_id = data["id_categoria"]
    user_id = data["id_usuario"]
    fecha_check_in = data.get("fecha_check_in")
    fecha_check_out = data.get("fecha_check_out")

    print(
        "[PMS] Command received: ConfirmReservation "
        f"reservation={reservation_id} category={category_id} "
        f"check_in={fecha_check_in} check_out={fecha_check_out}"
    )

    repository = ReservationRepository()
    event_bus = EventBus()

    use_case = ConfirmReservation(repository, event_bus)

    result = use_case.execute(
        reservation_id,
        category_id,
        user_id,
        fecha_check_in,
        fecha_check_out,
    )

    print("[PMS] Result:", result)


def handle_cancel_reservation(data):

    reservation_id = data["id_reserva"]

    print(f"[PMS] Command received: CancelReservation for reservation {reservation_id}")

    repository = ReservationRepository()
    event_bus = EventBus()

    use_case = CancelReservation(repository, event_bus)

    result = use_case.execute(reservation_id)

    print("[PMS] Result:", result)