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
    Estructura esperada por el servicio al intentar decodificar y extraer validaciones de un JWT recibido.
    Contiene la misma información original que se inyectó al llamarse a `create_access_token`.
    """
    sub: str | None = None
    email: str | None = None
    rol: str | None = None
    partner_id: str | None = None
    sid: str | None = None


class LoginRequest(BaseModel):
    """
    Cuerpo de la petición esperada para el endpoint de login via JSON directo.
    Recibe el e-mail válido y la clave en formato limpio.
    """
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """
    Cuerpo esperado para renovar una sesión activa mediante refresh token.
    """
    refresh_token: str
