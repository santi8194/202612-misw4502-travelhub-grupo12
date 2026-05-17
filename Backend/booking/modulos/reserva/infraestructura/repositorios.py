from modulos.reserva.infraestructura.mapeadores_dto import MapeadorReservaDTO
from seedwork.dominio.repositorios import Repositorio
from modulos.reserva.dominio.entidades import Reserva, Usuario, CategoriaHabitacion
from modulos.reserva.dominio.objetos_valor import EstadoReserva, Pax
from modulos.reserva.infraestructura.dto import AuditoriaCancelacionReservaDTO, ReservaDTO
from config.db import db
import logging
import uuid
import datetime

logger = logging.getLogger(__name__)

class RepositorioReservas(Repositorio):

    def __init__(self):
        self._mapeador = MapeadorReservaDTO()

    def agregar(self, entidad: Reserva):
        reserva_dto = self._mapeador.entidad_a_dto(entidad)
        db.session.add(reserva_dto)

    def actualizar(self, entidad: Reserva):
        reserva_dto = db.session.query(ReservaDTO).filter_by(id=str(entidad.id)).first()
        if reserva_dto:
            reserva_dto.usuario = str(entidad.usuario.id) if entidad.usuario and entidad.usuario.id else reserva_dto.usuario
            if entidad.usuario and entidad.usuario.email is not None:
                reserva_dto.usuario_email = entidad.usuario.email
            reserva_dto.id_categoria = str(entidad.id_categoria) if entidad.id_categoria else None
            reserva_dto.codigo_confirmacion_ota = entidad.codigo_confirmacion_ota
            reserva_dto.codigo_localizador_pms = entidad.codigo_localizador_pms
            reserva_dto.estado = entidad.estado.value
            reserva_dto.fecha_check_in = entidad.fecha_check_in.isoformat() if entidad.fecha_check_in else None
            reserva_dto.fecha_check_out = entidad.fecha_check_out.isoformat() if entidad.fecha_check_out else None
            reserva_dto.ocupacion_adultos = entidad.ocupacion.adultos if entidad.ocupacion else None
            reserva_dto.ocupacion_ninos = entidad.ocupacion.ninos if entidad.ocupacion else None
            reserva_dto.ocupacion_infantes = entidad.ocupacion.infantes if entidad.ocupacion else None
            reserva_dto.fecha_actualizacion = entidad.fecha_actualizacion

    def eliminar(self, entidad_id: str):
        db.session.query(ReservaDTO).filter_by(id=entidad_id).delete()

    def obtener_por_id(self, id: str) -> Reserva:
        logger.info(f"Obteniendo reserva por ID: {id}")
        reserva_dto = db.session.query(ReservaDTO).filter_by(id=id).first()
        if not reserva_dto:
            logger.warning(f"No se encontró ninguna reserva con ID: {id}")
            return None
        logger.info(f"Reserva encontrada: {reserva_dto}")
        return self._mapeador.dto_a_entidad(reserva_dto)

    def obtener_todos(self) -> list[Reserva]:
        dtos = db.session.query(ReservaDTO).all()
        return [self._mapeador.dto_a_entidad(dto) for dto in dtos]

    def obtener_por_usuario(self, id_usuario: str) -> list[Reserva]:
        dtos = (db.session.query(ReservaDTO)
                .filter_by(usuario=id_usuario)
                .order_by(ReservaDTO.fecha_creacion.desc())
                .all())
        return [self._mapeador.dto_a_entidad(dto) for dto in dtos]

    def obtener_por_categorias(self, ids_categoria: list[str]) -> list[Reserva]:
        if not ids_categoria:
            return []

        dtos = (
            db.session.query(ReservaDTO)
            .filter(ReservaDTO.id_categoria.in_(ids_categoria))
            .order_by(ReservaDTO.fecha_creacion.desc())
            .all()
        )
        return [self._mapeador.dto_a_entidad(dto) for dto in dtos]

    def obtener_activa_por_usuario_categoria_fechas(
        self,
        id_usuario: str,
        id_categoria: str,
        fecha_check_in: datetime.date,
        fecha_check_out: datetime.date,
    ) -> Reserva | None:
        if not id_usuario or not id_categoria or not fecha_check_in or not fecha_check_out:
            return None

        reserva_dto = (
            db.session.query(ReservaDTO)
            .filter_by(
                usuario=id_usuario,
                id_categoria=id_categoria,
                fecha_check_in=fecha_check_in.isoformat(),
                fecha_check_out=fecha_check_out.isoformat(),
            )
            .filter(ReservaDTO.estado.in_([EstadoReserva.HOLD.value, EstadoReserva.PENDIENTE.value]))
            .order_by(ReservaDTO.fecha_creacion.desc())
            .first()
        )

        if not reserva_dto:
            return None

        return self._mapeador.dto_a_entidad(reserva_dto)


