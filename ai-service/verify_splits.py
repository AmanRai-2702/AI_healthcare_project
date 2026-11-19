
from pathlib import Path

base = Path("data/xray_splits")

for split in ["validation", "test"]:
    print(f"\n{split.upper()}")

    for class_name in ["normal", "pneumonia"]:
        folder = base / split / class_name
        count = len(list(folder.glob("*.jpg")))
        print(f"{class_name}: {count}")

        if count != 50:
            raise RuntimeError(
                f"Expected 50 {class_name} images in {split}, got {count}"
            )

print("\nAll evaluation subsets verified!")
