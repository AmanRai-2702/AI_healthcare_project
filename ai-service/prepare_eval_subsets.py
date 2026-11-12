
from pathlib import Path
from huggingface_hub import hf_hub_download
import pyarrow.parquet as pq
from PIL import Image
import io

DATASET = "mmenendezg/pneumonia_x_ray"
SAMPLES_PER_CLASS = 50

def extract_split(split_name):
    filename = f"data/{split_name}-00000-of-00001.parquet"

    print(f"\nPreparing {split_name} split...")

    path = hf_hub_download(
        repo_id=DATASET,
        repo_type="dataset",
        filename=filename,
    )

    parquet = pq.ParquetFile(path)
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
            len(selected[label]) >= SAMPLES_PER_CLASS
            for label in selected
        ):
            break

    for label, images in selected.items():
        class_name = "normal" if label == 0 else "pneumonia"
        folder = Path("data/xray_splits") / split_name / class_name
        folder.mkdir(parents=True, exist_ok=True)

        for index, image_bytes in enumerate(images):
            with Image.open(io.BytesIO(image_bytes)) as image:
                image.convert("RGB").save(
                    folder / f"{class_name}_{index:03d}.jpg",
                    quality=95,
                )

    print("Normal:", len(selected[0]))
    print("Pneumonia:", len(selected[1]))

    if any(len(selected[label]) < SAMPLES_PER_CLASS for label in (0, 1)):
        raise RuntimeError(
            f"Not enough images in {split_name} for both classes."
        )

extract_split("validation")
extract_split("test")

print("\nValidation and test extraction complete!")
