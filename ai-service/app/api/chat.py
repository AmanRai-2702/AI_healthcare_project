
from fastapi import APIRouter, HTTPException

from app.common.schemas import ChatRequest, ChatResponse
from app.rag.pipeline import answer_question


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        result = answer_question(
            question=request.question,
            patient_id=request.patient_id,
            top_k=request.top_k,
        )

        return result

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the chat request.",
        )
