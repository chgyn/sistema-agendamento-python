import uuid
from datetime import datetime, time
from typing import TYPE_CHECKING
from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    Time,
    Integer,
    ForeignKey,
    Uuid,
    func,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.domain.models.base import Base

if TYPE_CHECKING:
    from app.domain.models.establishment import Establishment
    from app.domain.models.service import Service
    from app.domain.models.appointment import Appointment


class Professional(Base):
    __tablename__ = "professionals"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    establishment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("establishments.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    bio: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    establishment: Mapped["Establishment"] = relationship(back_populates="professionals", lazy="raise")
    services: Mapped[list["ProfessionalService"]] = relationship(
        back_populates="professional", cascade="all, delete-orphan", lazy="raise"
    )
    working_hours: Mapped[list["ProfessionalWorkingHour"]] = relationship(
        back_populates="professional", cascade="all, delete-orphan", lazy="raise"
    )
    unavailabilities: Mapped[list["ProfessionalUnavailability"]] = relationship(
        back_populates="professional", cascade="all, delete-orphan", lazy="raise"
    )
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="professional", lazy="raise")


class ProfessionalService(Base):
    __tablename__ = "professional_services"
    __table_args__ = (
        UniqueConstraint("professional_id", "service_id", name="uq_professional_service"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    professional_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("professionals.id", ondelete="CASCADE"), index=True, nullable=False
    )
    service_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("services.id", ondelete="CASCADE"), index=True, nullable=False
    )

    professional: Mapped["Professional"] = relationship(back_populates="services", lazy="raise")
    service: Mapped["Service"] = relationship(back_populates="professional_services", lazy="raise")


class ProfessionalWorkingHour(Base):
    __tablename__ = "professional_working_hours"
    __table_args__ = (
        UniqueConstraint("professional_id", "day_of_week", name="uq_professional_weekday"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    professional_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("professionals.id", ondelete="CASCADE"), index=True, nullable=False
    )
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Segunda ... 6=Domingo
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    break_start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    break_end_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    professional: Mapped["Professional"] = relationship(back_populates="working_hours", lazy="raise")


class ProfessionalUnavailability(Base):
    __tablename__ = "professional_unavailabilities"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    professional_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("professionals.id", ondelete="CASCADE"), index=True, nullable=False
    )
    start_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    end_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    professional: Mapped["Professional"] = relationship(back_populates="unavailabilities", lazy="raise")
