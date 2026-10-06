from datetime import datetime, timedelta, timezone
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.exceptions import (
    EntityNotFoundError,
    BusinessRuleViolation,
    AppointmentConflictError,
)
from app.domain.models.appointment import Appointment, AppointmentStatus
from app.repositories.establishment_repository import EstablishmentRepository
from app.repositories.professional_repository import ProfessionalRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.appointment_repository import AppointmentRepository
from app.schemas.public import (
    PublicAppointmentCreateRequest,
    AppointmentPublicResponse,
)
from app.schemas.appointment import (
    AppointmentCreateInternal,
    AppointmentDetailResponse,
)
from app.workers.tasks import send_appointment_confirmation, send_appointment_cancellation


class AppointmentService:
    def __init__(
        self,
        establishment_repo: EstablishmentRepository | None = None,
        professional_repo: ProfessionalRepository | None = None,
        service_repo: ServiceRepository | None = None,
        customer_repo: CustomerRepository | None = None,
        appointment_repo: AppointmentRepository | None = None,
    ):
        self.establishment_repo = establishment_repo or EstablishmentRepository()
        self.professional_repo = professional_repo or ProfessionalRepository()
        self.service_repo = service_repo or ServiceRepository()
        self.customer_repo = customer_repo or CustomerRepository()
        self.appointment_repo = appointment_repo or AppointmentRepository()

    async def create_public_appointment(
        self, session: AsyncSession, slug: str, data: PublicAppointmentCreateRequest
    ) -> AppointmentPublicResponse:
        establishment = await self.establishment_repo.get_by_slug(session, slug)
        if not establishment or not establishment.is_active:
            raise EntityNotFoundError("Estabelecimento", slug)

        now_utc = datetime.now(timezone.utc)
        start_dt = data.start_datetime if data.start_datetime.tzinfo else data.start_datetime.replace(tzinfo=timezone.utc)
        if start_dt < now_utc:
            raise BusinessRuleViolation("Não é possível agendar um horário no passado.")

        service = await self.service_repo.get_by_id_and_establishment(
            session, data.service_id, establishment.id
        )
        if not service or not service.is_active:
            raise EntityNotFoundError("Serviço", data.service_id)

        professional = await self.professional_repo.get_by_id_with_details(
            session, data.professional_id, establishment.id
        )
        if not professional or not professional.is_active:
            raise EntityNotFoundError("Profissional", data.professional_id)

        end_dt = start_dt + timedelta(minutes=service.duration_minutes)

        # Transação atômica com verificação de conflitos (prevenção de race condition)
        async with session.begin_nested():
            conflicts = await self.appointment_repo.check_conflicts(
                session=session,
                professional_id=professional.id,
                start_datetime=start_dt,
                end_datetime=end_dt,
                for_update=True,
            )
            if conflicts:
                raise AppointmentConflictError("Este horário acabou de ser reservado. Por favor, selecione outro.")

            # Cadastro ou reutilização do cliente no tenant
            customer = await self.customer_repo.find_or_create(
                session=session,
                establishment_id=establishment.id,
                name=data.customer_name,
                phone=data.customer_phone,
                email=data.customer_email,
            )

            appointment = Appointment(
                establishment_id=establishment.id,
                customer_id=customer.id,
                professional_id=professional.id,
                service_id=service.id,
                start_datetime=start_dt,
                end_datetime=end_dt,
                status=AppointmentStatus.SCHEDULED,
                notes=data.notes,
            )
            session.add(appointment)
            await session.flush()
            await session.refresh(appointment)

        await session.commit()

        # Dispara tarefa Celery assíncrona em segundo plano
        try:
            send_appointment_confirmation.delay(str(appointment.id))
        except Exception:
            # Não quebra o agendamento caso o worker/broker esteja temporariamente indisponível
            pass

        return AppointmentPublicResponse(
            id=appointment.id,
            start_datetime=appointment.start_datetime,
            end_datetime=appointment.end_datetime,
            status=appointment.status.value,
            service_name=service.name,
            professional_name=professional.name,
            message="Agendamento realizado com sucesso!",
        )

    async def create_internal_appointment(
        self, session: AsyncSession, establishment_id: uuid.UUID, data: AppointmentCreateInternal
    ) -> AppointmentDetailResponse:
        service = await self.service_repo.get_by_id_and_establishment(session, data.service_id, establishment_id)
        if not service:
            raise EntityNotFoundError("Serviço", data.service_id)

        professional = await self.professional_repo.get_by_id_with_details(session, data.professional_id, establishment_id)
        if not professional:
            raise EntityNotFoundError("Profissional", data.professional_id)

        customer = await self.customer_repo.get_by_id_and_establishment(session, data.customer_id, establishment_id)
        if not customer:
            raise EntityNotFoundError("Cliente", data.customer_id)

        start_dt = data.start_datetime if data.start_datetime.tzinfo else data.start_datetime.replace(tzinfo=timezone.utc)
        end_dt = start_dt + timedelta(minutes=service.duration_minutes)

        async with session.begin_nested():
            conflicts = await self.appointment_repo.check_conflicts(
                session=session,
                professional_id=professional.id,
                start_datetime=start_dt,
                end_datetime=end_dt,
                for_update=True,
            )
            if conflicts:
                raise AppointmentConflictError("Conflito com outro agendamento ativo do profissional.")

            appointment = Appointment(
                establishment_id=establishment_id,
                customer_id=customer.id,
                professional_id=professional.id,
                service_id=service.id,
                start_datetime=start_dt,
                end_datetime=end_dt,
                status=AppointmentStatus.CONFIRMED,
                notes=data.notes,
            )
            session.add(appointment)
            await session.flush()

        await session.commit()
        detailed = await self.appointment_repo.get_by_id_with_relations(session, appointment.id, establishment_id)
        return self._to_detail_response(detailed)

    async def update_status(
        self,
        session: AsyncSession,
        appointment_id: uuid.UUID,
        establishment_id: uuid.UUID,
        new_status: AppointmentStatus,
    ) -> AppointmentDetailResponse:
        appointment = await self.appointment_repo.get_by_id_with_relations(session, appointment_id, establishment_id)
        if not appointment:
            raise EntityNotFoundError("Agendamento", appointment_id)

        appointment.status = new_status
        await self.appointment_repo.update(session, appointment)
        await session.commit()
        return self._to_detail_response(appointment)

    async def cancel_appointment(
        self,
        session: AsyncSession,
        appointment_id: uuid.UUID,
        establishment_id: uuid.UUID,
        reason: str,
    ) -> AppointmentDetailResponse:
        appointment = await self.appointment_repo.get_by_id_with_relations(session, appointment_id, establishment_id)
        if not appointment:
            raise EntityNotFoundError("Agendamento", appointment_id)

        appointment.status = AppointmentStatus.CANCELLED
        appointment.cancellation_reason = reason
        appointment.cancelled_at = datetime.now(timezone.utc)

        await self.appointment_repo.update(session, appointment)
        await session.commit()

        # Dispara notificação assíncrona de cancelamento
        try:
            send_appointment_cancellation.delay(str(appointment.id), reason)
        except Exception:
            pass

        return self._to_detail_response(appointment)

    async def list_appointments(
        self,
        session: AsyncSession,
        establishment_id: uuid.UUID,
        start_date: datetime,
        end_date: datetime,
        professional_id: uuid.UUID | None = None,
        status: AppointmentStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AppointmentDetailResponse]:
        appointments = await self.appointment_repo.list_by_period(
            session=session,
            establishment_id=establishment_id,
            start_date=start_date,
            end_date=end_date,
            professional_id=professional_id,
            status=status,
            limit=limit,
            offset=offset,
        )
        return [self._to_detail_response(a) for a in appointments]

    async def list_appointments_paginated(
        self,
        session: AsyncSession,
        establishment_id: uuid.UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        professional_id: uuid.UUID | None = None,
        status: AppointmentStatus | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[AppointmentDetailResponse], int]:
        appointments, total = await self.appointment_repo.list_by_period_paginated(
            session=session,
            establishment_id=establishment_id,
            start_date=start_date,
            end_date=end_date,
            professional_id=professional_id,
            status=status,
            page=page,
            page_size=page_size,
        )
        return [self._to_detail_response(a) for a in appointments], total

    def _to_detail_response(self, a: Appointment) -> AppointmentDetailResponse:
        return AppointmentDetailResponse(
            id=a.id,
            establishment_id=a.establishment_id,
            customer_id=a.customer_id,
            customer_name=a.customer.name,
            customer_phone=a.customer.phone,
            professional_id=a.professional_id,
            professional_name=a.professional.name,
            service_id=a.service_id,
            service_name=a.service.name,
            start_datetime=a.start_datetime,
            end_datetime=a.end_datetime,
            status=a.status,
            cancellation_reason=a.cancellation_reason,
            cancelled_at=a.cancelled_at,
            notes=a.notes,
            created_at=a.created_at,
            updated_at=a.updated_at,
        )
