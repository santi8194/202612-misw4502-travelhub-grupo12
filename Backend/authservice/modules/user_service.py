"""
Propósito del archivo: Integración con la base de datos de usuarios.
Rol dentro del microservicio: Sirve de intermediario para obtener los registros y contraseñas (hasheadas) de un usuario desde PostgreSQL.
"""

from typing import Optional
from data.user import UserInDB
from infrastructure.database import SessionLocal
from infrastructure.models import User
import logging

logger = logging.getLogger(__name__)


class UserService:
    """
    Clase de servicio que maneja la lógica de negocio para interactuar con la identidad de los usuarios.
    Consulta la base de datos PostgreSQL para obtener información de usuarios.
    """
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[UserInDB]:
        """
        Consulta un usuario utilizando su correo electrónico desde la base de datos.

        Parámetros:
        - email (str): correo del usuario a buscar.

        Retorna:
        - Optional[UserInDB]: Esquema con datos completos del usuario, incluyendo el hash de su clave, 
          o None si el usuario no existe.
        """
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                logger.warning(f"Usuario no encontrado: {email}")
                return None
            
            # Obtener el rol principal del usuario (si existe)
            rol = "USER"  # rol por defecto
            if user.roles:
                rol = user.roles[0].name
            
            # Convertir el modelo ORM a UserInDB
            return UserInDB(
                id_usuario=user.id,
                email=user.email,
                password_hash=user.password_hash,
                rol=rol,
                partner_id=user.partner_id
            )
        except Exception as e:
            logger.error(f"Error al consultar usuario {email}: {str(e)}")
            return None
        finally:
            db.close()
