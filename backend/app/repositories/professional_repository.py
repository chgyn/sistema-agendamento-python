import uuid
from sqlalchemy import select, delete, or_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models.professional import (
    Professional,
    ProfessionalService,
    ProfessionalWorkingHour,
    ProfessionalUnavailability,
)
from app.repositories.base import BaseRepository


class ProfessionalRepository(BaseRepository[Professional]):
    def __init__(self):
        super().__init__(Professional)

    async def get_by_id_with_details(
        self, session: AsyncSession, professional_id: uuid.UUID, establishment_id: uuid.UUID
    ) -> Professional | None:
        stmt = (
            select(Professional)
            .options(
                selectinload(Professional.services),
                selectinload(Professional.working_hours),
                selectinload(Professional.unavailabilities),
            )
            .where(
                Professional.id == professional_id,
                Professional.establishment_id == establishment_id,
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_establishment(
        self,
        session: AsyncSession,
        establishment_id: uuid.UUID,
        active_only: bool = False,
        service_id: uuid.UUID | None = None,
    ) -> list[Professional]:
        stmt = (
            select(Professional)
            .options(
                selectinload(Professional.services),
                selectinload(Professional.working_hours),
            )
            .where(Professional.establishment_id == establishment_id)
        )
        if active_only:
            stmt = stmt.where(Professional.is_active.is_(True))

        if service_id is not None:
            stmt = stmt.join(Professional.services).where(
                ProfessionalService.service_id == service_id
            )

        stmt = stmt.order_by(Professional.name)
        result = await session.execute(stmt)
        return list(result.scalars().unique().all())

    async def list_by_establishment_paginated(
        self,
        session: AsyncSession,
        establishment_id: uuid.UUID,
        page: int = 1,
        page_size: int = 10,
        active_only: bool = False,
        service_id: uuid.UUID | None = None,
        search: str | None = None,
    ) -> tuple[list[Professional], int]:
        stmt = (
            select(Professional)
            .options(
                selectinload(Professional.services),
                selectinload(Professional.working_hours),
            )
            .where(Professional.establishment_id == establishment_id)
        )
        if active_only:
            stmt = stmt.where(Professional.is_active.is_(True))

        if service_id is not None:
            stmt = stmt.join(Professional.services).where(
                ProfessionalService.service_id == service_id
            )

        if search and search.strip():
            search_clean = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Professional.name).like(search_clean),
                    Professional.phone.like(f"%{search.strip()}%"),
                )
            )

        stmt = stmt.order_by(Professional.name.asc())
        return await self.paginate(session, stmt, page=page, page_size=page_size, unique=True)

    async def sync_services(
        self, session: AsyncSession, professional_id: uuid.UUID, service_ids: list[uuid.UUID]
    ) -> None:
        # Remove vínculos antigos
        await session.execute(
            delete(ProfessionalService).where(ProfessionalService.professional_id == professional_id)
        )
        # Adiciona novos vínculos
        for s_id in service_ids:
            session.add(ProfessionalService(professional_id=professional_id, service_id=s_id))
        await session.flush()

    async def set_working_hours(
        self, session: AsyncSession, professional_id: uuid.UUID, working_hours: list[ProfessionalWorkingHour]
    ) -> None:
        await session.execute(
            delete(ProfessionalWorkingHour).where(ProfessionalWorkingHour.professional_id == professional_id)
        )
        for wh in working_hours:
            wh.professional_id = professional_id
            session.add(wh)
        await session.flush()

    async def add_unavailability(
        self, session: AsyncSession, unavailability: ProfessionalUnavailability
    ) -> ProfessionalUnavailability:
        session.add(unavailability)
        await session.flush()
        await session.refresh(unavailability)
        return unavailability
