"""
Propósito del archivo: Validación de tokens JWT emitidos por AWS Cognito.
Rol dentro del microservicio: Centraliza la descarga y caché de las claves públicas JWK de Cognito
y la verificación criptográfica de los tokens de acceso (RS256).
"""

import json
from urllib.request import urlopen

from jose import jwt, JWTError
from config.config import settings

# Caché en memoria de las claves JWK de Cognito
_jwk_keys: list | None = None


def _get_cognito_jwk_keys() -> list:
    """
    Descarga y cachea las claves JWK públicas del User Pool de Cognito.
    Se utiliza para verificar la firma RS256 de los tokens emitidos.
    """
    global _jwk_keys
    if _jwk_keys is None:
        response = urlopen(settings.COGNITO_JWK_URL)
        _jwk_keys = json.loads(response.read())["keys"]
    return _jwk_keys


def validate_cognito_token(token: str) -> dict:
    """
    Valida un token JWT emitido por AWS Cognito usando las claves públicas JWK (RS256).

    Parámetros:
    - token (str): JWT emitido por Cognito (access_token o id_token).

    Retorna:
    - dict: Payload decodificado del token.

    Lanza:
    - JWTError: Si el token es inválido, expirado o no puede ser verificado.
    """
    keys = _get_cognito_jwk_keys()

    # Obtener el kid del header del token para buscar la clave correcta
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")

    key = None
    for k in keys:
        if k["kid"] == kid:
            key = k
            break

    if key is None:
        raise JWTError("Clave pública JWK no encontrada para el token")

    # Cognito access tokens no incluyen claim 'aud', solo ID tokens lo incluyen
    payload = jwt.decode(
        token,
        key,
        algorithms=["RS256"],
        issuer=settings.COGNITO_ISSUER,
        options={"verify_aud": False},
    )

    # Verificar que el token sea de tipo access o id
    token_use = payload.get("token_use")
    if token_use not in ("access", "id"):
        raise JWTError("Tipo de token no reconocido")

    return payload
