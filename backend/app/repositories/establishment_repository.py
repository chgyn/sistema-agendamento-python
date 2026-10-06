import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models.establishment import Establishment
from app.repositories.base import BaseRepository


class EstablishmentRepository(BaseRepository[Establishment]):
    def __init__(self):
        super().__init__(Establishment)

    async def get_by_slug(self, session: AsyncSession, slug: str) -> Establishment | None:
        stmt = select(Establishment).where(Establishment.slug == slug)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, session: AsyncSession, email: str) -> Establishment | None:
        stmt = select(Establishment).where(Establishment.email == email)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self, session: AsyncSession) -> list[Establishment]:
        stmt = select(Establishment).order_by(Establishment.name)
        result = await session.execute(stmt)
        return list(result.scalars().all())