class RepositorioAuditoriaCancelacionReserva:
    def agregar(self, auditoria: AuditoriaCancelacionReservaDTO):
        db.session.add(auditoria)

    def obtener_ultima_por_reserva(self, id_reserva: str) -> AuditoriaCancelacionReservaDTO | None:
        return (
            db.session.query(AuditoriaCancelacionReservaDTO)
            .filter_by(id_reserva=str(id_reserva))
            .order_by(AuditoriaCancelacionReservaDTO.created_at.desc())
            .first()
        )

    def obtener_por_reserva_referencia_y_estado(
        self,
        id_reserva: str,
        cancellation_reference: str,
        estado_nuevo: str,
    ) -> AuditoriaCancelacionReservaDTO | None:
        return (
            db.session.query(AuditoriaCancelacionReservaDTO)
            .filter_by(
                id_reserva=str(id_reserva),
                cancellation_reference=cancellation_reference,
                estado_nuevo=estado_nuevo,
            )
            .order_by(AuditoriaCancelacionReservaDTO.created_at.desc())
            .first()
        )

    def registrar_inicio_cancelacion(
        self,
        *,
        id_reserva: str,
        id_usuario: str | None,
        ip_origen: str | None,
        motivo: str | None,
        estado_anterior: str,
        estado_nuevo: str,
        politica_tipo: str | None,
        dias_anticipacion: int | None,
        porcentaje_penalidad: float | None,
        monto_pagado: float | None,
        monto_reembolso: float | None,
        refund_status: str | None,
        pms_status: str | None,
        cancellation_reference: str,
        origen: str = "HU_WEB_11",
    ) -> AuditoriaCancelacionReservaDTO:
        existente = self.obtener_por_reserva_referencia_y_estado(
            id_reserva=id_reserva,
            cancellation_reference=cancellation_reference,
            estado_nuevo=estado_nuevo,
        )
        if existente:
            return existente

        auditoria = AuditoriaCancelacionReservaDTO(
            id=str(uuid.uuid4()),
            id_reserva=str(id_reserva),
            id_usuario=str(id_usuario) if id_usuario else None,
            ip_origen=ip_origen,
            motivo=motivo,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            politica_tipo=politica_tipo,
            dias_anticipacion=dias_anticipacion,
            porcentaje_penalidad=porcentaje_penalidad,
            monto_pagado=monto_pagado,
            monto_reembolso=monto_reembolso,
            refund_status=refund_status,
            pms_status=pms_status,
            cancellation_reference=cancellation_reference,
            origen=origen,
            created_at=datetime.datetime.now(),
        )
        self.agregar(auditoria)
        return auditoria

    def registrar_confirmacion_pms(
        self,
        *,
        id_reserva: str,
        cancellation_reference: str | None = None,
    ) -> AuditoriaCancelacionReservaDTO:
        auditoria_base = self.obtener_ultima_por_reserva(str(id_reserva))
        referencia = cancellation_reference or (
            auditoria_base.cancellation_reference
            if auditoria_base
            else f"CXL-{str(id_reserva)[:8].upper()}"
        )

        existente_final = self.obtener_por_reserva_referencia_y_estado(
            id_reserva=str(id_reserva),
            cancellation_reference=referencia,
            estado_nuevo="CANCELADA",
        )
        if existente_final:
            return existente_final

        auditoria = AuditoriaCancelacionReservaDTO(
            id=str(uuid.uuid4()),
            id_reserva=str(id_reserva),
            id_usuario=auditoria_base.id_usuario if auditoria_base else None,
            ip_origen=auditoria_base.ip_origen if auditoria_base else None,
            motivo=auditoria_base.motivo if auditoria_base else None,
            estado_anterior="CANCELACION_EN_PROCESO",
            estado_nuevo="CANCELADA",
            politica_tipo=auditoria_base.politica_tipo if auditoria_base else None,
            dias_anticipacion=auditoria_base.dias_anticipacion if auditoria_base else None,
            porcentaje_penalidad=auditoria_base.porcentaje_penalidad if auditoria_base else None,
            monto_pagado=auditoria_base.monto_pagado if auditoria_base else None,
            monto_reembolso=auditoria_base.monto_reembolso if auditoria_base else None,
            refund_status=auditoria_base.refund_status if auditoria_base else None,
            pms_status="CONFIRMED",
            cancellation_reference=referencia,
            origen="PMS_CANCELLATION_CONFIRMED",
            created_at=datetime.datetime.now(),
        )
        self.agregar(auditoria)
        return auditoria
