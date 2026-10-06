from typing import Generic, TypeVar, Any
import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Repositório base genérico assíncrono para operações CRUD comuns."""

    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get_by_id(self, session: AsyncSession, entity_id: uuid.UUID) -> ModelType | None:
        stmt = select(self.model).where(self.model.id == entity_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, session: AsyncSession, entity: ModelType) -> ModelType:
        session.add(entity)
        await session.flush()
        await session.refresh(entity)
        return entity

    async def update(self, session: AsyncSession, entity: ModelType) -> ModelType:
        session.add(entity)
        await session.flush()
        await session.refresh(entity)
        return entity

    async def delete(self, session: AsyncSession, entity: ModelType) -> None:
        await session.delete(entity)
        await session.flush()
