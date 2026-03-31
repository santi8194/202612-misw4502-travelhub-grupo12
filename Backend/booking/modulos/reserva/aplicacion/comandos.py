from dataclasses import dataclass
import uuid
from seedwork.aplicacion.comandos import Comando

@dataclass
class CrearReservaHold(Comando):
    id_usuario: uuid.UUID
    id_categoria: uuid.UUID = None
    codigo_confirmacion_ota: str = None
    codigo_localizador_pms: str = None
    estado: str = None
    fecha_check_in: str = None
    fecha_check_out: str = None
    ocupacion: dict = None
    usuario_nombre: str = None
    usuario_email: str = None

@dataclass
class FormalizarReserva(Comando):
    id_reserva: uuid.UUID
    fecha_check_in: str = None
    fecha_check_out: str = None

@dataclass
class ConfirmarReservaLocalCmd(Comando):
    id_reserva: uuid.UUID

@dataclass
class CancelarReservaLocalCmd(Comando):
    id_reserva: uuid.UUID
