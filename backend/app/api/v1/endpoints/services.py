from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, Query, status
from app.api.deps import DbSession, CurrentUser, require_role
from app.domain.models.user import UserRole
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse
from app.schemas.pagination import PaginatedResponse, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.services.catalog_service import CatalogService

router = APIRouter()
catalog_service = CatalogService()


@router.get(
    "",
    response_model=PaginatedResponse[ServiceResponse],
    summary="Listar Serviços",
    description="Lista serviços cadastrados para o estabelecimento com paginação e busca.",
)
async def list_services(
    session: DbSession,
    current_user: CurrentUser,
    page: Annotated[int, Query(ge=1, description="Número da página (1-based)")] = 1,
    page_size: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE, description="Quantidade por página")] = DEFAULT_PAGE_SIZE,
    active_only: Annotated[bool, Query(description="Filtrar apenas serviços ativos")] = False,
    search: Annotated[str | None, Query(description="Filtrar por nome do serviço")] = None,
    all_records: Annotated[bool, Query(description="Retornar todos os registros sem corte de página")] = False,
) -> PaginatedResponse[ServiceResponse]:
    eff_page = 1 if all_records else page
    eff_page_size = MAX_PAGE_SIZE if all_records else page_size
    services, total = await catalog_service.list_services_paginated(
        session=session,
        establishment_id=current_user.establishment_id,
        page=eff_page,
        page_size=eff_page_size,
        active_only=active_only,
        search=search,
    )
    items = [ServiceResponse.model_validate(s) for s in services]
    return PaginatedResponse.create(items=items, total=total, page=eff_page, page_size=eff_page_size)


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
