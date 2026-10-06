import uuid
from decimal import Decimal
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, Numeric, Boolean, DateTime, ForeignKey, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.domain.models.base import Base

if TYPE_CHECKING:
    from app.domain.models.establishment import Establishment
    from app.domain.models.professional import ProfessionalService
    from app.domain.models.appointment import Appointment


class Service(Base):
    __tablename__ = "services"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    establishment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("establishments.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    establishment: Mapped["Establishment"] = relationship(back_populates="services", lazy="raise")
    professional_services: Mapped[list["ProfessionalService"]] = relationship(
        back_populates="service", cascade="all, delete-orphan", lazy="raise"
    )
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="service", lazy="raise")
