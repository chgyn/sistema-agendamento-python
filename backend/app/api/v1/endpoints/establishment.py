from typing import Annotated
from pydantic import BaseModel, EmailStr, Field
from fastapi import APIRouter, Depends, status
from app.api.deps import DbSession, CurrentUser, require_role
from app.domain.models.user import UserRole
from app.schemas.establishment import (
    EstablishmentCreate,
    EstablishmentUpdate,
    EstablishmentResponse,
)
from app.services.establishment_service import EstablishmentService

router = APIRouter()
establishment_service = EstablishmentService()


class EstablishmentRegisterRequest(BaseModel):
    establishment: EstablishmentCreate
    admin_name: str = Field(min_length=2, max_length=150)
    admin_email: EmailStr
    admin_password: str = Field(min_length=6, max_length=100)


@router.post(
    "/register",
    response_model=EstablishmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar Novo Estabelecimento e Primeiro Admin",
    description="Cria a conta do estabelecimento (tenant) e o primeiro usuário administrador.",
)
async def register_establishment(
    session: DbSession, payload: EstablishmentRegisterRequest
) -> EstablishmentResponse:
    est = await establishment_service.create_with_admin(
        session=session,
        establishment_in=payload.establishment,
        admin_name=payload.admin_name,
        admin_email=payload.admin_email,
        admin_password=payload.admin_password,
    )
    return EstablishmentResponse.model_validate(est)


@router.get(
    "/me",
    response_model=EstablishmentResponse,
    summary="Consultar Estabelecimento Atual",
    description="Retorna dados do estabelecimento associado ao usuário logado.",
)
async def get_my_establishment(
    session: DbSession, current_user: CurrentUser
) -> EstablishmentResponse:
    est = await establishment_service.get_by_id(session, current_user.establishment_id)
    return EstablishmentResponse.model_validate(est)


@router.patch(
    "/me",
    response_model=EstablishmentResponse,
    summary="Atualizar Estabelecimento Atual",
    description="Atualiza configurações do estabelecimento (exclusivo para perfil Administrador).",
)
async def update_my_establishment(
    session: DbSession,
    payload: EstablishmentUpdate,
    admin_user: Annotated[CurrentUser, Depends(require_role(UserRole.ADMIN))],
) -> EstablishmentResponse:
    est = await establishment_service.update(
        session=session,
        establishment_id=admin_user.establishment_id,
        data=payload,
    )
    return EstablishmentResponse.model_validate(est)
