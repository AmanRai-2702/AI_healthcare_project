
import logging

from fastapi import APIRouter, HTTPException, Query

from app.common import conversation_store


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.get("/")
def list_conversations(
    patient_id: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List conversations belonging to a patient."""

    try:
        conversations = conversation_store.list_conversations(
            patient_id=patient_id,
            limit=limit,
            offset=offset,
        )

        return {
            "conversations": conversations,
            "count": len(conversations),
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception:
        logger.exception("Failed to list conversations")
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve conversations.",
        )


@router.get("/{conversation_id}")
def get_conversation(
    conversation_id: str,
    patient_id: str = Query(..., min_length=1),
    limit: int = Query(100, ge=1, le=500),
):
    """Retrieve messages from a patient's conversation."""

    try:
        history = conversation_store.get_conversation_history(
            conversation_id=conversation_id,
            patient_id=patient_id,
            limit=limit,
        )

        return {
            "conversation_id": conversation_id,
            "messages": history,
            "count": len(history),
        }

    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    except Exception:
        logger.exception("Failed to retrieve conversation")
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve conversation.",
        )


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    patient_id: str = Query(..., min_length=1),
):
    """Delete a patient's conversation and its messages."""

    try:
        deleted = conversation_store.delete_conversation(
            conversation_id=conversation_id,
            patient_id=patient_id,
        )

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found.",
            )

        return {
            "message": "Conversation deleted successfully.",
            "conversation_id": conversation_id,
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception:
        logger.exception("Failed to delete conversation")
        raise HTTPException(
            status_code=500,
            detail="Unable to delete conversation.",
        )
