"""
Propósito del archivo: Integración con la base de datos de usuarios.
Rol dentro del microservicio: Sirve de intermediario para obtener los registros y contraseñas (hasheadas) de un usuario desde PostgreSQL.
"""

from datetime import datetime
from typing import Optional
from data.user import UserInDB
from infrastructure.database import SessionLocal
from infrastructure.models import Role, User
import logging

logger = logging.getLogger(__name__)


class UserService:
    """
    Clase de servicio que maneja la lógica de negocio para interactuar con la identidad de los usuarios.
    Consulta la base de datos PostgreSQL para obtener información de usuarios.
    """
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[UserInDB]:
        """
        Consulta un usuario utilizando su username de Cognito desde la base de datos.

        Parámetros:
        - username (str): username del usuario a buscar (campo 'username' del access token de Cognito).

        Retorna:
        - Optional[UserInDB]: Esquema con datos completos del usuario, o None si no existe.
        """
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == username).first()
            if not user:
                logger.warning(f"Usuario no encontrado por username: {username}")
                return None

            rol = "USER"
            if user.roles:
                rol = user.roles[0].name

            return UserInDB(
                id_usuario=user.id,
                email=user.email,
                password_hash=user.password_hash,
                rol=rol,
                partner_id=user.partner_id
            )
        except Exception as e:
            logger.error(f"Error al consultar usuario por username {username}: {str(e)}")
            return None
        finally:
            db.close()

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

    @staticmethod
    def create_or_update_registered_user(
        *,
        email: str,
        full_name: str,
        username: str,
        active: bool,
    ) -> Optional[UserInDB]:
        """
        Crea o actualiza un usuario local sincronizado con Cognito y garantiza el rol USER.

        Parámetros:
        - email (str): correo del usuario.
        - full_name (str): nombre completo del usuario.
        - username (str): username de Cognito (en este flujo usamos el email).
        - active (bool): estado local del usuario según etapa de confirmación.

        Retorna:
        - Optional[UserInDB]: Usuario sincronizado o None ante error.
        """
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if user is None:
                user = User(
                    email=email,
                    username=username,
                    full_name=full_name,
                    # Cognito gestiona la contraseña, se almacena marcador por compatibilidad de esquema histórico.
                    password_hash="COGNITO_MANAGED",
                    is_active="true" if active else "false",
                )
                db.add(user)
            else:
                user.full_name = full_name
                user.username = username
                user.is_active = "true" if active else "false"
                if not user.password_hash:
                    user.password_hash = "COGNITO_MANAGED"
                user.updated_at = datetime.utcnow()

            role_user = db.query(Role).filter(Role.name == "USER").first()
            if role_user and role_user not in user.roles:
                user.roles.append(role_user)

            db.commit()
            db.refresh(user)

            rol = user.roles[0].name if user.roles else "USER"
            return UserInDB(
                id_usuario=user.id,
                email=user.email,
                password_hash=user.password_hash,
                rol=rol,
                partner_id=user.partner_id,
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Error al crear/actualizar usuario registrado {email}: {str(e)}")
            return None
        finally:
            db.close()

    @staticmethod
    def activate_user(email: str) -> bool:
        """Marca un usuario local como activo al confirmar su código de registro."""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                return False

            user.is_active = "true"
            user.updated_at = datetime.utcnow()
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error al activar usuario {email}: {str(e)}")
            return False
        finally:
            db.close()
