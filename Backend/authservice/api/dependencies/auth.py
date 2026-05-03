"""
Propósito del archivo: Manejo de inyección de dependencias (DI) de FastAPI para autorización.
Rol dentro del microservicio: Provee funciones estándar reutilizables que se incrustan en las rutas que necesitan seguridad.
Valida tokens JWT emitidos por AWS Cognito usando claves públicas JWK (RS256).
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from config.config import settings
from config.security import validate_cognito_token
from data.user import UserResponse
from modules.user_service import UserService

# Middleware de seguridad que le indica a la interfaz tipo Swagger de dónde tomar y usar tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    """
    Resolutor de dependencia que valida el token JWT de Cognito y retorna la identidad del usuario.
    Extrae el email del token (campo 'email' en ID tokens o 'username' en access tokens)
    y consulta la base de datos para obtener los datos completos del usuario.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se han podido validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = validate_cognito_token(token)
        # Access tokens usan 'username' (sub de Cognito). ID tokens usan 'email'.
        username = payload.get("username")
        email = payload.get("email")
        if username is None and email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    #imprimir username
    print(f"Username: {username}, Email: {email}")
    # Buscar primero por username (access tokens de Cognito); fallback a email (ID tokens)
    user = UserService.get_user_by_username(username) if username else None
    if not user and email:
        user = UserService.get_user_by_email(email)

    lookup_key = username or email
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado en los registros: " + lookup_key)

    return UserResponse(
        id_usuario=user.id_usuario,
        email=user.email,
        full_name=user.full_name,
        rol=user.rol,
        partner_id=user.partner_id
    )
