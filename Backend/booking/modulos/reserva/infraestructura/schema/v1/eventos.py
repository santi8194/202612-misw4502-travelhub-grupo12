import uuid
from typing import Optional
from seedwork.infraestructura.schema.v1.eventos import EventoIntegracion

class ReservaCreadaPayload:
    def __init__(self, id_reserva: str, id_usuario: str, id_categoria: str, estado: str, fecha_creacion: str, fecha_reserva: str = None, monto: float = None, moneda: str = "COP", fecha_check_in: str = None, fecha_check_out: str = None):
        self.id_reserva = id_reserva
        self.id_usuario = id_usuario
        self.id_categoria = id_categoria
        self.estado = estado
        self.fecha_creacion = fecha_creacion
        self.fecha_reserva = fecha_reserva
        self.monto = monto
        self.moneda = moneda
        self.fecha_check_in = fecha_check_in
        self.fecha_check_out = fecha_check_out

    def to_dict(self):
        return {
            "id_reserva": self.id_reserva,
            "id_usuario": self.id_usuario,
            "id_categoria": self.id_categoria,
            "estado": self.estado,
            "fecha_creacion": self.fecha_creacion,
            "fecha_reserva": self.fecha_reserva,
            "monto": self.monto,
            "moneda": self.moneda,
            "fecha_check_in": self.fecha_check_in,
            "fecha_check_out": self.fecha_check_out
        }

class EventoReservaCreada(EventoIntegracion):
    def __init__(self, data: ReservaCreadaPayload, id: str = None, time: str = None, ingestion: str = None, specversion: str = "v1", type: str = "ReservaCreada", datacontenttype: str = "application/json", service_name: str = "booking"):
        super().__init__()
        self.id = id or str(uuid.uuid4())
        self.time = time
        self.ingestion = ingestion
        self.specversion = specversion
        self.type = type
        self.datacontenttype = datacontenttype
        self.service_name = service_name
        self.data = data

    def to_dict(self):
        return {
            "id": self.id,
            "time": self.time,
            "ingestion": self.ingestion,
            "specversion": self.specversion,
            "type": self.type,
            "datacontenttype": self.datacontenttype,
            "service_name": self.service_name,
            "data": self.data.to_dict() if self.data else None
        }

class ReservaConfirmadaPayload:
    def __init__(
        self,
        id_reserva: str, id_cliente: str,
        emailCliente: Optional[str] = None,
        codigo_reserva: Optional[str] = None,
        categoria: Optional[str] = None,
        fecha_check_in: Optional[str] = None,
        fecha_check_out: Optional[str] = None,
        huespedes: Optional[int] = None,
        moneda: Optional[str] = None,
    ):
        self.id_reserva = id_reserva
        self.id_cliente = id_cliente
        self.emailCliente = emailCliente
        self.codigo_reserva = codigo_reserva
        self.categoria = categoria
        self.fecha_check_in = fecha_check_in
        self.fecha_check_out = fecha_check_out
        self.huespedes = huespedes
        self.moneda = moneda

    def to_dict(self):
        return {
            "id_reserva": self.id_reserva,
            "id_cliente": self.id_cliente,
            "emailCliente": self.emailCliente,
            "codigo_reserva": self.codigo_reserva,
            "categoria": self.categoria,
            "fecha_check_in": self.fecha_check_in,
            "fecha_check_out": self.fecha_check_out,
            "huespedes": self.huespedes,
            "moneda": self.moneda,
        }

class EventoReservaConfirmada(EventoIntegracion):
    def __init__(self, data: ReservaConfirmadaPayload, id: str = None, time: str = None, ingestion: str = None, specversion: str = "v1", type: str = "ReservaConfirmadaEvt", datacontenttype: str = "application/json", service_name: str = "booking"):
        super().__init__()
        self.id = id or str(uuid.uuid4())
        self.time = time
        self.ingestion = ingestion
        self.specversion = specversion
        self.type = type
        self.datacontenttype = datacontenttype
        self.service_name = service_name
        self.data = data

    def to_dict(self):
        return {
            "id": self.id,
            "time": self.time,
            "ingestion": self.ingestion,
            "specversion": self.specversion,
            "type": self.type,
            "datacontenttype": self.datacontenttype,
            "service_name": self.service_name,
            "data": self.data.to_dict() if self.data else None
        }


class ReservaCanceladaPayload:
    def __init__(
        self,
        id_reserva: str,
        emailCliente: Optional[str] = None,
        codigo_reserva: Optional[str] = None,
        categoria: Optional[str] = None,
        fecha_check_in: Optional[str] = None,
        fecha_check_out: Optional[str] = None,
        huespedes: Optional[int] = None,
        moneda: Optional[str] = None,
        motivo_cancelacion: Optional[str] = None,
    ):
        self.id_reserva = id_reserva
        self.emailCliente = emailCliente
        self.codigo_reserva = codigo_reserva
        self.categoria = categoria
        self.fecha_check_in = fecha_check_in
        self.fecha_check_out = fecha_check_out
        self.huespedes = huespedes
        self.moneda = moneda
        self.motivo_cancelacion = motivo_cancelacion

    def to_dict(self):
        return {
            "id_reserva": self.id_reserva,
            "emailCliente": self.emailCliente,
            "codigo_reserva": self.codigo_reserva,
            "categoria": self.categoria,
            "fecha_check_in": self.fecha_check_in,
            "fecha_check_out": self.fecha_check_out,
            "huespedes": self.huespedes,
            "moneda": self.moneda,
            "motivo_cancelacion": self.motivo_cancelacion,
        }


class EventoReservaCancelada(EventoIntegracion):
    def __init__(self, data: ReservaCanceladaPayload, id: str = None, time: str = None, ingestion: str = None, specversion: str = "v1", type: str = "ReservaCanceladaEvt", datacontenttype: str = "application/json", service_name: str = "booking"):
        super().__init__()
        self.id = id or str(uuid.uuid4())
        self.time = time
        self.ingestion = ingestion
        self.specversion = specversion
        self.type = type
        self.datacontenttype = datacontenttype
        self.service_name = service_name
        self.data = data

    def to_dict(self):
        return {
            "id": self.id,
            "time": self.time,
            "ingestion": self.ingestion,
            "specversion": self.specversion,
            "type": self.type,
            "datacontenttype": self.datacontenttype,
            "service_name": self.service_name,
            "data": self.data.to_dict() if self.data else None
        }
