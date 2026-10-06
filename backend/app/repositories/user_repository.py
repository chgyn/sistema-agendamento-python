import uuid
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, session: AsyncSession, email: str) -> User | None:
        stmt = (
            select(User)
            .options(selectinload(User.establishment))
            .where(User.email == email)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_and_establishment(
        self, session: AsyncSession, user_id: uuid.UUID, establishment_id: uuid.UUID
    ) -> User | None:
        stmt = (
            select(User)
            .where(User.id == user_id, User.establishment_id == establishment_id)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_establishment(
        self, session: AsyncSession, establishment_id: uuid.UUID
    ) -> list[User]:
        stmt = (
            select(User)
            .where(User.establishment_id == establishment_id)
            .order_by(User.name)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
