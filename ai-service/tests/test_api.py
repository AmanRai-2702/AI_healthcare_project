
from fastapi.testclient import TestClient

from app.main import app
import app.api.documents as documents_api

import numpy as np
import app.api.images as images_api

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_document_upload_success(monkeypatch):
    def fake_process(file_path):
        return {
            "status": "success",
            "filename": "temporary.pdf",
            "file_type": ".pdf",
            "size_bytes": 100,
            "text": "Hemoglobin: 13.5 g/dL",
            "findings": [],
        }

    monkeypatch.setattr(
        documents_api,
        "process_medical_document",
        fake_process,
    )

    response = client.post(
        "/documents/process",
        files={
            "file": (
                "LabReport.pdf",
                b"%PDF-1.4 fake test content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["filename"] == "LabReport.pdf"
    assert response.json()["status"] == "success"


def test_unsupported_file_rejected():
    response = client.post(
        "/documents/process",
        files={
            "file": ("report.exe", b"test", "application/octet-stream")
        },
    )

    assert response.status_code == 400


def test_empty_file_rejected():
    response = client.post(
        "/documents/process",
        files={
            "file": ("report.pdf", b"", "application/pdf")
        },
    )

    assert response.status_code == 400


def test_xray_preprocess_api_success(monkeypatch):
    def fake_preprocess(image_path, image_size, channels):
        return np.zeros((3, 224, 224), dtype=np.float32)

    monkeypatch.setattr(
        images_api,
        "preprocess_xray",
        fake_preprocess,
    )

    response = client.post(
        "/images/preprocess",
        files={
            "file": (
                "chest-example.png",
                b"fake image content",
                "image/png",
            )
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["filename"] == "chest-example.png"
    assert data["image_shape"] == [3, 224, 224]
    assert data["diagnosis"] is None


def test_xray_preprocess_api_invalid_image(monkeypatch):
    def fake_preprocess(*args, **kwargs):
        raise ValueError("Invalid image.")

    monkeypatch.setattr(
        images_api,
        "preprocess_xray",
        fake_preprocess,
    )

    response = client.post(
        "/images/preprocess",
        files={
            "file": (
                "broken.png",
                b"fake image content",
                "image/png",
            )
        },
    )

    assert response.status_code == 422