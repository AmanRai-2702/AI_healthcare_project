
from app.rag.retriever import search_chunks
from app.rag.prompts import build_rag_prompt
#from app.llm.gemini_client import generate_response
from app.llm.openrouter_client import generate_response



def answer_question(
    question: str,
    patient_id: str,
    top_k: int = 3,
    conversation_history: list[dict] | None = None,
) -> dict:
    """Retrieve patient-specific records and generate a grounded answer."""

    if not question.strip():
        raise ValueError("Question cannot be empty")

    if not patient_id.strip():
        raise ValueError("Patient ID cannot be empty")

    # Retrieve relevant records for this patient only.
    results = search_chunks(
        question=question,
        patient_id=patient_id,
        top_k=top_k,
    )

    # No medical context means no generated clinical answer.
    if not results:
        return {
            "question": question,
            "answer": (
                "I could not find relevant information in this patient's "
                "available records."
            ),
            "sources": [],
            "has_context": False,
        }

    context_parts = []
    sources = []

    for result in results:
        metadata = result["metadata"]

        context_entry = (
            f"Record text: {result['text']}\n"
            f"Source ID: {metadata.get('source_id', 'unknown')}\n"
            f"Source type: {metadata.get('source_type', 'unknown')}\n"
        )

        if metadata.get("document_name"):
            context_entry += (
                f"Document name: {metadata['document_name']}\n"
            )

        if metadata.get("clinical_date"):
            context_entry += (
                f"Clinical date: {metadata['clinical_date']}\n"
            )

        if metadata.get("findings"):
            context_entry += (
                f"Structured findings: {metadata['findings']}\n"
            )

        context_parts.append(context_entry)

        sources.append({
            "source_id": metadata["source_id"],
            "source_type": metadata["source_type"],
        })

    context = "\n\n".join(context_parts)

    # Include previous conversation for follow-up understanding.
    prompt = build_rag_prompt(
        question=question,
        context=context,
        conversation_history=conversation_history,
    )

    answer = generate_response(prompt)

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "has_context": True,
    }
