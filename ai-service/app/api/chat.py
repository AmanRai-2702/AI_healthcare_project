
import logging

from fastapi import APIRouter, HTTPException

from app.common.schemas import ChatRequest, ChatResponse
from app.common import conversation_store
from app.rag.pipeline import answer_question
from google.genai.errors import ServerError


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        # Create a new conversation or validate the existing one.
        if request.conversation_id is None:
            conversation_id = conversation_store.create_conversation(
                request.patient_id
            )
        else:
            conversation_id = request.conversation_id

            if not conversation_store.validate_conversation(
                conversation_id,
                request.patient_id,
            ):
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found.",
                )

        # Retrieve previous conversation messages.
        history = conversation_store.get_conversation_history(
            conversation_id=conversation_id,
            patient_id=request.patient_id,
            limit=20,
        )

        # Generate an answer using medical records and conversation history.
        result = answer_question(
            question=request.question,
            patient_id=request.patient_id,
            top_k=request.top_k,
            conversation_history=history,
        )

        # Save the current user question and assistant response.
        conversation_store.save_message(
            conversation_id=conversation_id,
            patient_id=request.patient_id,
            role="user",
            content=request.question,
        )

        conversation_store.save_message(
            conversation_id=conversation_id,
            patient_id=request.patient_id,
            role="assistant",
            content=result["answer"],
        )

        # Include conversation ID in the API response.
        result["conversation_id"] = conversation_id

        return result
    except HTTPException:
        raise
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except ServerError:
        logger.exception("Gemini service is temporarily unavailable")
        raise HTTPException(
            status_code=503,
            detail="AI service is temporarily unavailable. Please try again.",
        )
    except Exception:
        logger.exception("Unexpected error while processing chat request")

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the chat request.",
        )
