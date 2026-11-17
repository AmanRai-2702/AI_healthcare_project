
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    patient_id: str = Field(min_length=1)
    question: str = Field(min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)


class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: list[dict]
    has_context: bool
