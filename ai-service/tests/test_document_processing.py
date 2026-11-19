
from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont

from app.document_processing.loader import (
    DocumentLoadError,
    load_document,
)
from app.document_processing.medical_extraction import (
    extract_medical_findings,
)
from app.document_processing.pipeline import process_medical_document
from app.document_processing.text_cleaning import (
    clean_medical_text,
    normalize_for_matching,
)


def create_sample_image(path: Path) -> None:
    """Create a synthetic image for testing document loading."""
    image = Image.new("RGB", (1400, 400), "white")
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 38)
    except OSError:
        font = ImageFont.load_default(size=38)

    draw.text((40, 40), "MEDFUSION SAMPLE LAB REPORT", fill="black", font=font)
    draw.text((40, 140), "Hemoglobin: 13.5 g/dL", fill="black", font=font)
    draw.text((40, 240), "Glucose: 95 mg/dL", fill="black", font=font)

    image.save(path)


def test_loader_accepts_valid_png(tmp_path):
    image_path = tmp_path / "sample.png"
    create_sample_image(image_path)

    result = load_document(image_path)

    assert result["filename"] == "sample.png"
    assert result["extension"] == ".png"
    assert result["size_bytes"] > 0
    assert result["content"].startswith(b"\x89PNG\r\n\x1a\n")


def test_loader_rejects_unsupported_extension(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_text("not an image", encoding="utf-8")

    with pytest.raises(DocumentLoadError):
        load_document(path)


def test_loader_rejects_empty_file(tmp_path):
    path = tmp_path / "empty.png"
    path.write_bytes(b"")

    with pytest.raises(DocumentLoadError):
        load_document(path)


def test_cleaning_preserves_medical_values():
    result = clean_medical_text(
        "Hemoglobin:   13.5 g/dL\r\nGlucose:\t95 mg/dL"
    )

    assert "13.5 g/dL" in result
    assert "95 mg/dL" in result
    assert "\t" not in result


def test_normalize_for_matching_is_case_insensitive():
    assert normalize_for_matching("HEMOGLOBIN") == "hemoglobin"


def test_extract_medical_findings():
    findings = extract_medical_findings(
        "Hemoglobin: 13.5 g/dL\nGlucose: 95 mg/dL"
    )

    assert len(findings) == 2
    assert findings[0]["name"] == "hemoglobin"
    assert findings[0]["value"] == 13.5
    assert findings[0]["unit"] == "g/dL"
    assert findings[1]["name"] == "glucose"
    assert findings[1]["value"] == 95.0
    assert findings[1]["unit"] == "mg/dL"


def test_extractor_does_not_invent_missing_values():
    assert extract_medical_findings("Hemoglobin: not reported") == []


def test_pipeline_processes_synthetic_lab_image(tmp_path):
    image_path = tmp_path / "sample_lab.png"
    create_sample_image(image_path)

    result = process_medical_document(image_path)

    assert result["status"] == "success"
    assert any(
        item["name"] == "hemoglobin" and item["value"] == 13.5
        for item in result["findings"]
    )
    assert any(
        item["name"] == "glucose" and item["value"] == 95.0
        for item in result["findings"]
    )


def test_extractor_handles_value_without_separator():
    findings = extract_medical_findings("Hemoglobin 13.5 g/dL")

    assert len(findings) == 1
    assert findings[0]["name"] == "hemoglobin"
    assert findings[0]["value"] == 13.5
    assert findings[0]["unit"] == "g/dL"
