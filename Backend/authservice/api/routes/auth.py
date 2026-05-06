"""
Propósito del archivo: Definición y exposición de las APIs REST correspondientes al manejo de credenciales (Rutas).
Rol dentro del microservicio: Contiene los controllers HTTP para logueos, chequeo de estatus del token y renovación.
La autenticación y gestión de tokens es delegada a AWS Cognito.
"""

from typing import Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from data.auth import (
    ConfirmRegisterRequest,
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    Token,
)
from data.user import UserResponse
from modules.auth_service import AuthService
from modules.user_service import UserService
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


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest) -> Any:
    """
    Endpoint: Registra un viajero y dispara el envío del código de validación por Cognito.
    """
    cognito_response = AuthService.register_user(
        email=request.email,
        password=request.password,
        first_name=request.first_name,
        last_name=request.last_name,
        phone_number=request.phone_number,
    )

    full_name = f"{request.first_name} {request.last_name}".strip()
    # UserSub es el UUID que Cognito usará como claim 'username' en el Access Token
    cognito_sub = cognito_response.get("UserSub", request.email)
    saved_user = UserService.create_or_update_registered_user(
        email=request.email,
        full_name=full_name,
        username=cognito_sub,
        active=False,
    )
    if not saved_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible sincronizar el usuario en la base local",
        )

    code_delivery = cognito_response.get("CodeDeliveryDetails", {})
    return {
        "message": "Registro exitoso. Se envió un código de validación.",
        "destination": code_delivery.get("Destination"),
        "delivery_medium": code_delivery.get("DeliveryMedium"),
    }


@router.post("/register/confirm", response_model=MessageResponse)
def confirm_register(request: ConfirmRegisterRequest) -> Any:
    """
    Endpoint: Confirma el código de validación para activar la cuenta del viajero.
    """
    AuthService.confirm_registration(email=request.email, code=request.code)

    user_activated = UserService.activate_user(email=request.email)
    if not user_activated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado en la base local",
        )

    return {"message": "Cuenta confirmada correctamente. Ya puedes iniciar sesión."}


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


@router.get("/users/{id_usuario}", response_model=UserResponse)
def read_user_by_id(
    id_usuario: UUID,
    _current_user: UserResponse = Depends(get_current_user),
) -> Any:
    """
    Endpoint: Obtiene los datos de un usuario por id para integraciones internas autenticadas.
    """
    user = UserService.get_user_by_id(id_usuario)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    return UserResponse(
        id_usuario=user.id_usuario,
        email=user.email,
        full_name=user.full_name,
        rol=user.rol,
        partner_id=user.partner_id,
    )


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
