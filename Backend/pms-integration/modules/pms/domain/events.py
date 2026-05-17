class PMSReservationConfirmed:

    def __init__(self, pms_id, reservation_id, fecha_check_in=None, fecha_check_out=None, id_categoria=None, id_usuario=None, hotel_id=None):
        self.routing_key = "evt.pms.confirmacion_exitosa"
        self.type = "ConfirmacionPmsExitosaEvt"
        self.pms_id = pms_id
        self.reservation_id = reservation_id
        self.fecha_check_in = fecha_check_in
        self.fecha_check_out = fecha_check_out
        self.id_categoria = id_categoria
        self.id_usuario = id_usuario
        self.hotel_id = hotel_id

    def to_dict(self):
        return {
            "codigo_pms": self.pms_id,
            "id_reserva": self.reservation_id,
            "fecha_check_in": self.fecha_check_in,
            "fecha_check_out": self.fecha_check_out,
            "id_categoria": self.id_categoria,
            "id_usuario": self.id_usuario,
            "hotel_id": self.hotel_id
        }


class PMSReservationFailed:

    def __init__(self, reservation_id, reason, fecha_check_in=None, fecha_check_out=None):
        self.routing_key = "evt.pms.rechazada"
        self.type = "ReservaRechazadaPmsEvt"
        self.reservation_id = reservation_id
        self.reason = reason
        self.fecha_check_in = fecha_check_in
        self.fecha_check_out = fecha_check_out

    def to_dict(self):
        return {
            "id_reserva": self.reservation_id,
            "motivo": self.reason,
            "fecha_check_in": self.fecha_check_in,
            "fecha_check_out": self.fecha_check_out
        }


class PMSReservationCancelled:
    def __init__(self, reservation_id, id_categoria=None):
        self.routing_key = "evt.pms.reserva_cancelada"
        self.type = "ConfirmacionPmsCanceladaEvt"
        self.reservation_id = reservation_id
        self.id_categoria = id_categoria

    def to_dict(self):
        return {
            "id_categoria": self.id_categoria,
            "id_reserva": self.reservation_id
        }


class PMSInventoryUpdated:
    """
    Evento publicado cuando el PMS notifica un cambio de inventario.
    
    Este evento es consumido por Catalog para actualizar su inventario.
    Catalog resuelve el UUID de la categoría usando el codigo_mapeo_pms.
    """
    
    def __init__(self, codigo_mapeo_pms, fecha, cupos_totales, cupos_disponibles, event_timestamp):
        self.routing_key = "pms.inventory.updated"
        self.type = "PMSInventoryUpdated"
        self.codigo_mapeo_pms = codigo_mapeo_pms
        self.fecha = fecha.isoformat() if hasattr(fecha, 'isoformat') else fecha
        self.cupos_totales = cupos_totales
        self.cupos_disponibles = cupos_disponibles
        self.event_timestamp = event_timestamp.isoformat() if hasattr(event_timestamp, 'isoformat') else event_timestamp

    def to_dict(self):
        return {
            "type": self.type,
            "codigo_mapeo_pms": self.codigo_mapeo_pms,
            "fecha": self.fecha,
            "cupos_totales": self.cupos_totales,
            "cupos_disponibles": self.cupos_disponibles,
            "event_timestamp": self.event_timestamp
        }