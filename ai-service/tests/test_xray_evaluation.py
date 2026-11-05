
import pytest

from app.xray_analysis.evaluation import evaluate_predictions


def test_evaluation_metrics():
    result = evaluate_predictions(
        [0, 0, 1, 1],
        [0, 0, 1, 1],
    )

    assert result["accuracy"] == 1.0
    assert result["precision"] == 1.0
    assert result["recall_sensitivity"] == 1.0
    assert result["specificity"] == 1.0
    assert result["f1_score"] == 1.0
    assert result["sample_count"] == 4


def test_incorrect_predictions():
    result = evaluate_predictions(
        [0, 0, 1, 1],
        [0, 1, 0, 1],
    )

    assert result["accuracy"] == 0.5
    assert result["confusion_matrix"]["false_positive"] == 1
    assert result["confusion_matrix"]["false_negative"] == 1


def test_empty_data_rejected():
    with pytest.raises(ValueError):
        evaluate_predictions([], [])


def test_mismatched_lengths_rejected():
    with pytest.raises(ValueError):
        evaluate_predictions([0, 1], [0])


def test_invalid_labels_rejected():
    with pytest.raises(ValueError):
        evaluate_predictions([0, 2], [0, 1])
