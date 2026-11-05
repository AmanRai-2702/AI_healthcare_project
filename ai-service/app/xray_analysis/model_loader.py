
"""Model creation and checkpoint loading for chest X-ray analysis."""

from pathlib import Path
from typing import Any

import torch
from torch import nn
from torchvision import models


class ModelLoadError(RuntimeError):
    """Raised when a model checkpoint cannot be loaded safely."""


def build_model(num_classes: int = 2) -> nn.Module:
    """Create a ResNet-18 architecture without downloading pretrained weights."""
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
    """Load trained weights and return the model in evaluation mode.

    The checkpoint must contain a compatible state_dict. Randomly
    initialized weights are never returned as a loaded model.
    """
    path = Path(checkpoint_path).expanduser()

    if not path.is_file():
        raise FileNotFoundError(
            f"Model checkpoint not found: {path}. "
            "Provide a trained, compatible checkpoint."
        )

    target_device = torch.device(
        device if device is not None
        else ("cuda" if torch.cuda.is_available() else "cpu")
    )

    if target_device.type == "cuda" and not torch.cuda.is_available():
        raise ModelLoadError("CUDA was requested but is not available.")

    try:
        # weights_only=True avoids unpickling arbitrary Python objects.
        checkpoint: Any = torch.load(
            path,
            map_location=target_device,
            weights_only=True,
        )
    except Exception as exc:
        raise ModelLoadError(
            f"Could not read checkpoint '{path}': {exc}"
        ) from exc

    if isinstance(checkpoint, dict):
        state_dict = checkpoint.get(
            "state_dict",
            checkpoint.get("model_state_dict", checkpoint),
        )
    else:
        raise ModelLoadError(
            "Checkpoint must be a state_dict or contain "
            "'state_dict' / 'model_state_dict'."
        )

    if not isinstance(state_dict, dict) or not state_dict:
        raise ModelLoadError("Checkpoint does not contain a valid state_dict.")

    # Support checkpoints saved from DataParallel models.
    if all(isinstance(key, str) for key in state_dict):
        state_dict = {
            key.removeprefix("module."): value
            for key, value in state_dict.items()
        }

    model = build_model(num_classes=num_classes)

    try:
        model.load_state_dict(state_dict, strict=True)
    except (RuntimeError, TypeError) as exc:
        raise ModelLoadError(
            "Checkpoint weights do not match the ResNet-18 architecture "
            f"with {num_classes} output classes: {exc}"
        ) from exc

    model.to(target_device)
    model.eval()
    return model
