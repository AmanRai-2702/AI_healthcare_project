
from sentence_transformers import SentenceTransformer

# Load a small model for converting text into embeddings
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def create_embeddings(texts):
    """Convert a list of texts into embedding vectors."""

    if not texts:
        return []

    embeddings = model.encode(texts, normalize_embeddings=True)

    return embeddings.tolist()


def create_query_embedding(question):
    """Convert a user's question into an embedding."""

    if not question.strip():
        raise ValueError("Question cannot be empty")

    return create_embeddings([question])[0]
