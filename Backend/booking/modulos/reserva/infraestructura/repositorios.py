from modulos.reserva.infraestructura.mapeadores_dto import MapeadorReservaDTO
from seedwork.dominio.repositorios import Repositorio
from modulos.reserva.dominio.entidades import Reserva, Usuario, CategoriaHabitacion
from modulos.reserva.dominio.objetos_valor import EstadoReserva, Pax
from modulos.reserva.infraestructura.dto import ReservaDTO
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
