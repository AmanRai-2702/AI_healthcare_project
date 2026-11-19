
"""OCR utilities for medical documents and scanned PDFs."""

import os
from io import BytesIO
from pathlib import Path

import pymupdf
import pytesseract
from PIL import Image, ImageOps, UnidentifiedImageError


SUPPORTED_IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".tif",
    ".tiff",
    ".webp",
}

SUPPORTED_EXTENSIONS = SUPPORTED_IMAGE_EXTENSIONS | {".pdf"}

DEFAULT_TESSERACT_PATH = Path(
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


class OCRProcessingError(ValueError):
    """Raised when a document cannot be processed by OCR."""


def _configure_tesseract() -> None:
    """Configure Tesseract using an environment variable or Windows default."""
    configured_path = os.getenv("TESSERACT_CMD")

    if configured_path:
        pytesseract.pytesseract.tesseract_cmd = configured_path
    elif DEFAULT_TESSERACT_PATH.is_file():
        pytesseract.pytesseract.tesseract_cmd = str(
            DEFAULT_TESSERACT_PATH
        )


def _prepare_image(image: Image.Image) -> Image.Image:
    """Prepare an image for OCR without changing its dimensions."""
    image = ImageOps.exif_transpose(image)
    image = ImageOps.grayscale(image)
    return ImageOps.autocontrast(image)


def _ocr_image(image: Image.Image, language: str) -> str:
    """Extract text from an already opened image."""
    _configure_tesseract()
    prepared = _prepare_image(image)
    return pytesseract.image_to_string(
        prepared,
        lang=language,
        config="--psm 3",
    ).strip()


def extract_text(
    file_path: str | Path,
    language: str = "eng",
    pdf_dpi: int = 200,
) -> str:
    """
    Extract text from a PDF or supported image.

    Text-based PDF pages use direct text extraction. Pages without enough
    embedded text are rendered and processed using Tesseract OCR.

    Args:
        file_path: Path to a PDF or supported image.
        language: Installed Tesseract language code, such as "eng".
        pdf_dpi: Rendering resolution used for scanned PDF pages.

    Returns:
        Extracted text. For PDFs, page contents are separated by newlines.

    Raises:
        OCRProcessingError: If the file is invalid or cannot be processed.
        pytesseract.TesseractNotFoundError: If Tesseract is unavailable.
    """
    path = Path(file_path)

    if not path.exists() or not path.is_file():
        raise OCRProcessingError("The specified file does not exist.")

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise OCRProcessingError(
            f"Unsupported file type: {extension or 'no extension'}"
        )

    if path.stat().st_size == 0:
        raise OCRProcessingError("The file is empty.")

    if pdf_dpi < 72 or pdf_dpi > 600:
        raise OCRProcessingError("pdf_dpi must be between 72 and 600.")

    _configure_tesseract()

    try:
        if extension == ".pdf":
            return _extract_pdf_text(path, language, pdf_dpi)

        with Image.open(path) as image:
            # Handle multi-frame TIFF files as well as ordinary images.
            extracted_pages = []

            for frame_number in range(getattr(image, "n_frames", 1)):
                image.seek(frame_number)
                frame = image.copy()
                text = _ocr_image(frame, language)

                if text:
                    extracted_pages.append(text)

            return "\n\n".join(extracted_pages).strip()

    except pytesseract.TesseractNotFoundError:
        raise
    except (pymupdf.FileDataError, UnidentifiedImageError, OSError) as exc:
        raise OCRProcessingError(
            f"Could not read or process the document: {path.name}"
        ) from exc


def _extract_pdf_text(
    path: Path,
    language: str,
    pdf_dpi: int,
) -> str:
    """Extract embedded PDF text, using OCR for scanned pages."""
    page_texts = []

    with pymupdf.open(path) as document:
        if document.is_encrypted:
            raise OCRProcessingError(
                "Password-protected PDFs are not supported yet."
            )

        for page in document:
            text = page.get_text("text").strip()

            # Scanned pages usually have no embedded text.
            if len(text) < 20:
                scale = pdf_dpi / 72
                pixmap = page.get_pixmap(
                    matrix=pymupdf.Matrix(scale, scale),
                    alpha=False,
                )
                image_bytes = pixmap.tobytes("png")

                with Image.open(BytesIO(image_bytes)) as image:
                    text = _ocr_image(image, language)

            page_texts.append(text)

    return "\n\n".join(
        text for text in page_texts if text
    ).strip()
