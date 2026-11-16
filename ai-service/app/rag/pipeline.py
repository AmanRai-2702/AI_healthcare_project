
from app.rag.retriever import search_chunks


def answer_question(question: str, patient_id: str, top_k: int = 3) -> dict:
    """Retrieve patient-specific records and prepare an evidence-based response."""

    if not question.strip():
        raise ValueError("Question cannot be empty")

    if not patient_id.strip():
        raise ValueError("Patient ID cannot be empty")

    # Retrieve relevant records for this patient only
    results = search_chunks(
        question=question,
        patient_id=patient_id,
        top_k=top_k,
    )

    # Handle cases where no relevant records were found
    if not results:
        return {
            "question": question,
            "answer": "I could not find relevant information in this patient's available records.",
            "sources": [],
            "has_context": False,
        }

    # Prepare an answer using the retrieved text
    context_parts = []
    sources = []

    for result in results:
        context_parts.append(result["text"])

        sources.append({
            "source_id": result["metadata"]["source_id"],
            "source_type": result["metadata"]["source_type"],
        })

    answer = (
        "Relevant information found in the patient's records:\n"
        + "\n".join(context_parts)
    )

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "has_context": True,
    }
