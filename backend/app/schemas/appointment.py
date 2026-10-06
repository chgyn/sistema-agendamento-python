from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict, Field
from app.domain.models.appointment import AppointmentStatus


class AppointmentCreateInternal(BaseModel):
    customer_id: uuid.UUID
    professional_id: uuid.UUID
    service_id: uuid.UUID
    start_datetime: datetime
    notes: str | None = Field(default=None, max_length=500)


class AppointmentStatusUpdateRequest(BaseModel):
    status: AppointmentStatus


class AppointmentCancelRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=255, description="Motivo do cancelamento")


class AppointmentDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    establishment_id: uuid.UUID
    customer_id: uuid.UUID
    customer_name: str
    customer_phone: str
    professional_id: uuid.UUID
    professional_name: str
    service_id: uuid.UUID
    service_name: str
    start_datetime: datetime
    end_datetime: datetime
    status: AppointmentStatus
    cancellation_reason: str | None = None
    cancelled_at: datetime | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
