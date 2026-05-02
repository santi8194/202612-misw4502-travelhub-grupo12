"""
Propósito del archivo: Definición de esquemas para operaciones de autenticación.
Rol dentro del microservicio: Centraliza la estructura de los datos que los clientes envían o esperan recibir sobre procesos de ingreso como inicio de sesión y validación de tokens.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, EmailStr, field_validator


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


class RegisterRequest(BaseModel):
    """Solicitud de registro de un viajero en Cognito y persistencia local en authservice."""

    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    password: str

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_required_names(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Nombres y apellidos son obligatorios")
        return value

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        value = value.strip()
        # E.164: +[country code][number], hasta 15 digitos
        if not re.fullmatch(r"^\+[1-9]\d{7,14}$", value):
            raise ValueError("El número de teléfono debe estar en formato E.164, por ejemplo +573001234567")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("La contraseña debe tener mínimo 8 caracteres")
        if not re.search(r"[a-z]", value):
            raise ValueError("La contraseña debe incluir al menos una minúscula")
        if not re.search(r"[A-Z]", value):
            raise ValueError("La contraseña debe incluir al menos una mayúscula")
        if not re.search(r"\d", value):
            raise ValueError("La contraseña debe incluir al menos un número")
        if not re.search(r"[^A-Za-z0-9]", value):
            raise ValueError("La contraseña debe incluir al menos un carácter especial")
        return value


class ConfirmRegisterRequest(BaseModel):
    """Solicitud para confirmar el registro con el código enviado por Cognito."""

    email: EmailStr
    code: str

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str) -> str:
        value = value.strip()
        if not re.fullmatch(r"^\d{4,8}$", value):
            raise ValueError("El código de validación debe tener entre 4 y 8 dígitos")
        return value


class RegisterResponse(BaseModel):
    """Respuesta de registro con información del canal de entrega del código."""

    message: str
    destination: str | None = None
    delivery_medium: str | None = None


class MessageResponse(BaseModel):
    """Respuesta de confirmación simple para operaciones exitosas."""

    message: str
