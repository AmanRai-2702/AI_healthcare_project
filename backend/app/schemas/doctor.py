from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DoctorBase(BaseModel):
    specialization: str | None = Field(default=None, max_length=150)
    license_number: str | None = Field(default=None, max_length=100)
    organization: str | None = Field(default=None, max_length=255)


class DoctorCreate(DoctorBase):
    user_id: UUID


class DoctorUpdate(BaseModel):
    specialization: str | None = Field(default=None, max_length=150)
    license_number: str | None = Field(default=None, max_length=100)
    organization: str | None = Field(default=None, max_length=255)


class DoctorResponse(DoctorBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)