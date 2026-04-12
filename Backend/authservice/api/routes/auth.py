"""
Propósito del archivo: Definición y exposición de las APIs REST correspondientes al manejo de credenciales (Rutas).
Rol dentro del microservicio: Contiene los controllers HTTP para logueos, chequeo de estatus del token y renovación. Enlaza los esquemas de Pydantic con las capas de lógica (Services).
"""

from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from config.config import settings
from config.security import create_access_token
from data.auth import Token, LoginRequest, RefreshTokenRequest
from data.user import UserResponse
from modules.auth_service import AuthService
from api.dependencies.auth import get_current_user
from modules.session_service import SessionService

router = APIRouter()


@router.post("/login", response_model=Token)
def login(request: LoginRequest) -> Any:
    """
    Endpoint: Ingresar a la aplicación intercambiando JSON de credenciales por Token (Login regular).
    """
    user = AuthService.authenticate_user(email=request.email, password=request.password)
    session = SessionService.create_session(user.id_usuario)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Lógica Crítica: Generación del JWT vinculando la expiración custom descrita en las politicas
    access_token = create_access_token(
        subject=user.id_usuario,
        email=user.email,
        rol=user.rol,
        partner_id=str(user.partner_id) if user.partner_id else None,
        session_id=str(session.id),
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": session.refresh_token,
        "token_type": "bearer"
    }


@router.post("/login/form", response_model=Token)
def login_form(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    Endpoint: Ingresar a la aplicación intercambiando Form-Data para sistemas integrados compatibles o Swagger UI.
    """
    user = AuthService.authenticate_user(email=form_data.username, password=form_data.password)
    session = SessionService.create_session(user.id_usuario)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        subject=user.id_usuario,
        email=user.email,
        rol=user.rol,
        partner_id=str(user.partner_id) if user.partner_id else None,
        session_id=str(session.id),
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": session.refresh_token,
        "token_type": "bearer"
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
    Endpoint: Renueva sin necesidad de credenciales explícitas el tiempo de vida de la sesión activa, 
    entregando un nuevo token firmado, a partir de uno previamente válido a expirar.
    """
    session = SessionService.rotate_refresh_token(request.refresh_token)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se han podido validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        subject=session.user_id,
        email=session.email,
        rol=session.rol,
        partner_id=str(session.partner_id) if session.partner_id else None,
        session_id=str(session.id),
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": session.refresh_token,
        "token_type": "bearer"
    }
