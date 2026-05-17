from dataclasses import dataclass
import uuid
from seedwork.aplicacion.comandos import Comando


# --- COMANDOS: Acción Hacia Adelante ---
@dataclass
class ProcesarPagoCmd(Comando):
    id_reserva: uuid.UUID
    monto: float

@dataclass
class ConfirmarReservaPmsCmd(Comando):
    id_reserva: uuid.UUID
    id_categoria: uuid.UUID
    id_usuario: uuid.UUID
    fecha_check_in: str
    fecha_check_out: str

@dataclass
class SolicitarAprobacionManualCmd(Comando):
    id_reserva: uuid.UUID
    id_categoria: uuid.UUID

@dataclass
class MarcarSagaEsperandoVoucherCmd(Comando):
    id_reserva: uuid.UUID = None


# --- COMANDOS: Compensación (Rollback LIFO) ---
@dataclass
class CancelarReservaPmsCmd(Comando):
    id_reserva: uuid.UUID
    id_categoria: uuid.UUID

@dataclass
class ReversarPagoCmd(Comando):
    id_reserva: uuid.UUID
    monto: float

@dataclass
class RechazarReservaCmd(Comando):  # Detonante externo manual
    id_reserva: uuid.UUID = None
