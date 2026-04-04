"""
Propósito del archivo: Definición de esquemas de datos (Pydantic models) relacionados con el usuario.
Rol dentro del microservicio: Provee la capa de transferencia de datos (DTOs) para validar, recibir y retornar información simulada de los usuarios sin mezclar lógica de base de datos.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, UUID4


class UserBase(BaseModel):
    """
    Esquema base que agrupa la información en común de un usuario.
    Declara las propiedades esenciales de un usuario que se usa transversalmente en el servicio.
    """
    email: EmailStr
    rol: str
    partner_id: Optional[UUID4] = None


class UserInDB(UserBase):
    """
    Esquema que representa lo que retorna internamente el mock o la BD.
    Contiene campos de mayor sensibilidad como el identificador inmutable y el hash.
    """
    id_usuario: UUID4
    password_hash: str


class UserResponse(UserBase):
    """
    Esquema utilizado como máscara para retornar información del usuario al cliente.
    Filtra la información para exponerla; estrictamente sin incluir contraseñas.
    """
    id_usuario: UUID4
