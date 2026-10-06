from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EstablishmentBase(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    slug: str = Field(min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    email: EmailStr
    phone: str = Field(min_length=8, max_length=30)
    address: str | None = Field(default=None, max_length=255)
    settings: dict = Field(default_factory=dict)


class EstablishmentCreate(EstablishmentBase):
    pass


class EstablishmentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=8, max_length=30)
    address: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    settings: dict | None = None


class EstablishmentResponse(EstablishmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
