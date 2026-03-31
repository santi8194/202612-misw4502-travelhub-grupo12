import logging

logger = logging.getLogger(__name__)

from seedwork.aplicacion.comandos import Handler
from modulos.reserva.aplicacion.comandos import (
    CrearReservaHold, FormalizarReserva, 
    ConfirmarReservaLocalCmd, CancelarReservaLocalCmd
)
from modulos.reserva.dominio.entidades import Reserva, Usuario, CategoriaHabitacion
from modulos.reserva.dominio.objetos_valor import EstadoReserva, Pax
from modulos.reserva.dominio.eventos import (
    ReservaConfirmadaEvt, FallaActualizacionLocalEvt
)
from modulos.reserva.infraestructura.repositorios import RepositorioReservas
from config.uow import UnidadTrabajoHibrida
import uuid
import datetime

class CrearReservaHoldHandler(Handler):
    def __init__(self, repositorio: RepositorioReservas, uow: UnidadTrabajoHibrida):
        self.repositorio = repositorio
        self.uow = uow
    
    def handle(self, comando: CrearReservaHold) -> uuid.UUID:
        with self.uow:
            reserva = Reserva(id=uuid.uuid4())
            id_categoria = comando.id_categoria
            ocupacion = None
            if comando.ocupacion:
                ocupacion = Pax(
                    adultos=int(comando.ocupacion.get('adultos', 0)),
                    ninos=int(comando.ocupacion.get('ninos', 0)),
                    infantes=int(comando.ocupacion.get('infantes', 0))
                )

            usuario = None
            if comando.id_usuario or comando.usuario_nombre or comando.usuario_email:
                usuario = Usuario(
                    id=str(comando.id_usuario) if comando.id_usuario else str(uuid.uuid4()),
                    nombre=comando.usuario_nombre,
                    email=comando.usuario_email
                )

            reserva.crear_reserva(
                id_categoria=id_categoria,
                codigo_confirmacion_ota=comando.codigo_confirmacion_ota,
                codigo_localizador_pms=comando.codigo_localizador_pms,
                estado=EstadoReserva(comando.estado) if comando.estado else None,
                fecha_check_in=datetime.date.fromisoformat(comando.fecha_check_in) if comando.fecha_check_in else None,
                fecha_check_out=datetime.date.fromisoformat(comando.fecha_check_out) if comando.fecha_check_out else None,
                ocupacion=ocupacion,
                usuario=usuario
            )
            
            self.uow.agregar_eventos(reserva.eventos)
            self.repositorio.agregar(reserva)
            
            self.uow.commit() 
            logger.info(f"Reserva_Hold persistida y evento despachado: {reserva.id}")
        return reserva.id

class FormalizarReservaHandler(Handler):
    def __init__(self, repositorio: RepositorioReservas, uow: UnidadTrabajoHibrida):
        self.repositorio = repositorio
        self.uow = uow
    
    def handle(self, comando: FormalizarReserva) -> bool:
        with self.uow:
            reserva: Reserva = self.repositorio.obtener_por_id(str(comando.id_reserva))
            if not reserva:
                raise ValueError(f"No se encontró la reserva con ID: {comando.id_reserva}")
            
            reserva.formalizar_y_pagar()
            
            self.uow.agregar_eventos(reserva.eventos)
            self.repositorio.actualizar(reserva)
            
            # La UoW inserta en BD y publica el ReservaPendienteEvt
            self.uow.commit() 
            logger.info(f"Reserva {reserva.id} formalizada (PENDIENTE) y evento despachado.")
        return True

class ConfirmarReservaLocalHandler(Handler):
    def __init__(self, repositorio: RepositorioReservas, uow: UnidadTrabajoHibrida):
        self.repositorio = repositorio
        self.uow = uow
    
    def handle(self, comando: ConfirmarReservaLocalCmd) -> ReservaConfirmadaEvt:
        with self.uow:
            reserva: Reserva = self.repositorio.obtener_por_id(str(comando.id_reserva))
            if not reserva:
                raise ValueError(f"No se encontró la reserva con ID: {comando.id_reserva}")
            
            reserva.confirmar_reserva()
            
            reserva.eventos.clear() 
            evento_local = ReservaConfirmadaEvt(
                id_reserva=reserva.id, 
                fecha_actualizacion=datetime.datetime.now()
            )
            reserva.agregar_evento(evento_local)
            
            self.uow.agregar_eventos(reserva.eventos)
            self.repositorio.actualizar(reserva)
            self.uow.commit() 
            logger.info(f"✅ [HANDLER LOCAL] Reserva {reserva.id} CONFIRMADA localmente.")
        return evento_local

class CancelarReservaLocalHandler(Handler):
    def __init__(self, repositorio: RepositorioReservas, uow: UnidadTrabajoHibrida):
        self.repositorio = repositorio
        self.uow = uow
    
    def handle(self, comando: CancelarReservaLocalCmd) -> FallaActualizacionLocalEvt:
        with self.uow:
            reserva: Reserva = self.repositorio.obtener_por_id(str(comando.id_reserva))
            if not reserva:
                raise ValueError(f"No se encontró la reserva con ID: {comando.id_reserva}")
            
            reserva.cancelar_reserva()
            
            reserva.eventos.clear()
            evento_falla = FallaActualizacionLocalEvt(
                id_reserva=reserva.id, 
                fecha_actualizacion=datetime.datetime.now()
            )
            reserva.agregar_evento(evento_falla)
            
            self.uow.agregar_eventos(reserva.eventos)
            self.repositorio.actualizar(reserva)
            self.uow.commit() 
            logger.info(f"❌ [HANDLER LOCAL] Reserva {reserva.id} CANCELADA localmente por compensación.")
        return evento_falla
