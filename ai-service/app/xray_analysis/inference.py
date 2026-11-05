
"""Chest X-ray model inference."""

from pathlib import Path

import numpy as np
import torch
from torch import nn

from app.xray_analysis.preprocessing import preprocess_xray


def predict_xray(
    model: nn.Module,
    image_path: str | Path,
    class_names: list[str] | None = None,
    image_size: tuple[int, int] = (224, 224),
) -> dict:
    """Run model inference on a chest X-ray image.

    Returns predicted class and probabilities.
    These scores are not a medical diagnosis.
    """
    if not isinstance(model, nn.Module):
        raise TypeError("model must be a PyTorch nn.Module.")

    if not isinstance(image_path, (str, Path)):
        raise TypeError("image_path must be a string or Path.")

    try:
        device = next(model.parameters()).device
    except StopIteration as exc:
        raise ValueError("Model has no parameters.") from exc

    # ResNet-18 expects 3-channel input.
    image_array = preprocess_xray(
        image_path,
        image_size=image_size,
        channels=3,
    )

    if not isinstance(image_array, np.ndarray):
        raise TypeError("Preprocessing must return a NumPy array.")

    if image_array.ndim != 3 or image_array.shape[0] != 3:
        raise ValueError("Expected preprocessed image shape (3, H, W).")

    image_tensor = torch.from_numpy(
        np.ascontiguousarray(image_array)
    ).float().unsqueeze(0).to(device)

    model.eval()

    with torch.inference_mode():
        logits = model(image_tensor)

        if not isinstance(logits, torch.Tensor):
            raise TypeError("Model must return a PyTorch tensor.")

        if logits.ndim != 2 or logits.shape[0] != 1:
            raise ValueError("Model output must have shape (1, num_classes).")

        if not torch.isfinite(logits).all():
            raise ValueError("Model returned non-finite output values.")

        probabilities = torch.softmax(logits, dim=1)[0]

    scores = probabilities.cpu().tolist()
    predicted_index = int(torch.argmax(probabilities).item())

    if class_names is None:
        class_names = [
            f"class_{i}" for i in range(len(scores))
        ]

    if len(class_names) != len(scores):
        raise ValueError(
            "Number of class names must match model output classes."
        )

    return {
        "predicted_class": class_names[predicted_index],
        "confidence": scores[predicted_index],
        "probabilities": {
            name: score
            for name, score in zip(class_names, scores)
        },
        "note": (
            "Model scores are not a medical diagnosis. "
            "Clinical validation is required."
        ),
    }
