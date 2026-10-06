import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Uuid, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.domain.models.base import Base

if TYPE_CHECKING:
    from app.domain.models.establishment import Establishment
    from app.domain.models.appointment import Appointment


class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = (
        UniqueConstraint("establishment_id", "phone", name="uq_customer_establishment_phone"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    establishment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("establishments.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    establishment: Mapped["Establishment"] = relationship(back_populates="customers", lazy="raise")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="customer", lazy="raise")
