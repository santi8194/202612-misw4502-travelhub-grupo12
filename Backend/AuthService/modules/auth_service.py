"""
Propósito del archivo: Lógica principal de negocio y seguridad aplicada a la autenticación.
Rol dentro del microservicio: Administra la validación de credenciales cotejadas contra el servicio de usuarios, y maneja de memoria los bloqueos de cuenta tras intentos fallidos (prevención de fuerza bruta).
"""

from datetime import datetime, timedelta
from typing import Dict, Tuple
from fastapi import HTTPException, status
from pydantic import EmailStr
from config.config import settings
from config.security import verify_password
from modules.user_service import UserService
from data.user import UserInDB

# Diccionario en memoria para la protección de fuerza bruta.
# Llave: email del usuario
# Valor: Tupla de (cantidad de intentos fallidos, fecha de fin de bloqueo)
_failed_logins: Dict[str, Tuple[int, datetime]] = {}

class AuthService:
    """
    Controlador central de lógica para autenticaciones. Abstracción independiente de los endpoints.
    """
    
    @staticmethod
    def _is_locked_out(email: str) -> bool:
        """
        Verifica si una cuenta se encuentra restringida por sobrepasar el límite de intentos de inicio de sesión.
        """
        if email in _failed_logins:
            attempts, lockout_until = _failed_logins[email]
            if lockout_until and lockout_until > datetime.utcnow():
                return True
        return False

    @staticmethod
    def _record_failed_attempt(email: str) -> None:
        """
        Lleva el conteo de los inicios de sesión erróneos. Suma al contador y define la hora de 
        bloqueo en base a la configuración global (config.py) en caso de superar el umbral.
        """
        attempts, _ = _failed_logins.get(email, (0, None))
        attempts += 1
        lockout_until = None
        
        # Lógica Crítica: Aplicación de políticas de seguridad para bloquear usuarios por el tiempo especificado.
        if attempts >= settings.MAX_LOGIN_ATTEMPTS:
            lockout_until = datetime.utcnow() + timedelta(minutes=settings.LOCKOUT_DURATION_MINUTES)
            
        _failed_logins[email] = (attempts, lockout_until)

    @staticmethod
    def _reset_attempts(email: str) -> None:
        """
        Limpia el registro de fallos al ingresar satisfactoriamente, restaurando las oportunidades
        del usuario a su valor por defecto.
        """
        if email in _failed_logins:
            del _failed_logins[email]

    @staticmethod
    def authenticate_user(email: EmailStr, password: str) -> UserInDB:
        """
        Autentica un usuario verificando su correo, previniendo bloqueos vigentes y cotejando la
        contraseña en texto plano con la versión segura traída del servicio de Usuarios.
        """
        # Chequeo previo para evitar que el ataque continúe enviando solicitudes pesadas
        if AuthService._is_locked_out(email):
            lockout_time = _failed_logins[email][1]
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Cuenta temporalmente bloqueada debido a intentos continuos fallidos. Intente luego de {lockout_time} UTC."
            )

        # Trata de emular una consulta externa
        user = UserService.get_user_by_email(email)
        
        if not user:
            AuthService._record_failed_attempt(email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Lógica Crítica: Comparación local segura entre la pass dada e internal hash
        if not verify_password(password, user.password_hash):
            AuthService._record_failed_attempt(email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Exito. Restaurar el historial de protección de la sesión de este usuario.
        AuthService._reset_attempts(email)
        return user
