"""
Propósito del archivo: Definición y exposición de las APIs REST correspondientes al manejo de credenciales (Rutas).
Rol dentro del microservicio: Contiene los controllers HTTP para logueos, chequeo de estatus del token y renovación. Enlaza los esquemas de Pydantic con las capas de lógica (Services).
"""

from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from config.config import settings
from config.security import create_access_token
from data.auth import Token, LoginRequest
from data.user import UserResponse
from modules.auth_service import AuthService
from api.dependencies.auth import get_current_user

router = APIRouter()


@router.post("/login", response_model=Token)
def login(request: LoginRequest) -> Any:
    """
    Endpoint: Ingresar a la aplicación intercambiando JSON de credenciales por Token (Login regular).
    """
    user = AuthService.authenticate_user(email=request.email, password=request.password)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Lógica Crítica: Generación del JWT vinculando la expiración custom descrita en las politicas
    access_token = create_access_token(
        subject=user.id_usuario,
        email=user.email,
        rol=user.rol,
        partner_id=str(user.partner_id) if user.partner_id else None,
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/login/form", response_model=Token)
def login_form(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    Endpoint: Ingresar a la aplicación intercambiando Form-Data para sistemas integrados compatibles o Swagger UI.
    """
    user = AuthService.authenticate_user(email=form_data.username, password=form_data.password)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        subject=user.id_usuario,
        email=user.email,
        rol=user.rol,
        partner_id=str(user.partner_id) if user.partner_id else None,
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: UserResponse = Depends(get_current_user)) -> Any:
    """
    Endpoint: Obtiene el contexto general y la meta-data del usuario logueado en tiempo real.
    """
    return current_user


@router.post("/refresh", response_model=Token)
def refresh_token(current_user: UserResponse = Depends(get_current_user)) -> Any:
    """
    Endpoint: Renueva sin necesidad de credenciales explícitas el tiempo de vida de la sesión activa, 
    entregando un nuevo token firmado, a partir de uno previamente válido a expirar.
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        subject=current_user.id_usuario,
        email=current_user.email,
        rol=current_user.rol,
        partner_id=str(current_user.partner_id) if current_user.partner_id else None,
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
