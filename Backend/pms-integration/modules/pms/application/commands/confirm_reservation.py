import json
from datetime import date
from functools import lru_cache
from pathlib import Path

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError

from modules.pms.domain.entities import Reservation
from modules.pms.domain.events import PMSReservationConfirmed, PMSReservationFailed


class ConfirmReservation:

    def __init__(self, repository, event_bus):
        self.repository = repository
        self.event_bus = event_bus

    @staticmethod
    @lru_cache(maxsize=1)
    def _category_mapping():
        mapping_path = Path(__file__).resolve().parents[4] / "data" / "pms_uuid_mapping_full.json"
        with open(mapping_path, encoding="utf-8") as f:
            return json.load(f)

    def _resolve_category(self, id_categoria: str):
        mapping = self._category_mapping()
        target = str(id_categoria)

        if isinstance(mapping.get("mappings"), dict):
            mapping = mapping["mappings"]

        # Legacy mapping shape: {"hotels": [{"room_types": [...]}]}
        for hotel in mapping.get("hotels", []):
            for room_type in hotel.get("room_types", []):
                if str(room_type.get("category_uuid")) == target:
                    return {
                        "hotel_code": hotel.get("hotel_code"),
                        "hotel_id": hotel.get("hotel_name") or hotel.get("hotel_code"),
                        "room_type_code": room_type.get("room_type_code"),
                    }

        # Current mapping shape: {"HOTEL_CODE": {"rooms": {"RM": {...}}}}
        for hotel_code, hotel_data in mapping.items():
            if hotel_code == "hotels" or not isinstance(hotel_data, dict):
                continue

            rooms = hotel_data.get("rooms") or {}
            if not isinstance(rooms, dict):
                continue

            for room_code, room_data in rooms.items():
                if str(room_data.get("category_uuid")) == target:
                    resolved_room_type = room_data.get("room_type_code") or room_code
                    resolved_hotel_code = hotel_data.get("hotel_code") or hotel_code
                    return {
                        "hotel_code": resolved_hotel_code,
                        "hotel_id": hotel_data.get("hotel_name") or resolved_hotel_code,
                        "room_type_code": resolved_room_type,
                    }

        return None

    @staticmethod
    def _parse_dates(fecha_check_in: str, fecha_check_out: str):
        try:
            check_in = date.fromisoformat(fecha_check_in)
            check_out = date.fromisoformat(fecha_check_out)
        except Exception as exc:
            raise ValueError("Las fechas de check-in/check-out deben usar formato YYYY-MM-DD") from exc

        if check_out <= check_in:
            raise ValueError("fecha_check_out debe ser posterior a fecha_check_in")

        return check_in.isoformat(), check_out.isoformat()

    def execute(self, id_reserva, id_categoria, id_usuario, fecha_check_in, fecha_check_out):

        if not id_usuario:
            raise ValueError("id_usuario es obligatorio para confirmar en PMS")

        check_in_str, check_out_str = self._parse_dates(fecha_check_in, fecha_check_out)

        category_mapping = self._resolve_category(id_categoria)
        if not category_mapping:
            pms_event = PMSReservationFailed(
                reservation_id=id_reserva,
                reason=f"No existe mapeo de categoria PMS para {id_categoria}",
                fecha_check_in=check_in_str,
                fecha_check_out=check_out_str,
            )
            self.event_bus.publish_event(
                routing_key=pms_event.routing_key,
                event_type=pms_event.type,
                payload=pms_event.to_dict(),
            )
            return {
                "event_generated": pms_event.type,
                "motivo": pms_event.reason,
                "id_reserva": id_reserva,
            }

        existing_reservation = self.repository.obtain_by_reservation_id(id_reserva)

        print(f"[PMS] Checking existing reservation for id {id_reserva}: {'Found' if existing_reservation else 'Not found'}")

        if existing_reservation:
            return {
                "message": "Reservation already processed",
                "current_reservation_id": existing_reservation.reservation_id,
            }

        active_booking = self.repository.obtain_active_by_category_and_range(
            str(id_categoria),
            check_in_str,
            check_out_str,
        )
        if active_booking:
            print(
                f"[PMS] Category {id_categoria} is already ACTIVELY booked "
                f"between {check_in_str} and {check_out_str} (State: {active_booking.state})"
            )
            pms_event = PMSReservationFailed(
                reservation_id=id_reserva,
                reason=(
                    "Proteccion contra overbooking: la categoria no tiene disponibilidad "
                    "en las fechas seleccionadas."
                ),
                fecha_check_in=check_in_str,
                fecha_check_out=check_out_str,
            )
            self.event_bus.publish_event(
                routing_key=pms_event.routing_key,
                event_type=pms_event.type,
                payload=pms_event.to_dict(),
            )
            return {
                "message": "Category is already actively booked for this date range",
                "state": active_booking.state,
            }

        try:
            pms_reservation = Reservation.create(
                id_reserva,
                id_categoria,
                id_usuario,
                check_in_str,
                check_out_str,
                category_mapping["hotel_id"],
                category_mapping["hotel_code"],
                category_mapping["room_type_code"],
            )

            self.repository.save(pms_reservation)

            pms_event = PMSReservationConfirmed(
                pms_id=pms_reservation.id,
                reservation_id=id_reserva,
                fecha_check_in=check_in_str,
                fecha_check_out=check_out_str,
                id_categoria=str(id_categoria),
                id_usuario=str(id_usuario),
                hotel_id=category_mapping["hotel_id"],
            )
            self.event_bus.publish_event(
                routing_key=pms_event.routing_key,
                event_type=pms_event.type,
                payload=pms_event.to_dict(),
            )

            return pms_event.to_dict()

        except IntegrityError:
            print(
                f"[PMS] IntegrityError caught for category {id_categoria} "
                f"between {check_in_str} and {check_out_str}. Overbooking avoided."
            )
            pms_event = PMSReservationFailed(
                reservation_id=id_reserva,
                reason="Proteccion contra overbooking: categoria ya reservada para este rango.",
                fecha_check_in=check_in_str,
                fecha_check_out=check_out_str,
            )
        except StaleDataError:
            print(f"[PMS] StaleDataError caught for category {id_categoria}. Overbooking avoided.")
            pms_event = PMSReservationFailed(
                reservation_id=id_reserva,
                reason="Proteccion contra overbooking: categoria ya reservada para este rango.",
                fecha_check_in=check_in_str,
                fecha_check_out=check_out_str,
            )
        except Exception as e:
            print(f"[PMS] Error inesperado: {str(e)}")
            pms_event = PMSReservationFailed(
                reservation_id=id_reserva,
                reason=str(e),
                fecha_check_in=check_in_str,
                fecha_check_out=check_out_str,
            )

        self.event_bus.publish_event(
            routing_key=pms_event.routing_key,
            event_type=pms_event.type,
            payload=pms_event.to_dict(),
        )

        return {
            "event_generated": pms_event.type,
            "motivo": pms_event.reason,
            "id_reserva": id_reserva,
        }