from datetime import date, datetime, time, timedelta, timezone
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.exceptions import EntityNotFoundError
from app.domain.models.appointment import AppointmentStatus
from app.repositories.establishment_repository import EstablishmentRepository
from app.repositories.professional_repository import ProfessionalRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.appointment_repository import AppointmentRepository
from app.schemas.public import AvailabilityResponse, TimeSlot


class AvailabilityService:
    def __init__(
        self,
        establishment_repo: EstablishmentRepository | None = None,
        professional_repo: ProfessionalRepository | None = None,
        service_repo: ServiceRepository | None = None,
        appointment_repo: AppointmentRepository | None = None,
    ):
        self.establishment_repo = establishment_repo or EstablishmentRepository()
        self.professional_repo = professional_repo or ProfessionalRepository()
        self.service_repo = service_repo or ServiceRepository()
        self.appointment_repo = appointment_repo or AppointmentRepository()

    async def get_available_slots(
        self,
        session: AsyncSession,
        slug: str,
        professional_id: uuid.UUID,
        service_id: uuid.UUID,
        target_date: date,
    ) -> AvailabilityResponse:
        establishment = await self.establishment_repo.get_by_slug(session, slug)
        if not establishment or not establishment.is_active:
            raise EntityNotFoundError("Estabelecimento", slug)

        professional = await self.professional_repo.get_by_id_with_details(
            session, professional_id, establishment.id
        )
        if not professional or not professional.is_active:
            raise EntityNotFoundError("Profissional", professional_id)

        service = await self.service_repo.get_by_id_and_establishment(
            session, service_id, establishment.id
        )
        if not service or not service.is_active:
            raise EntityNotFoundError("Serviço", service_id)

        # Dia da semana (0 = Segunda-feira, 6 = Domingo)
        day_of_week = target_date.weekday()
        working_hour = next(
            (wh for wh in professional.working_hours if wh.day_of_week == day_of_week and wh.is_active),
            None,
        )

        if not working_hour:
            return AvailabilityResponse(
                date=target_date,
                professional_id=professional_id,
                service_id=service_id,
                slots=[],
            )

        # Buscar agendamentos existentes do dia
        day_start = datetime.combine(target_date, time.min).replace(tzinfo=timezone.utc)
        day_end = datetime.combine(target_date, time.max).replace(tzinfo=timezone.utc)
        existing_appointments = await self.appointment_repo.list_active_for_professional_on_date(
            session, professional_id, day_start, day_end
        )

        duration = timedelta(minutes=service.duration_minutes)
        slots: list[TimeSlot] = []

        current_slot_start = datetime.combine(target_date, working_hour.start_time).replace(tzinfo=timezone.utc)
        work_end = datetime.combine(target_date, working_hour.end_time).replace(tzinfo=timezone.utc)

        # Intervalo de descanso (almoço)
        break_start = None
        break_end = None
        if working_hour.break_start_time and working_hour.break_end_time:
            break_start = datetime.combine(target_date, working_hour.break_start_time).replace(tzinfo=timezone.utc)
            break_end = datetime.combine(target_date, working_hour.break_end_time).replace(tzinfo=timezone.utc)

        now_utc = datetime.now(timezone.utc)

        while current_slot_start + duration <= work_end:
            current_slot_end = current_slot_start + duration
            is_available = True

            # 1. Se o horário já passou hoje
            if current_slot_start < now_utc:
                is_available = False

            # 2. Verifica colisão com intervalo de descanso
            if is_available and break_start and break_end:
                if current_slot_start < break_end and current_slot_end > break_start:
                    is_available = False

            # 3. Verifica colisão com indisponibilidades cadastradas
            if is_available:
                for unav in professional.unavailabilities:
                    # Assegura que o datetime tenha timezone
                    unav_start = unav.start_datetime if unav.start_datetime.tzinfo else unav.start_datetime.replace(tzinfo=timezone.utc)
                    unav_end = unav.end_datetime if unav.end_datetime.tzinfo else unav.end_datetime.replace(tzinfo=timezone.utc)
                    if current_slot_start < unav_end and current_slot_end > unav_start:
                        is_available = False
                        break

            # 4. Verifica colisão com agendamentos existentes
            if is_available:
                for appt in existing_appointments:
                    appt_start = appt.start_datetime if appt.start_datetime.tzinfo else appt.start_datetime.replace(tzinfo=timezone.utc)
                    appt_end = appt.end_datetime if appt.end_datetime.tzinfo else appt.end_datetime.replace(tzinfo=timezone.utc)
                    if current_slot_start < appt_end and current_slot_end > appt_start:
                        is_available = False
                        break

            slots.append(
                TimeSlot(
                    start_time=current_slot_start.strftime("%H:%M"),
                    end_time=current_slot_end.strftime("%H:%M"),
                    is_available=is_available,
                )
            )

            # Próximo slot avança pela duração do serviço ou intervalo de 30min se for muito longo
            step_minutes = min(service.duration_minutes, 30)
            current_slot_start += timedelta(minutes=step_minutes)

        return AvailabilityResponse(
            date=target_date,
            professional_id=professional_id,
            service_id=service_id,
            slots=slots,
        )
