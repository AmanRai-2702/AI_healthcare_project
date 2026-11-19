
import numpy as np
import pytest
from PIL import Image

from app.xray_analysis.preprocessing import (
    XRayPreprocessingError,
    preprocess_xray,
)


def create_test_image(path, size=(320, 240), color="gray"):
    image = Image.new("RGB", size, color=color)
    image.save(path)


def test_preprocess_grayscale_image(tmp_path):
    path = tmp_path / "sample_xray.png"
    create_test_image(path)

    result = preprocess_xray(path)

    assert result.shape == (1, 224, 224)
    assert result.dtype == np.float32
    assert np.all(result >= 0.0)
    assert np.all(result <= 1.0)


def test_preprocess_rgb_image(tmp_path):
    path = tmp_path / "sample_xray.png"
    create_test_image(path)

    result = preprocess_xray(path, image_size=(128, 128), channels=3)

    assert result.shape == (3, 128, 128)
    assert result.dtype == np.float32


def test_missing_file_is_rejected(tmp_path):
    with pytest.raises(XRayPreprocessingError):
        preprocess_xray(tmp_path / "missing.png")


def test_unsupported_extension_is_rejected(tmp_path):
    path = tmp_path / "report.pdf"
    path.write_bytes(b"not an image")

    with pytest.raises(XRayPreprocessingError):
        preprocess_xray(path)


def test_empty_file_is_rejected(tmp_path):
    path = tmp_path / "empty.png"
    path.write_bytes(b"")

    with pytest.raises(XRayPreprocessingError):
        preprocess_xray(path)


def test_corrupt_image_is_rejected(tmp_path):
    path = tmp_path / "corrupt.png"
    path.write_bytes(b"this is not a real image")

    with pytest.raises(XRayPreprocessingError):
        preprocess_xray(path)


def test_invalid_channel_count_is_rejected(tmp_path):
    path = tmp_path / "sample.png"
    create_test_image(path)

    with pytest.raises(XRayPreprocessingError):
        preprocess_xray(path, channels=2)


def test_invalid_image_size_is_rejected(tmp_path):
    path = tmp_path / "sample.png"
    create_test_image(path)

    with pytest.raises(XRayPreprocessingError):
        preprocess_xray(path, image_size=(0, 224))
