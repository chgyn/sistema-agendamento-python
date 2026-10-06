from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, Query, status
from app.api.deps import DbSession, CurrentUser, require_role
from app.domain.models.user import UserRole
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse
from app.services.catalog_service import CatalogService

router = APIRouter()
catalog_service = CatalogService()


@router.get(
    "",
    response_model=list[ServiceResponse],
    summary="Listar Serviços",
    description="Lista todos os serviços cadastrados para o estabelecimento autenticado.",
)
async def list_services(
    session: DbSession,
    current_user: CurrentUser,
    active_only: Annotated[bool, Query(description="Filtrar apenas serviços ativos")] = False,
) -> list[ServiceResponse]:
    services = await catalog_service.list_services(
        session, current_user.establishment_id, active_only=active_only
    )
    return [ServiceResponse.model_validate(s) for s in services]


@router.post(
    "",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar Novo Serviço",
    description="Adiciona um novo serviço ao catálogo do estabelecimento (somente Administrador).",
)
async def create_service(
    session: DbSession,
    payload: ServiceCreate,
    admin_user: Annotated[CurrentUser, Depends(require_role(UserRole.ADMIN))],
) -> ServiceResponse:
    service = await catalog_service.create_service(
        session, admin_user.establishment_id, payload
    )
    return ServiceResponse.model_validate(service)


@router.get(
    "/{service_id}",
    response_model=ServiceResponse,
    summary="Obter Detalhes do Serviço",
)
async def get_service(
    session: DbSession,
    service_id: uuid.UUID,
    current_user: CurrentUser,
) -> ServiceResponse:
    service = await catalog_service.get_service(
        session, service_id, current_user.establishment_id
    )
    return ServiceResponse.model_validate(service)


@router.put(
    "/{service_id}",
    response_model=ServiceResponse,
    summary="Atualizar Serviço",
    description="Atualiza dados do serviço (somente Administrador).",
)
async def update_service(
    session: DbSession,
    service_id: uuid.UUID,
    payload: ServiceUpdate,
    admin_user: Annotated[CurrentUser, Depends(require_role(UserRole.ADMIN))],
) -> ServiceResponse:
    service = await catalog_service.update_service(
        session, service_id, admin_user.establishment_id, payload
    )
    return ServiceResponse.model_validate(service)
