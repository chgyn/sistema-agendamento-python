import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING
from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    Uuid,
    Enum as SQLEnum,
    Index,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.domain.models.base import Base

if TYPE_CHECKING:
    from app.domain.models.establishment import Establishment
    from app.domain.models.customer import Customer
    from app.domain.models.professional import Professional
    from app.domain.models.service import Service


class AppointmentStatus(StrEnum):
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    NO_SHOW = "NO_SHOW"


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        Index("ix_appointments_conflict_check", "professional_id", "start_datetime", "end_datetime", "status"),
        Index("ix_appointments_establishment_date", "establishment_id", "start_datetime", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    establishment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("establishments.id", ondelete="CASCADE"), index=True, nullable=False
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("customers.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    professional_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("professionals.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    service_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("services.id", ondelete="RESTRICT"), index=True, nullable=False
    )

    start_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(
        SQLEnum(AppointmentStatus, name="appointment_status_enum", native_enum=False),
        default=AppointmentStatus.SCHEDULED,
        nullable=False,
    )
    cancellation_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    establishment: Mapped["Establishment"] = relationship(back_populates="appointments", lazy="raise")
    customer: Mapped["Customer"] = relationship(back_populates="appointments", lazy="raise")
    professional: Mapped["Professional"] = relationship(back_populates="appointments", lazy="raise")
    service: Mapped["Service"] = relationship(back_populates="appointments", lazy="raise")
