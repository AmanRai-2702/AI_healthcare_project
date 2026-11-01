from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


DoctorPatientStatus = Literal["pending", "active", "revoked"]


class DoctorPatientRequest(BaseModel):
    patient_id: UUID


class DoctorPatientStatusUpdate(BaseModel):
    status: Literal["active", "revoked"]


class DoctorPatientResponse(BaseModel):
    id: UUID
    doctor_id: UUID
    patient_id: UUID
    status: DoctorPatientStatus
    granted_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DoctorPatientListResponse(BaseModel):
    total: int
    relationships: list[DoctorPatientResponse]