from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, Query, status
from app.api.deps import DbSession, CurrentUser, require_role
from app.domain.models.user import UserRole
from app.schemas.professional import (
    ProfessionalCreate,
    ProfessionalUpdate,
    ProfessionalResponse,
    WorkingHourCreate,
    WorkingHourResponse,
    UnavailabilityCreate,
    UnavailabilityResponse,
)
from app.services.catalog_service import CatalogService

router = APIRouter()
catalog_service = CatalogService()


@router.get(
    "",
    response_model=list[ProfessionalResponse],
    summary="Listar Profissionais",
    description="Retorna os profissionais cadastrados para o estabelecimento autenticado.",
)
async def list_professionals(
    session: DbSession,
    current_user: CurrentUser,
    active_only: Annotated[bool, Query(description="Filtrar apenas profissionais ativos")] = False,
    service_id: Annotated[uuid.UUID | None, Query(description="Filtrar por serviço habilitado")] = None,
) -> list[ProfessionalResponse]:
    professionals = await catalog_service.list_professionals(
        session, current_user.establishment_id, active_only=active_only, service_id=service_id
    )
    return [
        ProfessionalResponse(
            id=p.id,
            establishment_id=p.establishment_id,
            name=p.name,
            email=p.email,
            phone=p.phone,
            bio=p.bio,
            is_active=p.is_active,
            service_ids=[ps.service_id for ps in p.services],
            working_hours=[WorkingHourResponse.model_validate(wh) for wh in p.working_hours],
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in professionals
    ]


@router.post(
    "",
    response_model=ProfessionalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar Profissional",
    description="Adiciona profissional com seus serviços habilitados e grade horária (somente Administrador).",
)
async def create_professional(
    session: DbSession,
    payload: ProfessionalCreate,
    admin_user: Annotated[CurrentUser, Depends(require_role(UserRole.ADMIN))],
) -> ProfessionalResponse:
    p = await catalog_service.create_professional(
        session, admin_user.establishment_id, payload
    )
    return ProfessionalResponse(
        id=p.id,
        establishment_id=p.establishment_id,
        name=p.name,
        email=p.email,
        phone=p.phone,
        bio=p.bio,
        is_active=p.is_active,
        service_ids=[ps.service_id for ps in p.services],
        working_hours=[WorkingHourResponse.model_validate(wh) for wh in p.working_hours],
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


@router.get(
    "/{professional_id}",
    response_model=ProfessionalResponse,
    summary="Obter Detalhes do Profissional",
)
async def get_professional(
    session: DbSession,
    professional_id: uuid.UUID,
    current_user: CurrentUser,
) -> ProfessionalResponse:
    p = await catalog_service.get_professional(
        session, professional_id, current_user.establishment_id
    )
    return ProfessionalResponse(
        id=p.id,
        establishment_id=p.establishment_id,
        name=p.name,
        email=p.email,
        phone=p.phone,
        bio=p.bio,
        is_active=p.is_active,
        service_ids=[ps.service_id for ps in p.services],
        working_hours=[WorkingHourResponse.model_validate(wh) for wh in p.working_hours],
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


@router.put(
    "/{professional_id}",
    response_model=ProfessionalResponse,
    summary="Atualizar Profissional",
)
async def update_professional(
    session: DbSession,
    professional_id: uuid.UUID,
    payload: ProfessionalUpdate,
    admin_user: Annotated[CurrentUser, Depends(require_role(UserRole.ADMIN))],
) -> ProfessionalResponse:
    p = await catalog_service.update_professional(
        session, professional_id, admin_user.establishment_id, payload
    )
    return ProfessionalResponse(
        id=p.id,
        establishment_id=p.establishment_id,
        name=p.name,
        email=p.email,
        phone=p.phone,
        bio=p.bio,
        is_active=p.is_active,
        service_ids=[ps.service_id for ps in p.services],
        working_hours=[WorkingHourResponse.model_validate(wh) for wh in p.working_hours],
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


@router.put(
    "/{professional_id}/working-hours",
    response_model=list[WorkingHourResponse],
    summary="Configurar Grade Semanal de Horários",
)
async def set_working_hours(
    session: DbSession,
    professional_id: uuid.UUID,
    payload: list[WorkingHourCreate],
    admin_user: Annotated[CurrentUser, Depends(require_role(UserRole.ADMIN))],
) -> list[WorkingHourResponse]:
    whs = await catalog_service.set_working_hours(
        session, professional_id, admin_user.establishment_id, payload
    )
    return [WorkingHourResponse.model_validate(wh) for wh in whs]


@router.post(
    "/{professional_id}/unavailabilities",
    response_model=UnavailabilityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar Bloqueio/Indisponibilidade Pontual",
)
async def add_unavailability(
    session: DbSession,
    professional_id: uuid.UUID,
    payload: UnavailabilityCreate,
    current_user: CurrentUser,
) -> UnavailabilityResponse:
    unav = await catalog_service.add_unavailability(
        session, professional_id, current_user.establishment_id, payload
    )
    return UnavailabilityResponse.model_validate(unav)
