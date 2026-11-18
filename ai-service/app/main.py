
from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.api.conversations import router as conversations_router


app = FastAPI(
    title="MedFusion AI Service",
    description="AI processing, RAG, and multimodal analysis",
    version="0.1.0",
)

app.include_router(chat_router)
app.include_router(conversations_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "medfusion-ai-service",
    }
