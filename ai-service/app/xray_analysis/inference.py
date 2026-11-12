
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
    """Run experimental chest X-ray classification."""

    if not isinstance(model, nn.Module):
        raise TypeError("model must be a PyTorch nn.Module.")

    if not isinstance(image_path, (str, Path)):
        raise TypeError("image_path must be a string or Path.")

    try:
        device = next(model.parameters()).device
    except StopIteration as exc:
        raise ValueError("Model has no parameters.") from exc

    image_array = preprocess_xray(
        image_path,
        image_size=image_size,
        channels=3,
    )

    if not isinstance(image_array, np.ndarray):
        raise TypeError("Preprocessing must return a NumPy array.")

    if image_array.ndim != 3 or image_array.shape[0] != 3:
        raise ValueError("Expected image shape (3, H, W).")

    mean = np.asarray(
        getattr(model, "xray_mean", [0.485, 0.456, 0.406]),
        dtype=np.float32,
    ).reshape(3, 1, 1)

    std = np.asarray(
        getattr(model, "xray_std", [0.229, 0.224, 0.225]),
        dtype=np.float32,
    ).reshape(3, 1, 1)

    if np.any(std <= 0):
        raise ValueError("Normalization standard deviations must be positive.")

    # Match the normalization used during training.
    image_array = (image_array - mean) / std

    image_tensor = torch.from_numpy(
        np.ascontiguousarray(image_array)
    ).float().unsqueeze(0).to(device)

    if class_names is None:
        class_names = getattr(
            model,
            "xray_class_names",
            ["normal", "pneumonia"],
        )

    model.eval()

    with torch.inference_mode():
        logits = model(image_tensor)

        if not isinstance(logits, torch.Tensor):
            raise TypeError("Model must return a tensor.")

        if logits.ndim != 2 or logits.shape[0] != 1:
            raise ValueError("Invalid model output shape.")

        if not torch.isfinite(logits).all():
            raise ValueError("Model returned non-finite values.")

        probabilities = torch.softmax(logits, dim=1)[0]

    scores = probabilities.cpu().tolist()
    predicted_index = int(torch.argmax(probabilities).item())

    if len(class_names) != len(scores):
        raise ValueError("Class names do not match model outputs.")

    return {
        "predicted_class": class_names[predicted_index],
        "confidence": scores[predicted_index],
        "probabilities": {
            name: score
            for name, score in zip(class_names, scores)
        },
        "note": (
            "Experimental model output, not a medical diagnosis. "
            "Clinical validation is required."
        ),
    }
