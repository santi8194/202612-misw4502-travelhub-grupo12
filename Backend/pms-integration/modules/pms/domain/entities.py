from uuid import uuid4, UUID
from dataclasses import dataclass


@dataclass
class Reservation:
    id: UUID
    reservation_id: UUID
    id_categoria: str
    id_usuario: str
    hotel_code: str
    room_type_code: str
    hotel_id: str
    fecha_check_in: str
    fecha_check_out: str
    state: str
    version: int = 1

    @staticmethod
    def create(reservation_id, id_categoria, id_usuario, fecha_check_in, fecha_check_out, hotel_id, hotel_code, room_type_code):
        return Reservation(
            id=str(uuid4()),
            reservation_id=str(reservation_id),
            id_categoria=str(id_categoria),
            id_usuario=str(id_usuario),
            hotel_code=str(hotel_code),
            room_type_code=str(room_type_code),
            hotel_id=str(hotel_id),
            fecha_check_in=fecha_check_in,
            fecha_check_out=fecha_check_out,
            state="CONFIRMED",
            version=1
        )
    
    def cancel(self):
        self.state = "CANCELED"