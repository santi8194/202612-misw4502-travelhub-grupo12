from dataclasses import dataclass
import uuid


@dataclass
class ObtenerReservasPorUsuario:
    id_usuario: uuid.UUID
