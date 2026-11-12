
from pathlib import Path
from PIL import Image

base = Path("data/xray_subset")

for class_name in ["normal", "pneumonia"]:
    folder = base / class_name
    images = list(folder.glob("*.jpg"))

    print(f"\n{class_name.upper()}: {len(images)} images")

    if not images:
        raise RuntimeError(f"No images found in {folder}")

    # Check that images can actually be opened.
    for path in images[:5]:
        with Image.open(path) as img:
            img.verify()

    print("First 5 images verified successfully.")

print("\nSubset verification complete!")
