
from __future__ import annotations


def chunk_text(
    text: str,
    chunk_size: int = 800,
    overlap: int = 120,
) -> list[str]:
    """Split text into overlapping chunks, preserving word boundaries."""

    if not text or not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    words = text.split()
    chunks: list[str] = []
    start = 0

    while start < len(words):
        end = start
        current_length = 0

        while end < len(words):
            word_length = len(words[end])
            added_length = word_length if end == start else word_length + 1

            if current_length + added_length > chunk_size:
                break

            current_length += added_length
            end += 1

        # Always consume at least one word, even if that word is very long.
        if end == start:
            end += 1

        chunks.append(" ".join(words[start:end]))

        if end >= len(words):
            break

        # Keep approximately `overlap` characters from the previous chunk.
        next_start = end
        overlap_length = 0

        while next_start > start:
            previous_word = words[next_start - 1]
            added_length = len(previous_word) + (
                1 if overlap_length > 0 else 0
            )

            if overlap_length + added_length > overlap:
                break

            overlap_length += added_length
            next_start -= 1

        start = next_start if next_start > start else end

    return chunks
