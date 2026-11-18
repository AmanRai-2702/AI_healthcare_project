from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


MedicalRecordType = Literal[
    "lab_result",
    "prescription",
    "diagnosis",
    "imaging_finding",
    "doctor_note",
    "other",
]


class MedicalRecordCreate(BaseModel):
    patient_id: UUID
    source_document_id: UUID | None = None
    record_type: MedicalRecordType
    structured_data: dict[str, Any] = Field(default_factory=dict)
    recorded_at: datetime | None = None


class MedicalRecordUpdate(BaseModel):
    structured_data: dict[str, Any] | None = None
    recorded_at: datetime | None = None


class MedicalRecordResponse(BaseModel):
    id: UUID
    patient_id: UUID
    source_document_id: UUID | None = None
    record_type: MedicalRecordType
    structured_data: dict[str, Any]
    recorded_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MedicalHistoryResponse(BaseModel):
    patient_id: UUID
    total_records: int
    records: list[MedicalRecordResponse]