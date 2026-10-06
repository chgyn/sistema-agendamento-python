import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Uuid, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.domain.models.base import Base

if TYPE_CHECKING:
    from app.domain.models.establishment import Establishment


class UserRole(StrEnum):
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    establishment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("establishments.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role_enum", native_enum=False),
        default=UserRole.OPERATOR,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    establishment: Mapped["Establishment"] = relationship(back_populates="users", lazy="raise")
