from datetime import datetime
from decimal import Decimal
import uuid
from pydantic import BaseModel, ConfigDict, Field


class ServiceBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    duration_minutes: int = Field(gt=0, le=480, description="Duração em minutos (máx 8h)")
    price: Decimal = Field(ge=0, decimal_places=2, max_digits=10)


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    duration_minutes: int | None = Field(default=None, gt=0, le=480)
    price: Decimal | None = Field(default=None, ge=0, decimal_places=2, max_digits=10)
    is_active: bool | None = None


class ServiceResponse(ServiceBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    establishment_id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
