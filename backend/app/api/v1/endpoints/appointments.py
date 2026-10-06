from datetime import datetime, timezone
from typing import Annotated
import uuid
from fastapi import APIRouter, Query, status
from app.api.deps import DbSession, CurrentUser
from app.domain.models.appointment import AppointmentStatus
from app.schemas.appointment import (
    AppointmentCreateInternal,
    AppointmentStatusUpdateRequest,
    AppointmentCancelRequest,
    AppointmentDetailResponse,
)
from app.schemas.pagination import PaginatedResponse, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.services.appointment_service import AppointmentService

router = APIRouter()
appointment_service = AppointmentService()


@router.get(
    "",
    response_model=PaginatedResponse[AppointmentDetailResponse],
    summary="Listar Agendamentos do Estabelecimento",
    description="Filtra agendamentos por intervalo de datas, profissional e status com paginação padronizada.",
)
async def list_appointments(
    session: DbSession,
    current_user: CurrentUser,
    start_date: Annotated[datetime | None, Query(description="Data inicial (ISO 8601)")] = None,
    end_date: Annotated[datetime | None, Query(description="Data final (ISO 8601)")] = None,
    professional_id: Annotated[uuid.UUID | None, Query(description="Filtrar por profissional")] = None,
    appointment_status: Annotated[AppointmentStatus | None, Query(alias="status")] = None,
    page: Annotated[int, Query(ge=1, description="Número da página (1-based)")] = 1,
    page_size: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE, description="Quantidade por página")] = DEFAULT_PAGE_SIZE,
) -> PaginatedResponse[AppointmentDetailResponse]:
    items, total = await appointment_service.list_appointments_paginated(
        session=session,
        establishment_id=current_user.establishment_id,
        start_date=start_date,
        end_date=end_date,
        professional_id=professional_id,
        status=appointment_status,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse.create(items=items, total=total, page=page, page_size=page_size)


@router.post(
    "",
    response_model=AppointmentDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar Agendamento Interno",
    description="Registra agendamento realizado diretamente pelo operador/administrador.",
)
async def create_internal_appointment(
    session: DbSession,
    current_user: CurrentUser,
    payload: AppointmentCreateInternal,
) -> AppointmentDetailResponse:
    return await appointment_service.create_internal_appointment(
        session=session,
        establishment_id=current_user.establishment_id,
        data=payload,
    )


@router.patch(
    "/{appointment_id}/status",
    response_model=AppointmentDetailResponse,
    summary="Atualizar Status do Agendamento",
    description="Altera o ciclo de vida do atendimento (Confirmado, Concluído, Não compareceu).",
)
async def update_appointment_status(
    session: DbSession,
    appointment_id: uuid.UUID,
    current_user: CurrentUser,
    payload: AppointmentStatusUpdateRequest,
) -> AppointmentDetailResponse:
    return await appointment_service.update_status(
        session=session,
        appointment_id=appointment_id,
        establishment_id=current_user.establishment_id,
        new_status=payload.status,
    )


@router.post(
    "/{appointment_id}/cancel",
    response_model=AppointmentDetailResponse,
    summary="Cancelar Agendamento",
    description="Cancela o agendamento preservando histórico e liberando o horário na grade.",
)
async def cancel_appointment(
    session: DbSession,
    appointment_id: uuid.UUID,
    current_user: CurrentUser,
    payload: AppointmentCancelRequest,
) -> AppointmentDetailResponse:
    return await appointment_service.cancel_appointment(
        session=session,
        appointment_id=appointment_id,
        establishment_id=current_user.establishment_id,
        reason=payload.reason,
    )
