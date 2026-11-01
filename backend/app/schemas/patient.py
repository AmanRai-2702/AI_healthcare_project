from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PatientBase(BaseModel):
    date_of_birth: date | None = None
    sex: str | None = Field(default=None, max_length=30)


class PatientCreate(PatientBase):
    user_id: UUID


class PatientUpdate(BaseModel):
    date_of_birth: date | None = None
    sex: str | None = Field(default=None, max_length=30)


class PatientResponse(PatientBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)