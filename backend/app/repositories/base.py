from typing import Generic, TypeVar, Any
import uuid
from sqlalchemy import select, delete, func
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

    async def paginate(
        self,
        session: AsyncSession,
        base_query: Any,
        page: int = 1,
        page_size: int = 10,
        unique: bool = False,
    ) -> tuple[list[ModelType], int]:
        """Executa contagem total e fatiamento paginado de forma assíncrona com SQLAlchemy 2.0."""
        count_stmt = select(func.count()).select_from(base_query.order_by(None).subquery())
        total_result = await session.execute(count_stmt)
        total = total_result.scalar_one()

        offset = max(0, (page - 1) * page_size)
        items_stmt = base_query.limit(page_size).offset(offset)
        result = await session.execute(items_stmt)
        if unique:
            items = list(result.scalars().unique().all())
        else:
            items = list(result.scalars().all())
        return items, total
