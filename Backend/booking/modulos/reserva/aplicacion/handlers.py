import logging

logger = logging.getLogger(__name__)

from seedwork.aplicacion.comandos import Handler
from modulos.reserva.aplicacion.comandos import (
    CrearReservaHold, FormalizarReserva, 
    ConfirmarReservaLocalCmd, CancelarReservaLocalCmd, ExpirarReserva
)
from modulos.reserva.dominio.entidades import Reserva, Usuario, CategoriaHabitacion
from modulos.reserva.dominio.objetos_valor import EstadoReserva, Pax
from modulos.reserva.dominio.eventos import (
    ReservaConfirmadaEvt, FallaActualizacionLocalEvt
)
from modulos.reserva.infraestructura.catalog_client import CatalogServiceClient
from modulos.reserva.infraestructura.repositorios import RepositorioReservas
from config.uow import UnidadTrabajoHibrida
import uuid
import datetime

class CrearReservaHoldHandler(Handler):
    def __init__(self, repositorio: RepositorioReservas, uow: UnidadTrabajoHibrida, catalog_client: CatalogServiceClient | None = None):
        self.repositorio = repositorio
        self.uow = uow
        self.catalog_client = catalog_client or CatalogServiceClient()
    
    def handle(self, comando: CrearReservaHold) -> uuid.UUID:
        fecha_check_in = datetime.date.fromisoformat(comando.fecha_check_in) if comando.fecha_check_in else None
        fecha_check_out = datetime.date.fromisoformat(comando.fecha_check_out) if comando.fecha_check_out else None

        if not fecha_check_in or not fecha_check_out:
            raise ValueError("Las fechas de check-in y check-out son obligatorias")
        if fecha_check_out <= fecha_check_in:
            raise ValueError("La fecha de check-out debe ser posterior a la fecha de check-in")

        with self.uow:
            reserva_activa = self.repositorio.obtener_activa_por_usuario_categoria_fechas(
                id_usuario=str(comando.id_usuario),
                id_categoria=str(comando.id_categoria),
                fecha_check_in=fecha_check_in,
                fecha_check_out=fecha_check_out,
            )

        if reserva_activa:
            logger.info(f"Reserva activa existente encontrada para usuario/categoria/fechas: {reserva_activa.id}")
            return reserva_activa.id

        original_inventory_items = self.catalog_client.reserve_inventory(
            str(comando.id_categoria),
            fecha_check_in,
            fecha_check_out,
        )

        try:
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
                    fecha_check_in=fecha_check_in,
                    fecha_check_out=fecha_check_out,
                    ocupacion=ocupacion,
                    usuario=usuario
                )

                self.uow.agregar_eventos(reserva.eventos)
                self.repositorio.agregar(reserva)

                self.uow.commit()
                logger.info(f"Reserva_Hold persistida y evento despachado: {reserva.id}")
            return reserva.id
        except Exception:
            self.catalog_client.restore_inventory(str(comando.id_categoria), original_inventory_items)
            raise

class FormalizarReservaHandler(Handler):
    def __init__(self, repositorio: RepositorioReservas, uow: UnidadTrabajoHibrida):
        self.repositorio = repositorio
        self.uow = uow
    
    def handle(self, comando: FormalizarReserva) -> bool:
        with self.uow:
            reserva: Reserva = self.repositorio.obtener_por_id(str(comando.id_reserva))
            if not reserva:
                raise ValueError(f"No se encontró la reserva con ID: {comando.id_reserva}")
            
            reserva.formalizar_y_pagar(monto=comando.monto, moneda=comando.moneda)
            
            self.uow.agregar_eventos(reserva.eventos)
            self.repositorio.actualizar(reserva)
            
            # La UoW inserta en BD y publica el ReservaPendienteEvt
            self.uow.commit() 
            logger.info(f"Reserva {reserva.id} formalizada (PENDIENTE) y evento despachado.")
        return True


class ObtenerReservaPorIdHandler(Handler):
    def __init__(self, repositorio: RepositorioReservas, uow: UnidadTrabajoHibrida):
        self.repositorio = repositorio
        self.uow = uow

    def handle(self, id_reserva: uuid.UUID) -> Reserva | None:
        with self.uow:
            return self.repositorio.obtener_por_id(str(id_reserva))


class ExpirarReservaHandler(Handler):
    def __init__(self, repositorio: RepositorioReservas, uow: UnidadTrabajoHibrida, catalog_client: CatalogServiceClient | None = None):
        self.repositorio = repositorio
        self.uow = uow
        self.catalog_client = catalog_client or CatalogServiceClient()

    def handle(self, comando: ExpirarReserva) -> bool:
        with self.uow:
            reserva: Reserva = self.repositorio.obtener_por_id(str(comando.id_reserva))
            if not reserva:
                raise ValueError(f"No se encontró la reserva con ID: {comando.id_reserva}")

            reserva.expirar_reserva()

            if reserva.id_categoria and reserva.fecha_check_in and reserva.fecha_check_out:
                self.catalog_client.release_inventory(
                    str(reserva.id_categoria),
                    reserva.fecha_check_in,
                    reserva.fecha_check_out,
                )

            self.uow.agregar_eventos(reserva.eventos)
            self.repositorio.actualizar(reserva)
            self.uow.commit()
            logger.info(f"Reserva {reserva.id} marcada como EXPIRADA.")
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
    def __init__(self, repositorio: RepositorioReservas, uow: UnidadTrabajoHibrida, catalog_client: CatalogServiceClient | None = None):
        self.repositorio = repositorio
        self.uow = uow
        self.catalog_client = catalog_client or CatalogServiceClient()
    
    def handle(self, comando: CancelarReservaLocalCmd) -> FallaActualizacionLocalEvt:
        with self.uow:
            reserva: Reserva = self.repositorio.obtener_por_id(str(comando.id_reserva))
            if not reserva:
                raise ValueError(f"No se encontró la reserva con ID: {comando.id_reserva}")

            should_release_inventory = (
                reserva.estado not in (EstadoReserva.CANCELADA, EstadoReserva.EXPIRADA)
                and reserva.id_categoria
                and reserva.fecha_check_in
                and reserva.fecha_check_out
            )
            if should_release_inventory:
                self.catalog_client.release_inventory(
                    str(reserva.id_categoria),
                    reserva.fecha_check_in,
                    reserva.fecha_check_out,
                )
            
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


class ObtenerReservasPorUsuarioHandler(Handler):
    def __init__(self, repositorio: RepositorioReservas, uow: UnidadTrabajoHibrida):
        self.repositorio = repositorio
        self.uow = uow

    def handle(self, query) -> list[Reserva]:
        with self.uow:
            return self.repositorio.obtener_por_usuario(str(query.id_usuario))
