
from pathlib import Path
import json
import random

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from torchvision.models import ResNet18_Weights


# ==================================================
# CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

SEED = 42
IMAGE_SIZE = 224
BATCH_SIZE = 4
EPOCHS = 2
LEARNING_RATE = 0.0001

TRAIN_DIR = BASE_DIR / "data" / "xray_subset"
VAL_DIR = BASE_DIR / "data" / "xray_splits" / "validation"

OUTPUT_DIR = BASE_DIR / "models"
CHECKPOINT_PATH = OUTPUT_DIR / "pneumonia_resnet18.pth"
HISTORY_PATH = OUTPUT_DIR / "training_history.json"

DEVICE = torch.device("cpu")

# Define these BEFORE using them in transforms.
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]

EXPECTED_CLASSES = {
    "normal": 0,
    "pneumonia": 1,
}


# ==================================================
# REPRODUCIBILITY
# ==================================================

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)


# ==================================================
# CHECK DATASET DIRECTORIES
# ==================================================

if not TRAIN_DIR.exists():
    raise FileNotFoundError(f"Training folder not found: {TRAIN_DIR}")

if not VAL_DIR.exists():
    raise FileNotFoundError(f"Validation folder not found: {VAL_DIR}")


# ==================================================
# DATA TRANSFORMS
# ==================================================

train_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.RandomRotation(5),
    transforms.ToTensor(),
    transforms.Normalize(mean=MEAN, std=STD),
])

val_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=MEAN, std=STD),
])


# ==================================================
# LOAD DATASETS
# ==================================================

train_dataset = datasets.ImageFolder(
    root=str(TRAIN_DIR),
    transform=train_transform,
)

val_dataset = datasets.ImageFolder(
    root=str(VAL_DIR),
    transform=val_transform,
)

print("Training classes:", train_dataset.class_to_idx)
print("Validation classes:", val_dataset.class_to_idx)
print("Training images:", len(train_dataset))
print("Validation images:", len(val_dataset))

if train_dataset.class_to_idx != EXPECTED_CLASSES:
    raise ValueError(
        f"Unexpected training class mapping: "
        f"{train_dataset.class_to_idx}"
    )

if val_dataset.class_to_idx != EXPECTED_CLASSES:
    raise ValueError(
        f"Unexpected validation class mapping: "
        f"{val_dataset.class_to_idx}"
    )

if len(train_dataset) == 0 or len(val_dataset) == 0:
    raise RuntimeError("Training or validation dataset is empty.")


# ==================================================
# DATA LOADERS
# ==================================================

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=0,
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0,
)


# ==================================================
# BUILD RESNET-18 MODEL
# ==================================================

print("\nLoading pretrained ResNet-18...")

model = models.resnet18(
    weights=ResNet18_Weights.DEFAULT
)

# Freeze all pretrained parameters.
for parameter in model.parameters():
    parameter.requires_grad = False

# Unfreeze layer4 for fine-tuning.
for parameter in model.layer4.parameters():
    parameter.requires_grad = True

# Replace final layer for binary classification.
model.fc = nn.Linear(
    model.fc.in_features,
    2,
)

model = model.to(DEVICE)

criterion = nn.CrossEntropyLoss()

optimizer = torch.optim.Adam(
    filter(
        lambda parameter: parameter.requires_grad,
        model.parameters(),
    ),
    lr=LEARNING_RATE,
)


# ==================================================
# TRAINING / VALIDATION FUNCTION
# ==================================================

def run_epoch(loader, training):
    if training:
        model.train()
    else:
        model.eval()

    total_loss = 0.0
    correct = 0
    total = 0

    for images, labels in loader:
        images = images.to(DEVICE)
        labels = labels.to(DEVICE)

        if training:
            optimizer.zero_grad()

        with torch.set_grad_enabled(training):
            outputs = model(images)
            loss = criterion(outputs, labels)

            if training:
                loss.backward()
                optimizer.step()

        total_loss += loss.item() * images.size(0)

        predictions = outputs.argmax(dim=1)

        correct += (predictions == labels).sum().item()
        total += labels.size(0)

    if total == 0:
        raise RuntimeError("DataLoader returned no images.")

    average_loss = total_loss / total
    accuracy = correct / total

    return average_loss, accuracy


# ==================================================
# TRAIN MODEL
# ==================================================

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

best_val_accuracy = -1.0
history = []

print("\nStarting training on:", DEVICE)

for epoch in range(EPOCHS):
    print(f"\nEpoch {epoch + 1}/{EPOCHS}")

    train_loss, train_accuracy = run_epoch(
        train_loader,
        training=True,
    )

    val_loss, val_accuracy = run_epoch(
        val_loader,
        training=False,
    )

    print(f"Train loss: {train_loss:.4f}")
    print(f"Train accuracy: {train_accuracy:.4f}")
    print(f"Validation loss: {val_loss:.4f}")
    print(f"Validation accuracy: {val_accuracy:.4f}")

    history.append({
        "epoch": epoch + 1,
        "train_loss": train_loss,
        "train_accuracy": train_accuracy,
        "val_loss": val_loss,
        "val_accuracy": val_accuracy,
    })

    # Save the best validation checkpoint.
    if val_accuracy > best_val_accuracy:
        best_val_accuracy = val_accuracy

        torch.save(
            {
                "model_state_dict": model.state_dict(),
                "classes": train_dataset.class_to_idx,
                "image_size": IMAGE_SIZE,
                "mean": MEAN,
                "std": STD,
                "best_val_accuracy": best_val_accuracy,
            },
            CHECKPOINT_PATH,
        )

        print("Best checkpoint saved:", CHECKPOINT_PATH)


# ==================================================
# SAVE TRAINING HISTORY
# ==================================================

with open(HISTORY_PATH, "w", encoding="utf-8") as file:
    json.dump(history, file, indent=4)

print("\nTraining complete!")
print("Best validation accuracy:", best_val_accuracy)
print("Checkpoint:", CHECKPOINT_PATH)
print("Training history:", HISTORY_PATH)
