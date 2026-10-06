from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.domain.models.user import UserRole


class UserBase(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    role: UserRole = UserRole.OPERATOR


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=100)
    establishment_id: uuid.UUID | None = None


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    email: EmailStr | None = None
    role: UserRole | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=6, max_length=100)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    establishment_id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
