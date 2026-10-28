
import pytest

from app.rag.chunking import chunk_text
from app.rag.ingestion import ingest_text


def test_chunk_text_returns_empty_for_empty_input():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_chunk_text_splits_long_text():
    text = " ".join(["medical"] * 100)

    chunks = chunk_text(text, chunk_size=100, overlap=20)

    assert len(chunks) > 1
    assert all(chunks for chunks in chunks)
    assert all(len(chunk) <= 100 for chunk in chunks)


def test_chunk_text_rejects_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_text("sample text", chunk_size=100, overlap=100)


def test_ingestion_preserves_source_metadata():
    records = ingest_text(
        text="Synthetic patient note: routine follow-up.",
        source_id="demo-report-001",
        patient_id="demo-patient-001",
        source_type="medical_note",
    )

    assert len(records) == 1
    assert records[0]["source_id"] == "demo-report-001"
    assert records[0]["patient_id"] == "demo-patient-001"
    assert records[0]["chunk_index"] == 0
    assert "routine follow-up" in records[0]["text"]


def test_ingestion_rejects_missing_patient_id():
    with pytest.raises(ValueError):
        ingest_text(
            text="Synthetic medical note",
            source_id="demo-report-001",
            patient_id="",
        )
