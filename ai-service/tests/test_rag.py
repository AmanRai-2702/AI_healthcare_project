
import pytest

from app.rag.chunking import chunk_text
from app.rag.ingestion import ingest_text
from app.rag.retriever import store_chunks, search_chunks
from app.rag.pipeline import answer_question


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

def test_retriever_finds_relevant_information():
    """Check that a question retrieves a relevant synthetic record."""

    chunks = ingest_text(
        text=(
            "Synthetic note: The patient reported seasonal allergies. "
            "The clinician recommended discussing allergy treatment "
            "options at the next appointment."
        ),
        source_id="rag-test-source-001",
        patient_id="rag-test-patient-001",
    )

    store_chunks(chunks)

    results = search_chunks(
        question="What does the note say about allergies?",
        patient_id="rag-test-patient-001",
    )

    assert len(results) > 0
    assert "allerg" in results[0]["text"].lower()


def test_retriever_does_not_return_another_patients_records():
    """Check that patient filtering excludes unrelated records."""

    chunks = ingest_text(
        text="Synthetic note: The patient reported a headache.",
        source_id="rag-test-source-002",
        patient_id="rag-test-patient-002",
    )

    store_chunks(chunks)

    results = search_chunks(
        question="What symptom was reported?",
        patient_id="rag-test-patient-001",
    )

    assert all(
        result["metadata"]["patient_id"] == "rag-test-patient-001"
        for result in results
    )
    assert all(
        result["metadata"]["source_id"] != "rag-test-source-002"
        for result in results
    )





def test_answer_question_returns_relevant_context():
    chunks = ingest_text(
        text=(
            "Synthetic note: The patient reported seasonal allergies. "
            "The clinician discussed allergy treatment options."
        ),
        source_id="pipeline-test-001",
        patient_id="pipeline-patient-001",
    )

    store_chunks(chunks)

    result = answer_question(
        question="What does the note say about allergies?",
        patient_id="pipeline-patient-001",
    )

    assert result["has_context"] is True
    assert "allerg" in result["answer"].lower()
    assert len(result["sources"]) > 0


def test_answer_question_returns_no_context_for_unknown_patient():
    result = answer_question(
        question="What symptoms were reported?",
        patient_id="patient-with-no-records-999",
    )

    assert result["has_context"] is False
    assert result["sources"] == []
    

def test_ingestion_preserves_medical_findings():
    findings = [
        {
            "name": "hemoglobin",
            "value": 13.5,
            "unit": "g/dL",
        },
        {
            "name": "glucose",
            "value": 105,
            "unit": "mg/dL",
        },
    ]

    records = ingest_text(
        text="Hemoglobin: 13.5 g/dL. Glucose: 105 mg/dL.",
        source_id="lab-report-001",
        patient_id="patient-001",
        source_type="lab_report",
        document_name="blood_report.pdf",
        clinical_date="2026-11-15",
        findings=findings,
    )

    assert len(records) == 1
    assert records[0]["document_name"] == "blood_report.pdf"
    assert records[0]["clinical_date"] == "2026-11-15"
    assert records[0]["source_type"] == "lab_report"
    assert records[0]["findings"] == findings


def test_retriever_preserves_medical_metadata():
    findings = [
        {
            "name": "hemoglobin",
            "value": 13.5,
            "unit": "g/dL",
        }
    ]

    chunks = ingest_text(
        text="Hemoglobin: 13.5 g/dL.",
        source_id="metadata-report-001",
        patient_id="metadata-patient-001",
        source_type="lab_report",
        document_name="blood_report.pdf",
        clinical_date="2026-11-15",
        findings=findings,
    )

    store_chunks(chunks)

    results = search_chunks(
        question="What is the hemoglobin value?",
        patient_id="metadata-patient-001",
    )

    assert len(results) > 0

    metadata = results[0]["metadata"]

    assert metadata["source_id"] == "metadata-report-001"
    assert metadata["source_type"] == "lab_report"
    assert metadata["document_name"] == "blood_report.pdf"
    assert metadata["clinical_date"] == "2026-11-15"
    assert metadata["findings"] == findings
