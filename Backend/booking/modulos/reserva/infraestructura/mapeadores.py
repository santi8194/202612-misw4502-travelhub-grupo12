from seedwork.dominio.repositorios import Mapeador
from seedwork.dominio.eventos import EventoDominio
from modulos.reserva.dominio.eventos import ReservaPendiente, ReservaConfirmadaEvt, ReservaCanceladaEvt
from .schema.v1.eventos import EventoReservaCreada, ReservaCreadaPayload, EventoReservaConfirmada, ReservaConfirmadaPayload, EventoReservaCancelada, ReservaCanceladaPayload
import datetime

class MapeadorEventosReserva(Mapeador):

    versions = ('v1',)
    LATEST_VERSION = versions[0]

    def __init__(self):
        self.router = {
            ReservaPendiente: self._entidad_a_reserva_creada,
            ReservaConfirmadaEvt: self._entidad_a_reserva_confirmada,
            ReservaCanceladaEvt: self._entidad_a_reserva_cancelada,
        }

    def obtener_tipo(self) -> type:
        return EventoDominio.__class__

    def es_version_valida(self, version):
        for v in self.versions:
            if v == version:
                return True
        return False

    def _entidad_a_reserva_creada(self, evento: ReservaPendiente, version=LATEST_VERSION):
        def v1(ev):
            payload = ReservaCreadaPayload(
                id_reserva=str(ev.id_reserva),
                id_usuario=str(ev.id_usuario),
                id_categoria=str(ev.id_categoria),
                estado="PENDIENTE",
                fecha_creacion=ev.fecha_evento.isoformat() if hasattr(ev, 'fecha_evento') else datetime.datetime.now().isoformat(),
                fecha_reserva=ev.fecha_reserva if hasattr(ev, 'fecha_reserva') else None,
                monto=ev.monto if hasattr(ev, 'monto') else None,
                moneda=ev.moneda if hasattr(ev, 'moneda') else "COP",
                fecha_check_in=ev.fecha_check_in if hasattr(ev, 'fecha_check_in') else None,
                fecha_check_out=ev.fecha_check_out if hasattr(ev, 'fecha_check_out') else None
            )
            evento_integracion = EventoReservaCreada(
                id=str(ev.id),
                time=datetime.datetime.now().isoformat(),
                specversion=str(version),
                type='ReservaCreadaIntegracionEvt',
                data=payload
            )
            return evento_integracion

        if not self.es_version_valida(version):
            raise Exception(f'No se sabe procesar la version {version}')

        if version == 'v1':
            return v1(evento)

    def _entidad_a_reserva_confirmada(self, evento: ReservaConfirmadaEvt, version=LATEST_VERSION):
        def v1(ev):
            email_cliente = getattr(ev, "emailCliente", None) or getattr(ev, "email_cliente", None) or ""
            payload = ReservaConfirmadaPayload(
                id_reserva=str(ev.id_reserva),
                emailCliente=email_cliente,
                codigo_reserva=getattr(ev, "codigo_reserva", None),
                categoria=getattr(ev, "categoria", None),
                fecha_check_in=getattr(ev, "fecha_check_in", None),
                fecha_check_out=getattr(ev, "fecha_check_out", None),
                huespedes=getattr(ev, "huespedes", None),
                moneda=getattr(ev, "moneda", None),
            )
            evento_integracion = EventoReservaConfirmada(
                id=str(ev.id),
                time=datetime.datetime.now().isoformat(),
                specversion=str(version),
                type='ReservaConfirmadaEvt',
                data=payload
            )
            return evento_integracion

        if not self.es_version_valida(version):
            raise Exception(f'No se sabe procesar la version {version}')

        if version == 'v1':
            return v1(evento)

    def _entidad_a_reserva_cancelada(self, evento: ReservaCanceladaEvt, version=LATEST_VERSION):
        def v1(ev):
            email_cliente = getattr(ev, "emailCliente", None) or getattr(ev, "email_cliente", None) or ""
            payload = ReservaCanceladaPayload(
                id_reserva=str(ev.id_reserva),
                emailCliente=email_cliente,
                codigo_reserva=getattr(ev, "codigo_reserva", None),
                categoria=getattr(ev, "categoria", None),
                fecha_check_in=getattr(ev, "fecha_check_in", None),
                fecha_check_out=getattr(ev, "fecha_check_out", None),
                huespedes=getattr(ev, "huespedes", None),
                moneda=getattr(ev, "moneda", None),
                motivo_cancelacion=getattr(ev, "motivo_cancelacion", None),
            )
            evento_integracion = EventoReservaCancelada(
                id=str(ev.id),
                time=datetime.datetime.now().isoformat(),
                specversion=str(version),
                type='ReservaCanceladaEvt',
                data=payload
            )
            return evento_integracion

        if not self.es_version_valida(version):
            raise Exception(f'No se sabe procesar la version {version}')

        if version == 'v1':
            return v1(evento)

    def entidad_a_dto(self, entidad: EventoDominio, version=LATEST_VERSION):
        if not entidad:
            raise Exception("Evento nulo")
        
        func = self.router.get(entidad.__class__, None)
        if not func:
            print(f"[Mapeador] ADVERTENCIA: No existe implementación para el evento de dominio {entidad.__class__.__name__}. Se retornará nulo.")
            return None

        return func(entidad, version=version)

    def dto_a_entidad(self, dto, version=LATEST_VERSION):
        raise NotImplementedError
