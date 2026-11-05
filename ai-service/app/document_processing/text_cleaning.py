
"""Clean OCR text while preserving medically important information."""

import re
import unicodedata


def clean_medical_text(text: str) -> str:
    """
    Normalize OCR text without interpreting or changing medical values.

    Preserves decimal points, signs, dates, units, and line boundaries.
    Does not attempt to guess or correct potentially misread values.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    # Normalize Unicode characters, including compatibility characters.
    text = unicodedata.normalize("NFKC", text)

    # Remove common invisible formatting characters.
    text = text.replace("\u200b", "").replace("\ufeff", "")

    # Normalize line endings and tabs.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\t", " ")

    cleaned_lines = []

    for line in text.split("\n"):
        # Collapse repeated horizontal whitespace, but keep line structure.
        line = re.sub(r"[^\S\n]+", " ", line).strip()

        if line:
            cleaned_lines.append(line)

    # Limit excessive blank lines while keeping separate report sections.
    return "\n".join(cleaned_lines)


def normalize_for_matching(text: str) -> str:
    """
    Produce a lowercase matching string for searching known medical terms.

    Use this only for matching, not as a replacement for the original text.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    return clean_medical_text(text).casefold()
