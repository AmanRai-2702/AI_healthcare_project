
from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="Multimodal AI-Based Healthcare System",
    version="1.0.0",
)

app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
)


@app.get("/", tags=["Root"])
def root():
    return {
        "application": settings.APP_NAME,
        "message": "Welcome to MedFusion API",
        "docs": "/docs",
    }
