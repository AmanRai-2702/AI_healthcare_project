from datetime import datetime
from uuid import UUID
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


DocumentType = Literal[
    "prescription",
    "lab_report",
    "medical_report",
    "chest_xray",
    "other",
]

ProcessingStatus = Literal[
    "uploaded",
    "pending",
    "processing",
    "completed",
    "failed",
]


class DocumentResponse(BaseModel):
    id: UUID
    patient_id: UUID
    uploaded_by: UUID

    document_type: DocumentType
    original_filename: str
    mime_type: str
    file_size_bytes: int

    storage_provider: str
    processing_status: ProcessingStatus

    clinical_date: datetime | None = None
    uploaded_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentProcessingStatus(BaseModel):
    document_id: UUID
    processing_status: ProcessingStatus
    message: str | None = None


class DocumentMetadataUpdate(BaseModel):
    document_type: DocumentType | None = None
    clinical_date: datetime | None = None