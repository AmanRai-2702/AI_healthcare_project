
from pathlib import Path

import torch
import torch.nn as nn
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

BASE_DIR = Path(__file__).resolve().parent

CHECKPOINT = BASE_DIR / "models" / "pneumonia_resnet18.pth"
TEST_DIR = BASE_DIR / "data" / "xray_splits" / "test"

DEVICE = torch.device("cpu")
BATCH_SIZE = 4

# Load checkpoint
checkpoint = torch.load(
    CHECKPOINT,
    map_location=DEVICE,
    weights_only=True,
)

# Match the training preprocessing exactly
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        checkpoint["mean"],
        checkpoint["std"],
    ),
])

test_dataset = datasets.ImageFolder(
    TEST_DIR,
    transform=transform,
)

print("Test classes:", test_dataset.class_to_idx)
print("Test images:", len(test_dataset))

assert test_dataset.class_to_idx == {
    "normal": 0,
    "pneumonia": 1,
}, "Unexpected class mapping"

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0,
)

# Rebuild the same ResNet-18 architecture
model = models.resnet18(weights=None)
model.fc = nn.Linear(model.fc.in_features, 2)

model.load_state_dict(checkpoint["model_state_dict"])
model.to(DEVICE)
model.eval()

actual = []
predicted = []

with torch.no_grad():
    for images, labels in test_loader:
        outputs = model(images.to(DEVICE))
        predictions = outputs.argmax(dim=1)

        actual.extend(labels.tolist())
        predicted.extend(predictions.cpu().tolist())

# Calculate metrics
print("\nTEST RESULTS")
print("Accuracy:", round(accuracy_score(actual, predicted), 4))
print(
    "Precision:",
    round(precision_score(actual, predicted, zero_division=0), 4),
)
print(
    "Recall:",
    round(recall_score(actual, predicted, zero_division=0), 4),
)
print(
    "F1-score:",
    round(f1_score(actual, predicted, zero_division=0), 4),
)

print("\nConfusion Matrix:")
print(confusion_matrix(actual, predicted))

print("\nClassification Report:")
print(
    classification_report(
        actual,
        predicted,
        target_names=["Normal", "Pneumonia"],
        zero_division=0,
    )
)
