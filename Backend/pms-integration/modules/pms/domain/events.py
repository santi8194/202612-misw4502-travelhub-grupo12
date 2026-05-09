class PMSReservationConfirmed:

    def __init__(self, pms_id, reservation_id, fecha_reserva=None):
        self.routing_key = "evt.pms.confirmacion_exitosa"
        self.type = "ConfirmacionPmsExitosaEvt"
        self.pms_id = pms_id
        self.reservation_id = reservation_id
        self.fecha_reserva = fecha_reserva

    def to_dict(self):
        return {
            "codigo_pms": self.pms_id,
            "id_reserva": self.reservation_id,
            "fecha_reserva": self.fecha_reserva
        }


class PMSReservationFailed:

    def __init__(self, reservation_id, reason, fecha_reserva=None):
        self.routing_key = "evt.pms.rechazada"
        self.type = "ReservaRechazadaPmsEvt"
        self.reservation_id = reservation_id
        self.reason = reason
        self.fecha_reserva = fecha_reserva

    def to_dict(self):
        return {
            "id_reserva": self.reservation_id,
            "motivo": self.reason,
            "fecha_reserva": self.fecha_reserva
        }


class PMSReservationCancelled:
    def __init__(self, reservation_id, room_id):
        self.routing_key = "evt.pms.reserva_cancelada"
        self.type = "ConfirmacionPmsCanceladaEvt"
        self.reservation_id = reservation_id
        self.room_id = room_id

    def to_dict(self):
        return {
            "id_habitacion": self.room_id,
            "id_reserva": self.reservation_id
        }


class PMSInventoryUpdated:
    """
    Evento publicado cuando el PMS notifica un cambio de inventario.
    
    Este evento es consumido por Catalog para actualizar su inventario.
    """
    
    def __init__(self, id_propiedad, id_categoria, fecha, cupos_disponibles, event_timestamp):
        self.routing_key = "pms.inventory.updated"
        self.type = "PMSInventoryUpdated"
        self.id_propiedad = str(id_propiedad)
        self.id_categoria = str(id_categoria)
        self.fecha = fecha.isoformat() if hasattr(fecha, 'isoformat') else fecha
        self.cupos_disponibles = cupos_disponibles
        self.event_timestamp = event_timestamp.isoformat() if hasattr(event_timestamp, 'isoformat') else event_timestamp

    def to_dict(self):
        return {
            "type": self.type,
            "id_propiedad": self.id_propiedad,
            "id_categoria": self.id_categoria,
            "fecha": self.fecha,
            "cupos_disponibles": self.cupos_disponibles,
            "event_timestamp": self.event_timestamp
        }