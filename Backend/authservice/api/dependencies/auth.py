"""
Propósito del archivo: Manejo de inyección de dependencias (DI) de FastAPI para autorización.
Rol dentro del microservicio: Provee funciones estándar reutilizables que se incrustan en las rutas que necesitan seguridad.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from config.config import settings
from data.auth import TokenPayload
from data.user import UserResponse
from modules.session_service import SessionService
from modules.user_service import UserService

# Middleware de seguridad que le indica a la interfaz tipo Swagger de dónde tomar y usar tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    """
    Resolutor de dependencia que desencripta el JWT, verifica firmas y su caducidad, y devuelve
    la identidad del usuario asociado si y solo si los checks de seguridad son exitosos.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se han podido validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Lógica Crítica: Validación de Token
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # Transformando la carga útil desencriptada al modelo local para verificar formato
        token_data = TokenPayload(**payload)
        
        if token_data.sub is None or token_data.sid is None:
            raise credentials_exception
    except (JWTError, ValidationError):
        # Captura errores desde firmas mal configuradas hasta vencimiento (exp)
        raise credentials_exception
        
    # Obtiene al usuario nuevamente para asegurarse de que el usuario todavía existe (integridad temporal).
    user = UserService.get_user_by_email(token_data.email)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado en los registros")

    if not SessionService.validate_session(token_data.sid, user.id_usuario, touch_activity=True):
        raise credentials_exception
        
    return UserResponse(
        id_usuario=user.id_usuario,
        email=user.email,
        rol=user.rol,
        partner_id=user.partner_id
    )
