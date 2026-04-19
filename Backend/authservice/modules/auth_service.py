"""
Propósito del archivo: Lógica principal de autenticación delegada a AWS Cognito.
Rol dentro del microservicio: Administra la autenticación de usuarios y renovación de tokens
mediante el servicio de identidad de AWS Cognito, eliminando la verificación local de contraseñas.
"""

import base64
import hashlib
import hmac
import logging

import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, status

from config.config import settings

logger = logging.getLogger(__name__)


def _compute_secret_hash(username: str) -> str:
    """
    Calcula el SECRET_HASH requerido por Cognito cuando el App Client tiene client secret.

    Parámetros:
    - username (str): nombre de usuario (email) para el cálculo del hash.

    Retorna:
    - str: SECRET_HASH codificado en Base64.
    """
    message = username + settings.COGNITO_CLIENT_ID
    digest = hmac.new(
        settings.COGNITO_CLIENT_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return base64.b64encode(digest).decode("utf-8")


def _get_cognito_client():
    """Crea el cliente de Cognito Identity Provider de boto3."""
    return boto3.client("cognito-idp", region_name=settings.COGNITO_REGION)


def _handle_cognito_error(e: ClientError) -> None:
    """Traduce errores de Cognito a excepciones HTTP estandarizadas."""
    error_code = e.response["Error"]["Code"]

    if error_code in ("NotAuthorizedException", "UserNotFoundException"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif error_code == "UserNotConfirmedException":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario no confirmado. Verifique su correo electrónico.",
        )
    elif error_code in ("TooManyRequestsException", "LimitExceededException"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos. Intente nuevamente más tarde.",
        )
    else:
        logger.error(f"Error de Cognito: {error_code} - {e.response['Error']['Message']}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno de autenticación",
        )


class AuthService:
    """
    Controlador central de autenticación delegada a AWS Cognito.
    La verificación de contraseñas y protección contra fuerza bruta es manejada por Cognito.
    """

    @staticmethod
    def authenticate_user(email: str, password: str) -> dict:
        """
        Autentica un usuario mediante AWS Cognito usando USER_PASSWORD_AUTH.

        Parámetros:
        - email (str): correo electrónico del usuario.
        - password (str): contraseña en texto plano.

        Retorna:
        - dict: AuthenticationResult de Cognito con AccessToken, IdToken, RefreshToken, ExpiresIn, TokenType.
        """
        client = _get_cognito_client()

        auth_params = {
            "USERNAME": email,
            "PASSWORD": password,
            "SECRET_HASH": _compute_secret_hash(email),
        }

        try:
            response = client.initiate_auth(
                ClientId=settings.COGNITO_CLIENT_ID,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters=auth_params,
            )
            return response["AuthenticationResult"]
        except ClientError as e:
            _handle_cognito_error(e)

    @staticmethod
    def refresh_tokens(refresh_token: str, email: str) -> dict:
        """
        Renueva tokens mediante Cognito REFRESH_TOKEN_AUTH.

        Parámetros:
        - refresh_token (str): refresh token actual emitido por Cognito.
        - email (str): correo electrónico del usuario (necesario para SECRET_HASH).

        Retorna:
        - dict: AuthenticationResult de Cognito con AccessToken, IdToken, ExpiresIn, TokenType.
          Nota: Cognito mantiene el mismo RefreshToken.
        """
        client = _get_cognito_client()

        auth_params = {
            "REFRESH_TOKEN": refresh_token,
            "SECRET_HASH": _compute_secret_hash(email),
        }

        try:
            response = client.initiate_auth(
                ClientId=settings.COGNITO_CLIENT_ID,
                AuthFlow="REFRESH_TOKEN_AUTH",
                AuthParameters=auth_params,
            )
            return response["AuthenticationResult"]
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "NotAuthorizedException":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token inválido o expirado",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            logger.error(f"Error de Cognito al refrescar: {error_code} - {e.response['Error']['Message']}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno al renovar la sesión",
            )
