from datetime import datetime, time
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class WorkingHourBase(BaseModel):
    day_of_week: int = Field(ge=0, le=6, description="0=Segunda, 6=Domingo")
    start_time: time
    end_time: time
    break_start_time: time | None = None
    break_end_time: time | None = None
    is_active: bool = True


class WorkingHourCreate(WorkingHourBase):
    pass


class WorkingHourResponse(WorkingHourBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    professional_id: uuid.UUID


class UnavailabilityCreate(BaseModel):
    start_datetime: datetime
    end_datetime: datetime
    reason: str | None = Field(default=None, max_length=255)


class UnavailabilityResponse(UnavailabilityCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    professional_id: uuid.UUID


class ProfessionalBase(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    bio: str | None = Field(default=None, max_length=500)


class ProfessionalCreate(ProfessionalBase):
    service_ids: list[uuid.UUID] = Field(default_factory=list)
    working_hours: list[WorkingHourCreate] = Field(default_factory=list)


class ProfessionalUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    bio: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None
    service_ids: list[uuid.UUID] | None = None


class ProfessionalResponse(ProfessionalBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    establishment_id: uuid.UUID
    is_active: bool
    service_ids: list[uuid.UUID] = Field(default_factory=list)
    working_hours: list[WorkingHourResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
