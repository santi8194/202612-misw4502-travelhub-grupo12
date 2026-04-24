"""
Propósito del archivo: Definición y exposición de las APIs REST correspondientes al manejo de credenciales (Rutas).
Rol dentro del microservicio: Contiene los controllers HTTP para logueos, chequeo de estatus del token y renovación.
La autenticación y gestión de tokens es delegada a AWS Cognito.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from data.auth import Token, LoginRequest, RefreshTokenRequest
from data.user import UserResponse
from modules.auth_service import AuthService
from api.dependencies.auth import get_current_user

router = APIRouter()


@router.post("/login", response_model=Token)
def login(request: LoginRequest) -> Any:
    """
    Endpoint: Ingresar a la aplicación intercambiando JSON de credenciales por tokens de Cognito.
    """
    result = AuthService.authenticate_user(email=request.email, password=request.password)
    return {
        "access_token": result["AccessToken"],
        "refresh_token": result["RefreshToken"],
        "token_type": "bearer",
    }


@router.post("/login/form", response_model=Token)
def login_form(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    Endpoint: Ingresar a la aplicación intercambiando Form-Data para sistemas integrados compatibles o Swagger UI.
    """
    result = AuthService.authenticate_user(email=form_data.username, password=form_data.password)
    return {
        "access_token": result["AccessToken"],
        "refresh_token": result["RefreshToken"],
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: UserResponse = Depends(get_current_user)) -> Any:
    """
    Endpoint: Obtiene el contexto general y la meta-data del usuario logueado en tiempo real.
    """
    return current_user


@router.post("/refresh", response_model=Token)
def refresh_token(request: RefreshTokenRequest) -> Any:
    """
    Endpoint: Renueva tokens usando el refresh token de Cognito.
    Cognito mantiene el mismo refresh token y emite nuevos access/id tokens.
    """
    result = AuthService.refresh_tokens(
        refresh_token=request.refresh_token,
        email=request.email,
    )
    # Cognito REFRESH_TOKEN_AUTH no retorna un nuevo RefreshToken, se mantiene el original
    return {
        "access_token": result["AccessToken"],
        "refresh_token": request.refresh_token,
        "token_type": "bearer",
    }
