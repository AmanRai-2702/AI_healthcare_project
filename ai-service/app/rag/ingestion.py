
from __future__ import annotations

from typing import Any

from app.rag.chunking import chunk_text


def ingest_text(
    text: str,
    source_id: str,
    patient_id: str,
    source_type: str = "medical_note",
    chunk_size: int = 800,
    overlap: int = 120,
) -> list[dict[str, Any]]:
    """Convert source text into chunks with traceable metadata.

    This function does not store documents or generate embeddings yet.
    """

    if not source_id.strip():
        raise ValueError("source_id must not be empty")

    if not patient_id.strip():
        raise ValueError("patient_id must not be empty")

    chunks = chunk_text(
        text=text,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    return [
        {
            "chunk_id": f"{source_id}-chunk-{index:04d}",
            "source_id": source_id,
            "patient_id": patient_id,
            "source_type": source_type,
            "chunk_index": index,
            "text": chunk,
        }
        for index, chunk in enumerate(chunks)
    ]
