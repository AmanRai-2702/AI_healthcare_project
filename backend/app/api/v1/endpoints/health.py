
from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "application": "MedFusion",
        "message": "Backend API is running successfully",
    }
