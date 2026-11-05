
"""End-to-end medical document processing pipeline."""

from pathlib import Path
from typing import Any

from app.document_processing.loader import (
    DocumentLoadError,
    load_document,
)
from app.document_processing.medical_extraction import (
    extract_medical_findings,
)
from app.document_processing.ocr import (
    OCRProcessingError,
    extract_text,
)
from app.document_processing.text_cleaning import clean_medical_text


def process_medical_document(
    file_path: str | Path,
    language: str = "eng",
) -> dict[str, Any]:
    """
    Load a medical document, extract its text, clean it, and find measurements.

    Returns a dictionary containing processing status, extracted text,
    findings, and basic file metadata.
    """
    path = Path(file_path)

    # Validate the file using the existing loader.
    try:
        document = load_document(path)
    except DocumentLoadError as exc:
        return {
            "status": "error",
            "filename": path.name,
            "error": str(exc),
            "text": "",
            "findings": [],
        }

    try:
        raw_text = extract_text(path, language=language)
    except (OCRProcessingError, OSError) as exc:
        return {
            "status": "error",
            "filename": document["filename"],
            "error": str(exc),
            "text": "",
            "findings": [],
        }

    cleaned_text = clean_medical_text(raw_text)
    findings = extract_medical_findings(cleaned_text)

    return {
        "status": "success" if cleaned_text else "no_text_detected",
        "filename": document["filename"],
        "file_type": document["extension"],
        "size_bytes": document["size_bytes"],
        "text": cleaned_text,
        "findings": findings,
    }
