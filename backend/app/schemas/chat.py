from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChatMessageCreate(BaseModel):
    conversation_id: UUID | None = None
    message: str = Field(min_length=1, max_length=5000)


class ChatSourceReference(BaseModel):
    source_type: Literal[
        "medical_record",
        "document",
        "analysis",
    ]
    source_id: UUID
    title: str | None = None
    excerpt: str | None = None


class ChatMessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: Literal["user", "assistant", "system"]
    content: str
    source_references: list[ChatSourceReference] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationCreate(BaseModel):
    title: str | None = Field(default=None, max_length=255)


class ConversationResponse(BaseModel):
    id: UUID
    patient_id: UUID
    title: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatResponse(BaseModel):
    conversation_id: UUID
    message: ChatMessageResponse
    disclaimer: str = (
        "This AI-generated response is for informational purposes "
        "and does not replace professional medical advice or diagnosis. "
        "Consult a qualified healthcare professional."
    )


class ConversationHistoryResponse(BaseModel):
    conversation: ConversationResponse
    messages: list[ChatMessageResponse]