from enum import Enum
from seedwork.dominio.objetos_valor import ObjetoValor
from dataclasses import dataclass

class EstadoReserva(Enum):
    HOLD = "HOLD"
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    EXPIRADA = "EXPIRADA"

@dataclass(frozen=True)
class Pax(ObjetoValor):
    adultos: int = 0
    ninos: int = 0
    infantes: int = 0
