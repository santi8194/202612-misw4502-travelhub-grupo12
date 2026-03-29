from seedwork.dominio.repositorios import Repositorio
from modulos.reserva.dominio.entidades import Reserva, Usuario, CategoriaHabitacion
from modulos.reserva.dominio.objetos_valor import EstadoReserva, Pax
from modulos.reserva.infraestructura.dto import ReservaDTO
from config.db import db
import uuid
import datetime

class RepositorioReservas(Repositorio):
    
    def agregar(self, entidad: Reserva):
        reserva_dto = ReservaDTO(
            id=str(entidad.id),
            id_usuario=str(entidad.usuario.id) if entidad.usuario and entidad.usuario.id else None,
            id_categoria=str(entidad.id_categoria) if entidad.id_categoria else None,
            codigo_confirmacion_ota=entidad.codigo_confirmacion_ota,
            codigo_localizador_pms=entidad.codigo_localizador_pms,
            estado=entidad.estado.value,
            fecha_check_in=entidad.fecha_check_in.isoformat() if entidad.fecha_check_in else None,
            fecha_check_out=entidad.fecha_check_out.isoformat() if entidad.fecha_check_out else None,
            ocupacion_adultos=entidad.ocupacion.adultos if entidad.ocupacion else None,
            ocupacion_ninos=entidad.ocupacion.ninos if entidad.ocupacion else None,
            ocupacion_infantes=entidad.ocupacion.infantes if entidad.ocupacion else None,
            fecha_creacion=entidad.fecha_creacion,
            fecha_actualizacion=entidad.fecha_actualizacion
        )
        db.session.add(reserva_dto)

    def actualizar(self, entidad: Reserva):
        reserva_dto = db.session.query(ReservaDTO).filter_by(id=str(entidad.id)).first()
        if reserva_dto:
            reserva_dto.id_usuario = str(entidad.usuario.id) if entidad.usuario and entidad.usuario.id else reserva_dto.id_usuario
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
        reserva_dto = db.session.query(ReservaDTO).filter_by(id=id).first()
        if not reserva_dto:
            return None

        reserva = Reserva(
            id=uuid.UUID(reserva_dto.id),
            categoria=CategoriaHabitacion(id=uuid.UUID(reserva_dto.id_categoria)) if reserva_dto.id_categoria else None,
            codigo_confirmacion_ota=reserva_dto.codigo_confirmacion_ota,
            codigo_localizador_pms=reserva_dto.codigo_localizador_pms,
            estado=EstadoReserva(reserva_dto.estado),
            fecha_check_in=datetime.date.fromisoformat(reserva_dto.fecha_check_in) if reserva_dto.fecha_check_in else None,
            fecha_check_out=datetime.date.fromisoformat(reserva_dto.fecha_check_out) if reserva_dto.fecha_check_out else None,
            ocupacion=Pax(
                adultos=reserva_dto.ocupacion_adultos or 0,
                ninos=reserva_dto.ocupacion_ninos or 0,
                infantes=reserva_dto.ocupacion_infantes or 0
            ) if any([reserva_dto.ocupacion_adultos, reserva_dto.ocupacion_ninos, reserva_dto.ocupacion_infantes]) else None,
            usuario=Usuario(id=reserva_dto.id_usuario) if reserva_dto.id_usuario else None,
            fecha_creacion=reserva_dto.fecha_creacion,
            fecha_actualizacion=reserva_dto.fecha_actualizacion
        )
        return reserva

    def obtener_todos(self) -> list[Reserva]:
        dtos = db.session.query(ReservaDTO).all()
        reservas = []
        for dto in dtos:
            reservas.append(Reserva(
                id=uuid.UUID(dto.id),
                categoria=CategoriaHabitacion(id=uuid.UUID(dto.id_categoria)) if dto.id_categoria else None,
                codigo_confirmacion_ota=dto.codigo_confirmacion_ota,
                codigo_localizador_pms=dto.codigo_localizador_pms,
                estado=EstadoReserva(dto.estado),
                fecha_check_in=datetime.date.fromisoformat(dto.fecha_check_in) if dto.fecha_check_in else None,
                fecha_check_out=datetime.date.fromisoformat(dto.fecha_check_out) if dto.fecha_check_out else None,
                ocupacion=Pax(
                    adultos=dto.ocupacion_adultos or 0,
                    ninos=dto.ocupacion_ninos or 0,
                    infantes=dto.ocupacion_infantes or 0
                ) if any([dto.ocupacion_adultos, dto.ocupacion_ninos, dto.ocupacion_infantes]) else None,
                usuario=Usuario(id=dto.id_usuario) if dto.id_usuario else None,
                fecha_creacion=dto.fecha_creacion,
                fecha_actualizacion=dto.fecha_actualizacion
            ))
        return reservas
