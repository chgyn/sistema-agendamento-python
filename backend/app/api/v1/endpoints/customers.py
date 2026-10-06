from typing import Annotated
import uuid
from fastapi import APIRouter, Query
from app.api.deps import DbSession, CurrentUser
from app.schemas.customer import CustomerResponse
from app.repositories.customer_repository import CustomerRepository
from app.domain.exceptions import EntityNotFoundError

router = APIRouter()
customer_repo = CustomerRepository()


@router.get(
    "",
    response_model=list[CustomerResponse],
    summary="Listar Clientes do Estabelecimento",
)
async def list_customers(
    session: DbSession,
    current_user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=100, description="Limite máximo de registros")] = 50,
    offset: Annotated[int, Query(ge=0, description="Deslocamento para paginação")] = 0,
) -> list[CustomerResponse]:
    customers = await customer_repo.list_by_establishment(
        session, current_user.establishment_id, limit=limit, offset=offset
    )
    return [CustomerResponse.model_validate(c) for c in customers]


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
