from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


AnalysisType = Literal[
    "ocr",
    "nlp",
    "xray",
    "multimodal",
]

AnalysisStatus = Literal[
    "pending",
    "processing",
    "completed",
    "failed",
]


class AnalysisCreate(BaseModel):
    document_id: UUID
    analysis_type: AnalysisType
    model_name: str | None = Field(default=None, max_length=150)


class AnalysisResponse(BaseModel):
    id: UUID
    document_id: UUID
    analysis_type: AnalysisType
    status: AnalysisStatus
    model_name: str | None = None
    summary: str | None = None
    result_data: dict[str, Any] | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalysisStatusResponse(BaseModel):
    analysis_id: UUID
    status: AnalysisStatus
    message: str | None = None


class AnalysisResultResponse(BaseModel):
    analysis_id: UUID
    analysis_type: AnalysisType
    status: AnalysisStatus
    summary: str | None = None
    findings: dict[str, Any] | None = None
    disclaimer: str = (
        "AI-generated information is for clinical decision support only "
        "and is not a confirmed medical diagnosis. A qualified clinician "
        "must review and interpret the findings."
    )