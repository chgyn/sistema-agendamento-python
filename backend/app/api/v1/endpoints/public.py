from datetime import date
from typing import Annotated
import uuid
from fastapi import APIRouter, Query, status
from app.api.deps import DbSession
from app.schemas.public import (
    EstablishmentPublicResponse,
    ServicePublicResponse,
    ProfessionalPublicResponse,
    AvailabilityResponse,
    PublicAppointmentCreateRequest,
    AppointmentPublicResponse,
)
from app.services.establishment_service import EstablishmentService
from app.services.catalog_service import CatalogService
from app.services.availability_service import AvailabilityService
from app.services.appointment_service import AppointmentService

router = APIRouter()
establishment_service = EstablishmentService()
catalog_service = CatalogService()
availability_service = AvailabilityService()
appointment_service = AppointmentService()


@router.get(
    "/{slug}",
    response_model=EstablishmentPublicResponse,
    summary="Consultar Estabelecimento Público",
    description="Retorna informações públicas e catálogo da barbearia/salão pelo slug.",
)
async def get_public_establishment(session: DbSession, slug: str) -> EstablishmentPublicResponse:
    est = await establishment_service.get_by_slug(session, slug)
    return EstablishmentPublicResponse.model_validate(est)


@router.get(
    "/{slug}/services",
    response_model=list[ServicePublicResponse],
    summary="Listar Serviços Públicos",
    description="Retorna os serviços ativos oferecidos pelo estabelecimento.",
)
async def list_public_services(session: DbSession, slug: str) -> list[ServicePublicResponse]:
    est = await establishment_service.get_by_slug(session, slug)
    services = await catalog_service.list_services(session, est.id, active_only=True)
    return [ServicePublicResponse.model_validate(s) for s in services]


@router.get(
    "/{slug}/professionals",
    response_model=list[ProfessionalPublicResponse],
    summary="Listar Profissionais Públicos",
    description="Retorna os profissionais ativos que executam o serviço selecionado.",
)
async def list_public_professionals(
    session: DbSession,
    slug: str,
    service_id: Annotated[uuid.UUID | None, Query(description="Filtrar por serviço")] = None,
) -> list[ProfessionalPublicResponse]:
    est = await establishment_service.get_by_slug(session, slug)
    professionals = await catalog_service.list_professionals(
        session, est.id, active_only=True, service_id=service_id
    )
    return [ProfessionalPublicResponse.model_validate(p) for p in professionals]


@router.get(
    "/{slug}/availability",
    response_model=AvailabilityResponse,
    summary="Consultar Disponibilidade de Horários",
    description="Calcula dinamicamente os horários livres considerando grade, pausas, bloqueios e agendamentos existentes.",
)
async def get_availability(
    session: DbSession,
    slug: str,
    professional_id: Annotated[uuid.UUID, Query(description="ID do profissional")],
    service_id: Annotated[uuid.UUID, Query(description="ID do serviço")],
    target_date: Annotated[date, Query(description="Data da consulta (YYYY-MM-DD)", alias="date")],
) -> AvailabilityResponse:
    return await availability_service.get_available_slots(
        session=session,
        slug=slug,
        professional_id=professional_id,
        service_id=service_id,
        target_date=target_date,
    )


@router.post(
    "/{slug}/appointments",
    response_model=AppointmentPublicResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Realizar Agendamento Público",
    description="Confirma o agendamento pelo cliente com lock transacional e controle rigoroso de concorrência.",
)
async def create_public_appointment(
    session: DbSession,
    slug: str,
    payload: PublicAppointmentCreateRequest,
) -> AppointmentPublicResponse:
    return await appointment_service.create_public_appointment(
        session=session,
        slug=slug,
        data=payload,
    )
