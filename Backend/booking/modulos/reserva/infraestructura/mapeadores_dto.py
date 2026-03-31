from datetime import datetime, date
import uuid

from seedwork.dominio.repositorios import Mapeador
from modulos.reserva.dominio.entidades import CategoriaHabitacion, Reserva, Usuario
from modulos.reserva.dominio.objetos_valor import EstadoReserva, Pax
from modulos.reserva.infraestructura.dto import ReservaDTO


class MapeadorReservaDTO(Mapeador):
    """
    Convierte entre la Entidad de dominio Reserva y su representación
    en base de datos ReservaDTO.
    """

    def obtener_tipo(self) -> type:
        return Reserva

    def entidad_a_dto(self, entidad: Reserva) -> ReservaDTO:
        return ReservaDTO(
            id=str(entidad.id),
            usuario=str(entidad.usuario.id) if entidad.usuario else None,
            id_categoria=str(entidad.id_categoria),
            codigo_confirmacion_ota=entidad.codigo_confirmacion_ota,
            codigo_localizador_pms=entidad.codigo_localizador_pms,
            estado=entidad.estado.value if entidad.estado else None,
            fecha_check_in=entidad.fecha_check_in.isoformat() if entidad.fecha_check_in else None,
            fecha_check_out=entidad.fecha_check_out.isoformat() if entidad.fecha_check_out else None,
            ocupacion_adultos=entidad.ocupacion.adultos if entidad.ocupacion else None,
            ocupacion_ninos=entidad.ocupacion.ninos if entidad.ocupacion else None,
            ocupacion_infantes=entidad.ocupacion.infantes if entidad.ocupacion else None,
            fecha_creacion=entidad.fecha_creacion,
            fecha_actualizacion=entidad.fecha_actualizacion 
        )

    def dto_a_entidad(self, dto: ReservaDTO) -> Reserva:
        return Reserva(
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
        )
