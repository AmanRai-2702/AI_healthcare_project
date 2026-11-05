
"""API endpoint for chest X-ray image preprocessing."""

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.xray_analysis.preprocessing import preprocess_xray

router = APIRouter(prefix="/images", tags=["X-ray Images"])

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}
MAX_FILE_SIZE = 20 * 1024 * 1024


@router.post("/preprocess")
async def preprocess_image(file: UploadFile = File(...)):
    """Validate and preprocess an uploaded chest X-ray image."""

    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    filename = Path(file.filename).name
    suffix = Path(filename).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported X-ray image format.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image exceeds the 20 MB size limit.",
        )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False,
        ) as temp_file:
            temp_file.write(content)
            temp_path = Path(temp_file.name)

        image_array = preprocess_xray(
            temp_path,
            image_size=(224, 224),
            channels=3,
        )

        return {
            "status": "success",
            "filename": filename,
            "message": "X-ray image validated and preprocessed.",
            "image_shape": list(image_array.shape),
            "data_type": str(image_array.dtype),
            "min_pixel_value": float(image_array.min()),
            "max_pixel_value": float(image_array.max()),
            "diagnosis": None,
            "note": "This endpoint does not detect diseases or provide a diagnosis.",
        }

    except (ValueError, OSError) as exc:
        raise HTTPException(
            status_code=422,
            detail=f"X-ray preprocessing failed: {exc}",
        ) from exc

    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()
