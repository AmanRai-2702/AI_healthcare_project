
"""Input validation and preprocessing for chest X-ray images."""

from pathlib import Path

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError


SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024
MAX_IMAGE_PIXELS = 40_000_000


class XRayPreprocessingError(ValueError):
    """Raised when an X-ray image cannot be safely preprocessed."""


def preprocess_xray(
    image_path: str | Path,
    image_size: tuple[int, int] = (224, 224),
    channels: int = 1,
) -> np.ndarray:
    """
    Load and preprocess a chest X-ray image.

    Args:
        image_path: Path to a supported image file.
        image_size: Output size as (height, width).
        channels: Output channels: 1 for grayscale or 3 for RGB.

    Returns:
        A float32 NumPy array in channel-first format:
        (channels, height, width), with pixel values scaled to [0, 1].

    Notes:
        Model-specific mean/std normalization is intentionally omitted.
        Configure it later to match the selected trained model exactly.
    """
    path = Path(image_path)

    if not path.exists() or not path.is_file():
        raise XRayPreprocessingError("The specified image does not exist.")

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise XRayPreprocessingError(
            f"Unsupported image format: {path.suffix or 'no extension'}"
        )

    if path.stat().st_size == 0:
        raise XRayPreprocessingError("The image file is empty.")

    if path.stat().st_size > MAX_FILE_SIZE_BYTES:
        raise XRayPreprocessingError("The image file exceeds 20 MB.")

    if (
        not isinstance(image_size, tuple)
        or len(image_size) != 2
        or any(
            not isinstance(dimension, int)
            or isinstance(dimension, bool)
            or dimension <= 0
            for dimension in image_size
        )
    ):
        raise XRayPreprocessingError(
            "image_size must be a tuple of two positive integers."
        )

    if channels not in (1, 3):
        raise XRayPreprocessingError("channels must be 1 or 3.")

    try:
        with Image.open(path) as source:
            if source.width * source.height > MAX_IMAGE_PIXELS:
                raise XRayPreprocessingError(
                    "The image dimensions exceed the allowed pixel limit."
                )

            source.verify()

        with Image.open(path) as source:
            image = ImageOps.exif_transpose(source)

            if image.width * image.height > MAX_IMAGE_PIXELS:
                raise XRayPreprocessingError(
                    "The image dimensions exceed the allowed pixel limit."
                )

            image = image.convert("L" if channels == 1 else "RGB")

            height, width = image_size
            image = image.resize(
                (width, height),
                Image.Resampling.BILINEAR,
            )

            array = np.asarray(image, dtype=np.float32) / 255.0

    except XRayPreprocessingError:
        raise
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise XRayPreprocessingError(
            f"Could not read image: {path.name}"
        ) from exc

    if channels == 1:
        array = array[np.newaxis, :, :]
    else:
        array = np.transpose(array, (2, 0, 1))

    return np.ascontiguousarray(array, dtype=np.float32)
