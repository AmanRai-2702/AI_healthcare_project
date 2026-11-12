
from pathlib import Path
from huggingface_hub import hf_hub_download
import pyarrow.parquet as pq
from PIL import Image
import io

DATASET = "mmenendezg/pneumonia_x_ray"
SAMPLES_PER_CLASS = 200
OUTPUT_DIR = Path("data/xray_subset")

path = hf_hub_download(
    repo_id=DATASET,
    repo_type="dataset",
    filename="data/train-00000-of-00001.parquet",
)

parquet = pq.ParquetFile(path)

# Collect a balanced sample.
selected = {0: [], 1: []}

for group_index in range(parquet.metadata.num_row_groups):
    table = parquet.read_row_group(group_index)
    
    for row in table.to_pylist():
        label = int(row["label"])

        if label not in selected:
            continue

        if len(selected[label]) < SAMPLES_PER_CLASS:
            image_bytes = row["image"]["bytes"]

            if image_bytes:
                selected[label].append(image_bytes)

    if all(
        len(selected[label]) == SAMPLES_PER_CLASS
        for label in selected
    ):
        break

print("Selected samples:", {
    "normal": len(selected[0]),
    "pneumonia": len(selected[1]),
})

# Save images into class-specific folders.
for label, images in selected.items():
    class_name = "normal" if label == 0 else "pneumonia"
    output_folder = OUTPUT_DIR / class_name
    output_folder.mkdir(parents=True, exist_ok=True)

    for index, image_bytes in enumerate(images):
        with Image.open(io.BytesIO(image_bytes)) as image:
            image.convert("RGB").save(
                output_folder / f"{class_name}_{index:04d}.jpg",
                quality=95,
            )

print("\nExtraction complete!")

for class_name in ("normal", "pneumonia"):
    folder = OUTPUT_DIR / class_name
    print(f"{class_name}: {len(list(folder.glob('*.jpg')))} images")

print("Saved to:", OUTPUT_DIR.resolve())
