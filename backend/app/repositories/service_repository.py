import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models.service import Service
from app.repositories.base import BaseRepository


class ServiceRepository(BaseRepository[Service]):
    def __init__(self):
        super().__init__(Service)

    async def get_by_id_and_establishment(
        self, session: AsyncSession, service_id: uuid.UUID, establishment_id: uuid.UUID
    ) -> Service | None:
        stmt = (
            select(Service)
            .where(Service.id == service_id, Service.establishment_id == establishment_id)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_establishment(
        self, session: AsyncSession, establishment_id: uuid.UUID, active_only: bool = False
    ) -> list[Service]:
        stmt = select(Service).where(Service.establishment_id == establishment_id)
        if active_only:
            stmt = stmt.where(Service.is_active.is_(True))
        stmt = stmt.order_by(Service.name)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_establishment_paginated(
        self,
        session: AsyncSession,
        establishment_id: uuid.UUID,
        page: int = 1,
        page_size: int = 10,
        active_only: bool = False,
        search: str | None = None,
    ) -> tuple[list[Service], int]:
        stmt = select(Service).where(Service.establishment_id == establishment_id)
        if active_only:
            stmt = stmt.where(Service.is_active.is_(True))
        if search and search.strip():
            stmt = stmt.where(func.lower(Service.name).like(f"%{search.strip().lower()}%"))
        stmt = stmt.order_by(Service.name.asc())
        return await self.paginate(session, stmt, page=page, page_size=page_size)
