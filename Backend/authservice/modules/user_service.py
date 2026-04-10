"""
Propósito del archivo: Integración e interacción simulada (Mock) con el microservicio de Usuarios.
Rol dentro del microservicio: Sirve de intermediario para obtener los registros y contraseñas (hasheadas) de un usuario dado su email sin que el AuthService dependa de la base de datos de usuarios.
"""

import uuid
from typing import Optional
from data.user import UserInDB
from config.security import get_password_hash

# Base de datos en memoria para propósitos de demostración.
# Simula lo que respondería el microservicio de Usuarios con un GET interno.
MOCK_USERS_DB = [
    {
        "id_usuario": uuid.uuid4(),
        "email": "admin@hotel.com",
        # Default password is "123456"
        "password_hash": get_password_hash("123456"), 
        "rol": "ADMIN_HOTEL",
        "partner_id": uuid.uuid4(),
    },
    {
        "id_usuario": uuid.uuid4(),
        "email": "user@hotel.com",
        "password_hash": get_password_hash("user123"), 
        "rol": "USER",
        "partner_id": None
    }
]

class UserService:
    """
    Clase de servicio que maneja la lógica de negocio para interactuar con la identidad de los usuarios.
    En un entorno real, haría peticiones HTTP/gRPC a 'Usuario Service'.
    """
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[UserInDB]:
        """
        Consulta un usuario utilizando su correo electrónico.
        Simula llamar al microservicio externo 'Usuario Service'.

        Parámetros:
        - email (str): correo del usuario a buscar.

        Retorna:
        - Optional[UserInDB]: Esquema con datos completos del usuario, incluyendo el hash de su clave, 
          o None si el usuario no existe.
        """
        for user_data in MOCK_USERS_DB:
            if user_data["email"] == email:
                return UserInDB(**user_data)
        return None
