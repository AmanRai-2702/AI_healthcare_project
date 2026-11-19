
"""Evaluation metrics for chest X-ray classification."""

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


def evaluate_predictions(
    y_true: list[int] | np.ndarray,
    y_pred: list[int] | np.ndarray,
) -> dict:
    """Calculate classification metrics for binary classification."""

    actual = np.asarray(y_true)
    predicted = np.asarray(y_pred)

    if actual.ndim != 1 or predicted.ndim != 1:
        raise ValueError("Inputs must be one-dimensional.")

    if len(actual) == 0:
        raise ValueError("Evaluation data cannot be empty.")

    if len(actual) != len(predicted):
        raise ValueError("Actual and predicted lengths must match.")

    if not np.isin(actual, [0, 1]).all():
        raise ValueError("Actual labels must contain only 0 and 1.")

    if not np.isin(predicted, [0, 1]).all():
        raise ValueError("Predicted labels must contain only 0 and 1.")

    actual = actual.astype(int)
    predicted = predicted.astype(int)

    tn, fp, fn, tp = confusion_matrix(
        actual,
        predicted,
        labels=[0, 1],
    ).ravel()

    specificity = (
        tn / (tn + fp) if (tn + fp) > 0 else 0.0
    )

    return {
        "accuracy": float(accuracy_score(actual, predicted)),
        "precision": float(
            precision_score(actual, predicted, zero_division=0)
        ),
        "recall_sensitivity": float(
            recall_score(actual, predicted, zero_division=0)
        ),
        "specificity": float(specificity),
        "f1_score": float(
            f1_score(actual, predicted, zero_division=0)
        ),
        "confusion_matrix": {
            "true_negative": int(tn),
            "false_positive": int(fp),
            "false_negative": int(fn),
            "true_positive": int(tp),
        },
        "sample_count": int(len(actual)),
    }
