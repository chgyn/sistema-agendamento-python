from typing import Annotated
import uuid
from fastapi import APIRouter, Query
from app.api.deps import DbSession, CurrentUser
from app.schemas.customer import CustomerResponse
from app.schemas.pagination import PaginatedResponse, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.repositories.customer_repository import CustomerRepository
from app.domain.exceptions import EntityNotFoundError

router = APIRouter()
customer_repo = CustomerRepository()


@router.get(
    "",
    response_model=PaginatedResponse[CustomerResponse],
    summary="Listar Clientes do Estabelecimento",
    description="Retorna lista paginada de clientes com contagem total e busca opcional por nome ou telefone.",
)
async def list_customers(
    session: DbSession,
    current_user: CurrentUser,
    page: Annotated[int, Query(ge=1, description="Número da página (1-based)")] = 1,
    page_size: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE, description="Itens por página")] = DEFAULT_PAGE_SIZE,
    search: Annotated[str | None, Query(description="Filtrar por nome ou celular")] = None,
) -> PaginatedResponse[CustomerResponse]:
    customers, total = await customer_repo.list_by_establishment_paginated(
        session=session,
        establishment_id=current_user.establishment_id,
        page=page,
        page_size=page_size,
        search=search,
    )
    items = [CustomerResponse.model_validate(c) for c in customers]
    return PaginatedResponse.create(items=items, total=total, page=page, page_size=page_size)


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Obter Detalhes do Cliente",
)
async def get_customer(
    session: DbSession, customer_id: uuid.UUID, current_user: CurrentUser
) -> CustomerResponse:
    customer = await customer_repo.get_by_id_and_establishment(
        session, customer_id, current_user.establishment_id
    )
    if not customer:
        raise EntityNotFoundError("Cliente", customer_id)
    return CustomerResponse.model_validate(customer)
