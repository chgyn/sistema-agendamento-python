from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerBase(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    phone: str = Field(min_length=8, max_length=30)
    email: EmailStr | None = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    phone: str | None = Field(default=None, min_length=8, max_length=30)
    email: EmailStr | None = None


class CustomerResponse(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    establishment_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
