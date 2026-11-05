
"""Rule-based extraction of medical measurements from report text."""

import re
from typing import Any

from app.document_processing.text_cleaning import clean_medical_text


# Known measurement names and common aliases.
# This initial list is intentionally small; we can expand it later.
TEST_ALIASES = {
    "hemoglobin": ("hemoglobin", "haemoglobin", "hgb", "hb"),
    "glucose": ("glucose", "blood sugar"),
    "total cholesterol": ("total cholesterol", "cholesterol, total"),
    "platelets": ("platelets", "platelet count"),
    "creatinine": ("creatinine", "serum creatinine"),
    "white blood cell count": ("white blood cell count", "wbc count", "wbc"),
}

# Match a numeric result, including decimals and optional signs.
NUMBER_PATTERN = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)"

# Keep units explicit rather than guessing them.
UNIT_PATTERN = (
    r"(?:g/dL|mg/dL|mmol/L|µmol/L|umol/L|"
    r"10\^?\d+/L|10\^\d+/?L|"
    r"million/µL|million/uL|cells/µL|cells/uL|"
    r"mL/min(?:/1\.73m2)?|%|IU/L|U/L|fL|pg|g/L|mg/L)"
)


def _find_test_name(line: str) -> str | None:
    """Return the canonical test name if a known alias occurs in a line."""
    lowered = line.casefold()

    for canonical_name, aliases in TEST_ALIASES.items():
        for alias in sorted(aliases, key=len, reverse=True):
            pattern = rf"(?<!\w){re.escape(alias)}(?!\w)"
            if re.search(pattern, lowered):
                return canonical_name

    return None


def extract_medical_findings(text: str) -> list[dict[str, Any]]:
    """
    Extract recognized test names, numeric values, and explicitly written units.

    Each finding includes the source line so a reviewer can verify the result.
    This function does not determine whether a result is normal or abnormal.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    cleaned_text = clean_medical_text(text)
    findings: list[dict[str, Any]] = []

    for line in cleaned_text.splitlines():
        test_name = _find_test_name(line)

        if test_name is None:
            continue

        # First prefer a number after a colon or equals sign.
        separator_match = re.search(r"[:=]\s*(" + NUMBER_PATTERN + r")", line)

        # Otherwise, look for the first numeric token in the line.
        number_match = separator_match or re.search(NUMBER_PATTERN, line)

        if number_match is None:
            continue

        value_text = number_match.group(1)
        value = float(value_text)

        # Find an explicitly stated unit after the extracted number.
        remainder = line[number_match.end():]
        unit_match = re.match(
            r"\s*(" + UNIT_PATTERN + r")\b",
            remainder,
            flags=re.IGNORECASE,
        )

        unit = unit_match.group(1) if unit_match else None

        findings.append(
            {
                "name": test_name,
                "value": value,
                "value_text": value_text,
                "unit": unit,
                "source_text": line,
            }
        )

    return findings
