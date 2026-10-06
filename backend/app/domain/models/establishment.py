import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, Uuid, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.domain.models.base import Base

if TYPE_CHECKING:
    from app.domain.models.user import User
    from app.domain.models.service import Service
    from app.domain.models.professional import Professional
    from app.domain.models.customer import Customer
    from app.domain.models.appointment import Appointment


class Establishment(Base):
    __tablename__ = "establishments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    settings: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamentos com lazy='raise' para prevenir N+1 não intencional
    users: Mapped[list["User"]] = relationship(
        back_populates="establishment", cascade="all, delete-orphan", lazy="raise"
    )
    professionals: Mapped[list["Professional"]] = relationship(
        back_populates="establishment", cascade="all, delete-orphan", lazy="raise"
    )
    services: Mapped[list["Service"]] = relationship(
        back_populates="establishment", cascade="all, delete-orphan", lazy="raise"
    )
    customers: Mapped[list["Customer"]] = relationship(
        back_populates="establishment", cascade="all, delete-orphan", lazy="raise"
    )
    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="establishment", cascade="all, delete-orphan", lazy="raise"
    )
