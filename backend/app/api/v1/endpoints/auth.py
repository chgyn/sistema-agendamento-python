from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.api.deps import DbSession, CurrentUser
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login de Usuário Interno",
    description="Autentica usuário e retorna JWT access token.",
)
async def login(session: DbSession, login_data: LoginRequest) -> TokenResponse:
    return await auth_service.authenticate(session, login_data)


@router.post(
    "/token",
    response_model=TokenResponse,
    include_in_schema=False,
    summary="Login compatível com documentação OpenAPI Swagger UI",
)
async def login_swagger(
    session: DbSession, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> TokenResponse:
    login_data = LoginRequest(email=form_data.username, password=form_data.password)
    return await auth_service.authenticate(session, login_data)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Dados do Usuário Logado",
    description="Retorna informações cadastrais do usuário autenticado e seu tenant.",
)
async def get_current_user_profile(current_user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(current_user)
