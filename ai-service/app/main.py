
from fastapi import FastAPI

from app.api.chat import router as chat_router


app = FastAPI(
    title="MedFusion AI Service",
    description="AI processing, RAG, and multimodal analysis",
    version="0.1.0",
)


app.include_router(chat_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "medfusion-ai-service",
    }
