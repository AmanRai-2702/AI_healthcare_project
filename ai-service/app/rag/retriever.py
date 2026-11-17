
import json

import chromadb

from app.rag.embeddings import (
    create_embeddings,
    create_query_embedding,
)


# Create a local database for storing document chunks.
client = chromadb.PersistentClient(path="data/chroma")

collection = client.get_or_create_collection(
    name="medfusion_demo",
    metadata={"hnsw:space": "cosine"},
)


def store_chunks(chunks):
    """Store document chunks, embeddings, and metadata."""

    if not chunks:
        return

    ids = [chunk["chunk_id"] for chunk in chunks]
    texts = [chunk["text"] for chunk in chunks]

    embeddings = create_embeddings(texts)

    metadata = []

    for chunk in chunks:
        item = {
            "patient_id": chunk["patient_id"],
            "source_id": chunk["source_id"],
            "source_type": chunk["source_type"],
            "chunk_index": chunk["chunk_index"],
            "findings": json.dumps(chunk.get("findings", [])),
        }

        # ChromaDB does not accept None metadata values.
        if chunk.get("document_name") is not None:
            item["document_name"] = chunk["document_name"]

        if chunk.get("clinical_date") is not None:
            item["clinical_date"] = chunk["clinical_date"]

        metadata.append(item)

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadata,
    )


def search_chunks(question, patient_id, top_k=3):
    """Find relevant chunks belonging to one patient."""

    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question cannot be empty")

    if not isinstance(patient_id, str) or not patient_id.strip():
        raise ValueError("Patient ID cannot be empty")

    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    if collection.count() == 0:
        return []

    question_embedding = create_query_embedding(question)

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k,
        where={"patient_id": patient_id},
    )

    matches = []

    for i, text in enumerate(results["documents"][0]):
        item_metadata = results["metadatas"][0][i]

        # Convert stored JSON findings back into a Python list.
        item_metadata["findings"] = json.loads(
            item_metadata.get("findings", "[]")
        )

        matches.append({
            "text": text,
            "metadata": item_metadata,
            "distance": results["distances"][0][i],
        })

    return matches
