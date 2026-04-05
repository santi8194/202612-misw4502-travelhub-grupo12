"""
Propósito del archivo: Módulo central para la generación de tokens y manejo de criptografía.
Rol dentro del microservicio: Centraliza el hasheo y verificación de contraseñas usando algoritmos seguros (bcrypt) y la firma electrónica de tokens JWT.
"""

from datetime import datetime, timedelta
import hashlib
import secrets
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from config.config import settings

# Instanciación del contexto de criptografía indicando que bcrypt es el esquema primario
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica que una contraseña en texto plano coincida con su versión en hash.

    Parámetros:
    - plain_password (str): contraseña ingresada por el usuario en texto plano.
    - hashed_password (str): contraseña encriptada almacenada en la base de datos.

    Retorna:
    - bool: True si la contraseña es correcta, False si no lo es.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Genera un hash seguro utilizando el algoritmo bcrypt.

    Parámetros:
    - password (str): contraseña en texto plano a encriptar.

    Retorna:
    - str: la contraseña cifrada lista para ser almacenada.
    """
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any], 
    email: str, 
    rol: str, 
    partner_id: str = None,
    session_id: str = None,
    expires_delta: timedelta = None
) -> str:
    """
    Genera un token JWT firmado de manera electrónica que encapsula los datos (claims) del usuario.

    Esta es la pieza central de la sesión stateless, inyectando los datos de identidad dentro del propio token
    y definiendo un límite de vida para mantener la seguridad.

    Parámetros:
    - subject (str o Any): ID único del usuario (usado típicamente en JWT bajo el claim 'sub').
    - email (str): correo electrónico principal del usuario.
    - rol (str): rol del usuario (ej. 'ADMIN_HOTEL' o 'USER').
    - partner_id (str, opcional): ID del partner asociado en caso de ser un rol que represente un hotel.
    - expires_delta (timedelta, opcional): tiempo que vivirá el token antes de expirar.

    Retorna:
    - str: una cadena que representa el JWT firmado.
    """
    # Lógica Crítica: Determinación del tiempo de expiración
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Payload principal que viaja adjunto con la firma digital
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "email": email,
        "rol": rol,
    }
    
    # Inclusión dinámica del partner_id solo si existe
    if partner_id:
        to_encode["partner_id"] = partner_id

    if session_id:
        to_encode["sid"] = session_id
        
    # Lógica Crítica: Firma y codificación final del JWT usando la llave secreta provista en el archivo .env
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token() -> str:
    """
    Genera un refresh token aleatorio de alta entropía para mantener sesiones seguras.
    """
    return secrets.token_urlsafe(48)


def hash_token(token: str) -> str:
    """
    Hashea el refresh token antes de persistirlo para evitar almacenarlo en texto plano.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
