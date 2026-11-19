
"""FastAPI endpoint for medical document processing."""

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.document_processing.pipeline import process_medical_document

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/process")
async def process_document(file: UploadFile = File(...)):
    """Upload a medical document and extract its text and findings."""

    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    suffix = Path(file.filename).suffix.lower()

    if suffix not in {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported document format.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 20 MB size limit.",
        )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False,
        ) as temp_file:
            temp_file.write(content)
            temp_path = Path(temp_file.name)

        result = process_medical_document(str(temp_path))
        result["filename"] = Path(file.filename).name
        return result

    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Document processing failed: {exc}",
        ) from exc

    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()
