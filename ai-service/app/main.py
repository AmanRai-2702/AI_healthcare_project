
from fastapi import FastAPI

app = FastAPI(
    title="MedFusion AI Service",
    description="AI processing, RAG, and multimodal analysis",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "medfusion-ai-service",
    }
