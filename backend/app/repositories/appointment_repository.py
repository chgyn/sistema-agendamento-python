from datetime import datetime
import uuid
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models.appointment import Appointment, AppointmentStatus
from app.repositories.base import BaseRepository


class AppointmentRepository(BaseRepository[Appointment]):
    def __init__(self):
        super().__init__(Appointment)

    async def get_by_id_with_relations(
        self, session: AsyncSession, appointment_id: uuid.UUID, establishment_id: uuid.UUID | None = None
    ) -> Appointment | None:
        stmt = (
            select(Appointment)
            .options(
                selectinload(Appointment.customer),
                selectinload(Appointment.professional),
                selectinload(Appointment.service),
            )
            .where(Appointment.id == appointment_id)
        )
        if establishment_id is not None:
            stmt = stmt.where(Appointment.establishment_id == establishment_id)

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def check_conflicts(
        self,
        session: AsyncSession,
        professional_id: uuid.UUID,
        start_datetime: datetime,
        end_datetime: datetime,
        exclude_appointment_id: uuid.UUID | None = None,
        for_update: bool = False,
    ) -> list[Appointment]:
        """Verifica se existem agendamentos ativos sobrepostos para o mesmo profissional.
        Regra de sobreposição: (A.start < B.end) AND (A.end > B.start) e status != CANCELLED.
        """
        stmt = (
            select(Appointment)
            .where(
                Appointment.professional_id == professional_id,
                Appointment.status != AppointmentStatus.CANCELLED,
                Appointment.start_datetime < end_datetime,
                Appointment.end_datetime > start_datetime,
            )
        )
        if exclude_appointment_id is not None:
            stmt = stmt.where(Appointment.id != exclude_appointment_id)

        if for_update:
            bind = session.get_bind()
            dialect_name = getattr(bind.dialect, "name", "") if bind else ""
            if dialect_name != "sqlite":
                stmt = stmt.with_for_update()

        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_period(
        self,
        session: AsyncSession,
        establishment_id: uuid.UUID,
        start_date: datetime,
        end_date: datetime,
        professional_id: uuid.UUID | None = None,
        status: AppointmentStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Appointment]:
        stmt = (
            select(Appointment)
            .options(
                selectinload(Appointment.customer),
                selectinload(Appointment.professional),
                selectinload(Appointment.service),
            )
            .where(
                Appointment.establishment_id == establishment_id,
                Appointment.start_datetime >= start_date,
                Appointment.start_datetime <= end_date,
            )
        )
        if professional_id is not None:
            stmt = stmt.where(Appointment.professional_id == professional_id)
        if status is not None:
            stmt = stmt.where(Appointment.status == status)

        stmt = stmt.order_by(Appointment.start_datetime.asc()).limit(limit).offset(offset)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_period_paginated(
        self,
        session: AsyncSession,
        establishment_id: uuid.UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        professional_id: uuid.UUID | None = None,
        status: AppointmentStatus | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Appointment], int]:
        stmt = (
            select(Appointment)
            .options(
                selectinload(Appointment.customer),
                selectinload(Appointment.professional),
                selectinload(Appointment.service),
            )
            .where(Appointment.establishment_id == establishment_id)
        )
        if start_date is not None:
            stmt = stmt.where(Appointment.start_datetime >= start_date)
        if end_date is not None:
            stmt = stmt.where(Appointment.start_datetime <= end_date)
        if professional_id is not None:
            stmt = stmt.where(Appointment.professional_id == professional_id)
        if status is not None:
            stmt = stmt.where(Appointment.status == status)

        stmt = stmt.order_by(Appointment.start_datetime.asc())
        return await self.paginate(session, stmt, page=page, page_size=page_size)

    async def list_active_for_professional_on_date(
        self,
        session: AsyncSession,
        professional_id: uuid.UUID,
        day_start: datetime,
        day_end: datetime,
    ) -> list[Appointment]:
        """Obtém agendamentos de um dia específico para cálculo de disponibilidade."""
        stmt = (
            select(Appointment)
            .where(
                Appointment.professional_id == professional_id,
                Appointment.status != AppointmentStatus.CANCELLED,
                Appointment.start_datetime >= day_start,
                Appointment.start_datetime <= day_end,
            )
            .order_by(Appointment.start_datetime.asc())
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
