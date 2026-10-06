from datetime import date, datetime
from decimal import Decimal
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EstablishmentPublicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    phone: str
    email: str
    address: str | None
    settings: dict


class ServicePublicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    duration_minutes: int
    price: Decimal


class ProfessionalPublicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    bio: str | None


class TimeSlot(BaseModel):
    start_time: str = Field(description="Horário no formato HH:MM")
    end_time: str = Field(description="Horário no formato HH:MM")
    is_available: bool


class AvailabilityResponse(BaseModel):
    date: date
    professional_id: uuid.UUID
    service_id: uuid.UUID
    slots: list[TimeSlot]


class PublicAppointmentCreateRequest(BaseModel):
    service_id: uuid.UUID
    professional_id: uuid.UUID
    start_datetime: datetime
    customer_name: str = Field(min_length=2, max_length=150)
    customer_phone: str = Field(min_length=8, max_length=30, description="Celular ou WhatsApp do cliente")
    customer_email: EmailStr | None = None
    notes: str | None = Field(default=None, max_length=500)


class AppointmentPublicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    start_datetime: datetime
    end_datetime: datetime
    status: str
    service_name: str
    professional_name: str
    message: str = "Agendamento realizado com sucesso!"
