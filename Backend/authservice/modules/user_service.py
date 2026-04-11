"""
Propósito del archivo: Integración e interacción simulada (Mock) con el microservicio de Usuarios.
Rol dentro del microservicio: Sirve de intermediario para obtener los registros y contraseñas de un usuario dado su email desde la base de datos PostgreSQL del microservicio.
"""

from typing import Optional
from sqlalchemy import select
from data.user import UserInDB
from infrastructure.database import new_session
from infrastructure.models import UserModel


def _to_user_in_db(user: UserModel) -> UserInDB:
    return UserInDB(
        id_usuario=user.id_usuario,
        email=user.email,
        password_hash=user.password_hash,
        rol=user.rol,
        partner_id=user.partner_id,
    )


class UserService:
    """
    Clase de servicio que maneja la lógica de negocio para interactuar con la identidad de los usuarios.
    Consulta la base de datos PostgreSQL para obtener información de usuarios.
    """
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[UserInDB]:
        """
        Consulta un usuario utilizando su correo electrónico desde PostgreSQL.

        Parámetros:
        - email (str): correo del usuario a buscar.

        Retorna:
        - Optional[UserInDB]: Esquema con datos completos del usuario, incluyendo el hash de su clave, 
          o None si el usuario no existe.
        """
        with new_session() as session:
            statement = select(UserModel).where(UserModel.email == str(email))
            user = session.execute(statement).scalar_one_or_none()

            if user is None:
                return None

            return _to_user_in_db(user)
