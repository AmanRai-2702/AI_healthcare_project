
"""Safe loading and basic validation for medical documents."""

from pathlib import Path

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".tif",
    ".tiff",
    ".webp",
}

FILE_SIGNATURES = {
    ".pdf": (b"%PDF-",),
    ".png": (b"\x89PNG\r\n\x1a\n",),
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
    ".tif": (b"II*\x00", b"MM\x00*"),
    ".tiff": (b"II*\x00", b"MM\x00*"),
    ".webp": (b"RIFF",),
}


class DocumentLoadError(ValueError):
    """Raised when a document cannot be safely loaded."""


def load_document(file_path: str | Path) -> dict:
    """Validate a document and return its bytes and basic metadata."""
    path = Path(file_path)

    if not path.exists():
        raise DocumentLoadError("The specified file does not exist.")

    if not path.is_file():
        raise DocumentLoadError("The specified path is not a file.")

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise DocumentLoadError(
            f"Unsupported file type: {extension or 'no extension'}"
        )

    size = path.stat().st_size

    if size == 0:
        raise DocumentLoadError("The file is empty.")

    if size > MAX_FILE_SIZE:
        raise DocumentLoadError("The file exceeds the 20 MB limit.")

    with path.open("rb") as file:
        content = file.read(MAX_FILE_SIZE + 1)

    if len(content) > MAX_FILE_SIZE:
        raise DocumentLoadError("The file exceeds the 20 MB limit.")

    signatures = FILE_SIGNATURES[extension]

    if not any(content.startswith(sig) for sig in signatures):
        raise DocumentLoadError(
            "The file content does not match its extension."
        )

    # WebP files use RIFF as their container signature and WEBP at byte 8.
    if extension == ".webp" and content[8:12] != b"WEBP":
        raise DocumentLoadError("Invalid WebP file signature.")

    return {
        "filename": path.name,
        "extension": extension,
        "size_bytes": len(content),
        "content": content,
    }
