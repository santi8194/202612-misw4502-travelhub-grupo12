"""
Propósito del archivo: Definición de esquemas para operaciones de autenticación.
Rol dentro del microservicio: Centraliza la estructura de los datos que los clientes envían o esperan recibir sobre procesos de ingreso como inicio de sesión y validación de tokens.
"""

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """
    Estructura de la respuesta enviada al cliente cuando se autentica exitosamente.
    Retorna el string codificado y el tipo de autorización esperada ('bearer').
    """
    access_token: str
    refresh_token: str
    token_type: str


class TokenPayload(BaseModel):
    """
    Estructura esperada al decodificar un token JWT de Cognito.
    Access tokens: sub, username, client_id, token_use.
    ID tokens: sub, email, aud, token_use.
    """
    sub: str | None = None
    email: str | None = None
    username: str | None = None
    token_use: str | None = None


class LoginRequest(BaseModel):
    """
    Cuerpo de la petición esperada para el endpoint de login via JSON directo.
    Recibe el e-mail válido y la clave en formato limpio.
    """
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """
    Cuerpo esperado para renovar una sesión activa mediante refresh token de Cognito.
    Requiere el email para calcular el SECRET_HASH necesario por Cognito.
    """
    refresh_token: str
    email: EmailStr
