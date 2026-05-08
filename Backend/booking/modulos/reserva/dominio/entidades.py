from __future__ import annotations
from dataclasses import dataclass, field
import datetime
import uuid

from seedwork.dominio.objetos_valor import ObjetoValor
from seedwork.dominio.entidades import AgregacionRaiz, Entidad
from modulos.reserva.dominio.objetos_valor import EstadoReserva, Pax
from modulos.reserva.dominio.eventos import (
    ReservaIniciada,
    ReservaPendiente,
    ReservaConfirmada,
    ReservaCancelada,
    ReservaExpirada
)
@dataclass(frozen=True)
class Direccion(ObjetoValor):
    ciudad: str = None
    pais: str = None
    lat: float = None
    lng: float = None

@dataclass(frozen=True)
class Dinero(ObjetoValor):
    monto: float = 0.0
    moneda: str = "COP"

@dataclass(frozen=True)
class Regla(ObjetoValor):
    dias_anticipacion: int = 0
    porcentaje_penalidad: float = 0.0

@dataclass
class Propiedad(Entidad):
    nombre: str = None
    estrellas: int = 0
    ubicacion: Direccion = None
    porcentaje_impuesto: float = 0.0



@dataclass
class CategoriaHabitacion(Entidad):
    codigo_mapeo_pms: str = None
    nombre_comercial: str = None
    descripcion: str = None
    precio_base: Dinero = None
    capacidad_pax: int = 0
    politica_cancelacion: Regla = None
    propiedad: Propiedad = None

@dataclass
class Usuario(Entidad):
    nombre: str = None
    email: str = None



@dataclass
class Reserva(AgregacionRaiz):
    id_categoria: CategoriaHabitacion = field(default=None)
    codigo_confirmacion_ota: str = field(default=None)
    codigo_localizador_pms: str = field(default=None)
    estado: EstadoReserva = field(default=EstadoReserva.HOLD)
    fecha_check_in: datetime.date = field(default=None)
    fecha_check_out: datetime.date = field(default=None)
    ocupacion: Pax = field(default=None)
    usuario: Usuario = field(default=None)

    fecha_creacion: datetime.datetime = field(default_factory=datetime.datetime.now)
    fecha_actualizacion: datetime.datetime = field(default_factory=datetime.datetime.now)

    def __post_init__(self):
        super().__post_init__()


    @property
    def id_reserva(self) -> uuid.UUID:
        return self.id

    @property
    def id_categoria(self) -> uuid.UUID:
        return self.categoria.id if self.categoria else None

    @id_categoria.setter
    def id_categoria(self, value: uuid.UUID):
        if value is None:
            self.categoria = None
        else:
            self.categoria = CategoriaHabitacion(id=value)

    def asignar_usuario(self, usuario: Usuario):
        self.usuario = usuario


    def actualizar_estado(self, nuevo_estado: EstadoReserva):
        self.estado = nuevo_estado
        self.fecha_actualizacion = datetime.datetime.now()

    def crear_reserva(
        self,
        id_categoria: CategoriaHabitacion = None,
        codigo_confirmacion_ota: str = None,
        codigo_localizador_pms: str = None,
        estado: EstadoReserva = EstadoReserva.HOLD,
        fecha_check_in: datetime.date = None,
        fecha_check_out: datetime.date = None,
        ocupacion: Pax = None,
        usuario: Usuario = None
    ):
        self.id_categoria = id_categoria
        self.codigo_confirmacion_ota = codigo_confirmacion_ota
        self.codigo_localizador_pms = codigo_localizador_pms
        self.estado = estado or EstadoReserva.HOLD
        self.fecha_check_in = fecha_check_in
        self.fecha_check_out = fecha_check_out
        self.ocupacion = ocupacion
        self.usuario = usuario
        self.fecha_creacion = datetime.datetime.now()
        self.fecha_actualizacion = self.fecha_creacion

        self.agregar_evento(ReservaIniciada(
            id_reserva=self.id,
            id_usuario=uuid.UUID(self.usuario.id) if self.usuario and self.usuario.id else None,
            id_categoria=self.id_categoria,
            fecha_creacion=self.fecha_creacion
        ))

    def formalizar_y_pagar(self, monto: float = None, moneda: str = "COP"):
        if self.estado != EstadoReserva.HOLD:
            raise ValueError("La reserva debe estar en estado HOLD para ser formalizada")

        self.estado = EstadoReserva.PENDIENTE
        self.fecha_actualizacion = datetime.datetime.now()
        self.agregar_evento(ReservaPendiente(
            id_reserva=self.id,
            id_usuario=uuid.UUID(self.usuario.id) if self.usuario and self.usuario.id else None,
            id_categoria=self.id_categoria,
            monto=monto,
            moneda=moneda,
            fecha_reserva=self.fecha_check_in.isoformat() if self.fecha_check_in else None
        ))

    def confirmar_reserva(self):
        if self.estado != EstadoReserva.PENDIENTE:
            raise ValueError("La reserva debe estar en PENDIENTE para ser confirmada")

        self.estado = EstadoReserva.CONFIRMADA
        self.fecha_actualizacion = datetime.datetime.now()
        self.agregar_evento(ReservaConfirmada(
            id_reserva=self.id,
            fecha_actualizacion=self.fecha_actualizacion
        ))

    def cancelar_reserva(self):
        self.estado = EstadoReserva.CANCELADA
        self.fecha_actualizacion = datetime.datetime.now()
        self.agregar_evento(ReservaCancelada(
            id_reserva=self.id,
            fecha_actualizacion=self.fecha_actualizacion
        ))

    def expirar_reserva(self):
        if self.estado != EstadoReserva.HOLD:
            raise ValueError("La reserva debe estar en HOLD para marcarse como EXPIRADA")

        self.estado = EstadoReserva.EXPIRADA
        self.fecha_actualizacion = datetime.datetime.now()
        self.agregar_evento(ReservaExpirada(
            id_reserva=self.id,
            fecha_actualizacion=self.fecha_actualizacion
        ))
