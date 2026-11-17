
from __future__ import annotations

import json
from typing import Any

from app.rag.chunking import chunk_text


def ingest_text(
    text: str,
    source_id: str,
    patient_id: str,
    source_type: str = "medical_note",
    chunk_size: int = 800,
    overlap: int = 120,
    document_name: str | None = None,
    clinical_date: str | None = None,
    findings: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Convert medical text into chunks with traceable metadata."""

    if not isinstance(source_id, str) or not source_id.strip():
        raise ValueError("source_id must not be empty")

    if not isinstance(patient_id, str) or not patient_id.strip():
        raise ValueError("patient_id must not be empty")

    if not isinstance(source_type, str) or not source_type.strip():
        raise ValueError("source_type must not be empty")

    if findings is not None:
        if not isinstance(findings, list):
            raise ValueError("findings must be a list")

        if not all(isinstance(item, dict) for item in findings):
            raise ValueError("Each finding must be a dictionary")

    chunks = chunk_text(
        text=text,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    records = []

    for index, chunk in enumerate(chunks):
        record = {
            "chunk_id": f"{source_id}-chunk-{index:04d}",
            "source_id": source_id,
            "patient_id": patient_id,
            "source_type": source_type,
            "chunk_index": index,
            "text": chunk,
            "document_name": document_name,
            "clinical_date": clinical_date,
            "findings": findings or [],
        }

        records.append(record)

    return records
