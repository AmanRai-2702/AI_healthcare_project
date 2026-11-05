"""Main FastAPI application."""

from fastapi import FastAPI

from app.api import documents, health , images

app = FastAPI(
    title="MedFusion AI Service",
    description="Medical document processing and AI service",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(documents.router)
app.include_router(images.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to MedFusion AI Service",
        "docs": "/docs",
    }