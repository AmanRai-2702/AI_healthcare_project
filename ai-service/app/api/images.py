
"""API endpoints for chest X-ray preprocessing and experimental analysis."""

import tempfile
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.xray_analysis.preprocessing import preprocess_xray
from app.xray_analysis.model_loader import load_model, ModelLoadError
from app.xray_analysis.inference import predict_xray

router = APIRouter(prefix="/images", tags=["X-ray Images"])

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}
MAX_FILE_SIZE = 20 * 1024 * 1024

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHECKPOINT_PATH = PROJECT_ROOT / "models" / "pneumonia_resnet18.pth"


@lru_cache(maxsize=1)
def get_xray_model():
    """Load the trained model once and reuse it across requests."""
    return load_model(
        CHECKPOINT_PATH,
        num_classes=2,
        device="cpu",
    )


async def save_uploaded_image(file: UploadFile):
    """Validate an uploaded image and save it temporarily."""

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    filename = Path(file.filename).name
    suffix = Path(filename).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported X-ray image format.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image exceeds the 20 MB size limit.",
        )

    temp_file = tempfile.NamedTemporaryFile(
        suffix=suffix,
        delete=False,
    )

    temp_path = Path(temp_file.name)

    try:
        with temp_file:
            temp_file.write(content)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise

    return filename, temp_path


@router.post("/preprocess")
async def preprocess_image(file: UploadFile = File(...)):
    """Validate and preprocess an uploaded chest X-ray image."""

    filename, temp_path = await save_uploaded_image(file)

    try:
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
        temp_path.unlink(missing_ok=True)


@router.post("/analyze")
async def analyze_xray(file: UploadFile = File(...)):
    """Run experimental Normal/Pneumonia classification."""

    filename, temp_path = await save_uploaded_image(file)

    try:
        model = get_xray_model()

        result = predict_xray(
            model,
            temp_path,
            class_names=["normal", "pneumonia"],
            image_size=(224, 224),
        )

        return {
            "status": "success",
            "filename": filename,
            "analysis": result,
            "note": (
                "Experimental AI output only. This is not a medical diagnosis "
                "and must not guide treatment decisions."
            ),
        }

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Trained X-ray model is unavailable: {exc}",
        ) from exc

    except ModelLoadError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Could not load trained X-ray model: {exc}",
        ) from exc

    except (ValueError, OSError) as exc:
        raise HTTPException(
            status_code=422,
            detail=f"X-ray analysis failed: {exc}",
        ) from exc

    finally:
        temp_path.unlink(missing_ok=True)
