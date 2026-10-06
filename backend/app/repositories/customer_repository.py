import uuid
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models.customer import Customer
from app.repositories.base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self):
        super().__init__(Customer)

    async def get_by_id_and_establishment(
        self, session: AsyncSession, customer_id: uuid.UUID, establishment_id: uuid.UUID
    ) -> Customer | None:
        stmt = (
            select(Customer)
            .where(Customer.id == customer_id, Customer.establishment_id == establishment_id)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_phone(
        self, session: AsyncSession, establishment_id: uuid.UUID, phone: str
    ) -> Customer | None:
        stmt = (
            select(Customer)
            .where(Customer.establishment_id == establishment_id, Customer.phone == phone)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_or_create(
        self,
        session: AsyncSession,
        establishment_id: uuid.UUID,
        name: str,
        phone: str,
        email: str | None = None,
    ) -> Customer:
        customer = await self.get_by_phone(session, establishment_id, phone)
        if customer:
            # Atualiza nome ou e-mail caso tenham sido fornecidos
            if name and customer.name != name:
                customer.name = name
            if email and customer.email != email:
                customer.email = email
            await session.flush()
            return customer

        customer = Customer(
            establishment_id=establishment_id,
            name=name,
            phone=phone,
            email=email,
        )
        session.add(customer)
        await session.flush()
        await session.refresh(customer)
        return customer

    async def list_by_establishment(
        self, session: AsyncSession, establishment_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> list[Customer]:
        stmt = (
            select(Customer)
            .where(Customer.establishment_id == establishment_id)
            .order_by(Customer.name)
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_establishment_paginated(
        self,
        session: AsyncSession,
        establishment_id: uuid.UUID,
        page: int = 1,
        page_size: int = 10,
        search: str | None = None,
    ) -> tuple[list[Customer], int]:
        stmt = select(Customer).where(Customer.establishment_id == establishment_id)
        if search and search.strip():
            search_clean = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Customer.name).like(search_clean),
                    Customer.phone.like(f"%{search.strip()}%"),
                )
            )
        stmt = stmt.order_by(Customer.name.asc())
        return await self.paginate(session, stmt, page=page, page_size=page_size)
