
"""Model creation and checkpoint loading for chest X-ray analysis."""

from pathlib import Path
from typing import Any

import torch
from torch import nn
from torchvision import models


class ModelLoadError(RuntimeError):
    """Raised when a model checkpoint cannot be loaded safely."""


IMAGE_MEAN = [0.485, 0.456, 0.406]
IMAGE_STD = [0.229, 0.224, 0.225]


def build_model(num_classes: int = 2) -> nn.Module:
    if not isinstance(num_classes, int) or isinstance(num_classes, bool):
        raise ValueError("num_classes must be an integer.")
    if num_classes < 2:
        raise ValueError("num_classes must be at least 2.")

    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


def load_model(
    checkpoint_path: str | Path,
    num_classes: int = 2,
    device: str | torch.device | None = None,
) -> nn.Module:
    """Load trained ResNet-18 checkpoint."""
    path = Path(checkpoint_path).expanduser()

    if not path.is_file():
        raise FileNotFoundError(f"Model checkpoint not found: {path}")

    target_device = torch.device(
        device if device is not None
        else ("cuda" if torch.cuda.is_available() else "cpu")
    )

    if target_device.type == "cuda" and not torch.cuda.is_available():
        raise ModelLoadError("CUDA is unavailable.")

    try:
        checkpoint: Any = torch.load(
            path,
            map_location=target_device,
            weights_only=True,
        )
    except Exception as exc:
        raise ModelLoadError(f"Could not read checkpoint: {exc}") from exc

    if not isinstance(checkpoint, dict):
        raise ModelLoadError("Invalid checkpoint format.")

    state_dict = checkpoint.get("model_state_dict", checkpoint.get("state_dict"))

    if not isinstance(state_dict, dict) or not state_dict:
        raise ModelLoadError("Checkpoint has no valid model_state_dict.")

    classes = checkpoint.get("classes", {
        "normal": 0,
        "pneumonia": 1,
    })

    expected_classes = {
        "normal": 0,
        "pneumonia": 1,
    }

    if classes != expected_classes:
        raise ModelLoadError(
            f"Unexpected class mapping in checkpoint: {classes}"
        )

    state_dict = {
        key.removeprefix("module."): value
        for key, value in state_dict.items()
    }

    model = build_model(num_classes=num_classes)

    try:
        model.load_state_dict(state_dict, strict=True)
    except (RuntimeError, TypeError) as exc:
        raise ModelLoadError(
            f"Checkpoint architecture mismatch: {exc}"
        ) from exc

    model.to(target_device)
    model.eval()

    # Keep preprocessing metadata alongside the model.
    model.xray_mean = checkpoint.get("mean", IMAGE_MEAN)
    model.xray_std = checkpoint.get("std", IMAGE_STD)
    model.xray_class_names = ["normal", "pneumonia"]

    return model
