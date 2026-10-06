import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.exceptions import EntityNotFoundError
from app.domain.models.service import Service
from app.domain.models.professional import (
    Professional,
    ProfessionalWorkingHour,
    ProfessionalUnavailability,
)
from app.repositories.service_repository import ServiceRepository
from app.repositories.professional_repository import ProfessionalRepository
from app.schemas.service import ServiceCreate, ServiceUpdate
from app.schemas.professional import (
    ProfessionalCreate,
    ProfessionalUpdate,
    WorkingHourCreate,
    UnavailabilityCreate,
)


class CatalogService:
    def __init__(
        self,
        service_repo: ServiceRepository | None = None,
        professional_repo: ProfessionalRepository | None = None,
    ):
        self.service_repo = service_repo or ServiceRepository()
        self.professional_repo = professional_repo or ProfessionalRepository()

    # --- SERVIÇOS ---
    async def create_service(
        self, session: AsyncSession, establishment_id: uuid.UUID, data: ServiceCreate
    ) -> Service:
        service = Service(
            establishment_id=establishment_id,
            name=data.name,
            description=data.description,
            duration_minutes=data.duration_minutes,
            price=data.price,
        )
        created = await self.service_repo.create(session, service)
        await session.commit()
        return created

    async def get_service(
        self, session: AsyncSession, service_id: uuid.UUID, establishment_id: uuid.UUID
    ) -> Service:
        service = await self.service_repo.get_by_id_and_establishment(session, service_id, establishment_id)
        if not service:
            raise EntityNotFoundError("Serviço", service_id)
        return service

    async def list_services(
        self, session: AsyncSession, establishment_id: uuid.UUID, active_only: bool = False
    ) -> list[Service]:
        return await self.service_repo.list_by_establishment(session, establishment_id, active_only=active_only)

    async def update_service(
        self, session: AsyncSession, service_id: uuid.UUID, establishment_id: uuid.UUID, data: ServiceUpdate
    ) -> Service:
        service = await self.get_service(session, service_id, establishment_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(service, key, value)
        updated = await self.service_repo.update(session, service)
        await session.commit()
        return updated

    # --- PROFISSIONAIS ---
    async def create_professional(
        self, session: AsyncSession, establishment_id: uuid.UUID, data: ProfessionalCreate
    ) -> Professional:
        professional = Professional(
            establishment_id=establishment_id,
            name=data.name,
            email=data.email,
            phone=data.phone,
            bio=data.bio,
        )
        created = await self.professional_repo.create(session, professional)

        if data.service_ids:
            await self.professional_repo.sync_services(session, created.id, data.service_ids)

        if data.working_hours:
            wh_models = [
                ProfessionalWorkingHour(
                    day_of_week=wh.day_of_week,
                    start_time=wh.start_time,
                    end_time=wh.end_time,
                    break_start_time=wh.break_start_time,
                    break_end_time=wh.break_end_time,
                    is_active=wh.is_active,
                )
                for wh in data.working_hours
            ]
            await self.professional_repo.set_working_hours(session, created.id, wh_models)

        await session.commit()
        detailed = await self.professional_repo.get_by_id_with_details(session, created.id, establishment_id)
        return detailed or created

    async def get_professional(
        self, session: AsyncSession, professional_id: uuid.UUID, establishment_id: uuid.UUID
    ) -> Professional:
        prof = await self.professional_repo.get_by_id_with_details(session, professional_id, establishment_id)
        if not prof:
            raise EntityNotFoundError("Profissional", professional_id)
        return prof

    async def list_professionals(
        self,
        session: AsyncSession,
        establishment_id: uuid.UUID,
        active_only: bool = False,
        service_id: uuid.UUID | None = None,
    ) -> list[Professional]:
        return await self.professional_repo.list_by_establishment(
            session, establishment_id, active_only=active_only, service_id=service_id
        )

    async def update_professional(
        self, session: AsyncSession, professional_id: uuid.UUID, establishment_id: uuid.UUID, data: ProfessionalUpdate
    ) -> Professional:
        prof = await self.get_professional(session, professional_id, establishment_id)
        update_dict = data.model_dump(exclude_unset=True, exclude={"service_ids"})
        for key, value in update_dict.items():
            setattr(prof, key, value)

        if data.service_ids is not None:
            await self.professional_repo.sync_services(session, prof.id, data.service_ids)

        await self.professional_repo.update(session, prof)
        await session.commit()
        return await self.get_professional(session, professional_id, establishment_id)

    async def set_working_hours(
        self,
        session: AsyncSession,
        professional_id: uuid.UUID,
        establishment_id: uuid.UUID,
        working_hours: list[WorkingHourCreate],
    ) -> list[ProfessionalWorkingHour]:
        await self.get_professional(session, professional_id, establishment_id)
        wh_models = [
            ProfessionalWorkingHour(
                day_of_week=wh.day_of_week,
                start_time=wh.start_time,
                end_time=wh.end_time,
                break_start_time=wh.break_start_time,
                break_end_time=wh.break_end_time,
                is_active=wh.is_active,
            )
            for wh in working_hours
        ]
        await self.professional_repo.set_working_hours(session, professional_id, wh_models)
        await session.commit()
        prof = await self.get_professional(session, professional_id, establishment_id)
        return prof.working_hours

    async def add_unavailability(
        self,
        session: AsyncSession,
        professional_id: uuid.UUID,
        establishment_id: uuid.UUID,
        data: UnavailabilityCreate,
    ) -> ProfessionalUnavailability:
        await self.get_professional(session, professional_id, establishment_id)
        unavailability = ProfessionalUnavailability(
            professional_id=professional_id,
            start_datetime=data.start_datetime,
            end_datetime=data.end_datetime,
            reason=data.reason,
        )
        created = await self.professional_repo.add_unavailability(session, unavailability)
        await session.commit()
        return created
