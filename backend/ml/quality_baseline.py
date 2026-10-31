"""Train an offline SCIN image-quality baseline.

This module intentionally does not import or modify the production predictor.
The dataset root must point to an externally acquired SCIN directory.
"""

from __future__ import annotations

import argparse
import csv
import json
import pickle
import random
from collections import Counter
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

QUALITY_LABELS = {
    "DEFAULT_YES_IMAGE_QUALITY_SUFFICIENT": "quality_sufficient",
    "YES_IMAGE_QUALITY_SUFFICIENT_NO_DISCERNIBLE_PATHOLOGY": "quality_sufficient",
    "NO_IMAGE_QUALITY_INSUFFICIENT": "insufficient",
}
FEATURE_DESCRIPTION = (
    "RGB means/stds, grayscale mean/std and percentiles, saturation statistics, "
    "and finite-difference edge energy after RGB resize to 128x128"
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _label_from_gradability(row: dict[str, str]) -> str:
    values = [
        row.get(f"dermatologist_gradable_for_skin_condition_{index}", "").strip()
        for index in range(1, 4)
    ]
    mapped = [QUALITY_LABELS[value] for value in values if value in QUALITY_LABELS]
    counts = Counter(mapped)
    if not counts:
        return "unknown"
    if len(counts) > 1:
        return "ambiguous"
    return next(iter(counts))


def _image_path(root: Path, manifest_path: str) -> Path:
    prefix = "dataset/images/"
    if not manifest_path.startswith(prefix):
        raise ValueError(f"Unexpected image path: {manifest_path}")
    return root / "images" / Path(*manifest_path[len(prefix) :].split("/"))


def extract_features(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        rgb = np.asarray(image.convert("RGB").resize((128, 128)), dtype=np.float32) / 255.0
    gray = rgb.mean(axis=2)
    horizontal = np.diff(gray, axis=1)
    vertical = np.diff(gray, axis=0)
    saturation = rgb.max(axis=2) - rgb.min(axis=2)
    return np.asarray(
        [
            *rgb.mean(axis=(0, 1)),
            *rgb.std(axis=(0, 1)),
            float(gray.mean()),
            float(gray.std()),
            *np.percentile(gray, [1, 5, 25, 50, 75, 95, 99]),
            float(saturation.mean()),
            float(saturation.std()),
            float((saturation > 0.25).mean()),
            float((horizontal * horizontal).mean()),
            float((vertical * vertical).mean()),
            float((np.abs(horizontal).mean() + np.abs(vertical).mean()) / 2),
        ],
        dtype=np.float32,
    )


def _metric_report(y_true: np.ndarray, predictions: np.ndarray) -> dict:
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, predictions, labels=[0, 1], zero_division=0
    )
    return {
        "n": int(len(y_true)),
        "accuracy": float(accuracy_score(y_true, predictions)),
        "precision_macro": float(precision.mean()),
        "recall_macro": float(recall.mean()),
        "f1_macro": float(f1.mean()),
        "precision_by_class": {
            "insufficient": float(precision[0]),
            "quality_sufficient": float(precision[1]),
        },
        "recall_by_class": {
            "insufficient": float(recall[0]),
            "quality_sufficient": float(recall[1]),
        },
        "f1_by_class": {
            "insufficient": float(f1[0]),
            "quality_sufficient": float(f1[1]),
        },
        "confusion_matrix_labels_insufficient_quality_sufficient": confusion_matrix(
            y_true, predictions, labels=[0, 1]
        ).tolist(),
    }


def _majority_report(y_true: np.ndarray) -> dict:
    majority = Counter(y_true.tolist()).most_common(1)[0][0]
    return {
        **_metric_report(y_true, np.full(len(y_true), majority)),
        "majority_class": "quality_sufficient" if majority else "insufficient",
    }


def load_split_rows(split_path: Path) -> list[dict[str, str]]:
    rows = _read_csv(split_path)
    if not rows:
        raise ValueError("The case split manifest is empty")
    return rows


def build_arrays(root: Path, rows: Iterable[dict[str, str]]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    features: list[np.ndarray] = []
    labels: list[int] = []
    splits: list[str] = []
    for row in rows:
        if row["label"] not in {"quality_sufficient", "insufficient"}:
            raise ValueError(f"Unexpected binary label: {row['label']}")
        path = _image_path(root, row["image_path"])
        if not path.is_file():
            raise FileNotFoundError(path)
        features.append(extract_features(path))
        labels.append(1 if row["label"] == "quality_sufficient" else 0)
        splits.append(row["split"])
    return np.vstack(features), np.asarray(labels), np.asarray(splits)


def train_and_evaluate(
    root: Path,
    output_dir: Path,
    seed: int = 20261030,
    split_path: Path | None = None,
) -> dict:
    random.seed(seed)
    np.random.seed(seed)
    rows = load_split_rows(split_path or root / "metadata" / "day4_case_split.csv")
    features, labels, splits = build_arrays(root, rows)
    model = Pipeline(
        [
            ("scale", StandardScaler()),
            (
                "classifier",
                LogisticRegression(
                    class_weight="balanced", max_iter=2000, random_state=seed
                ),
            ),
        ]
    )
    train_mask = splits == "train"
    model.fit(features[train_mask], labels[train_mask])
    metrics = {}
    majority = {}
    for split in ("train", "validation", "test"):
        mask = splits == split
        predictions = model.predict(features[mask])
        metrics[split] = _metric_report(labels[mask], predictions)
        majority[split] = _majority_report(labels[mask])

    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "quality_baseline.pkl").open("wb") as handle:
        pickle.dump(model, handle)
    report = {
        "dataset_root": str(root),
        "model": "StandardScaler + class-weighted LogisticRegression",
        "feature_count": int(features.shape[1]),
        "seed": seed,
        "preprocessing": FEATURE_DESCRIPTION,
        "class_counts": {
            split: dict(
                Counter(
                    "quality_sufficient" if label else "insufficient"
                    for label in labels[splits == split]
                )
            )
            for split in ("train", "validation", "test")
        },
        "metrics": metrics,
        "majority_baseline": majority,
    }
    (output_dir / "quality_baseline_metrics.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return report


def predict_image(model_path: Path, image_path: Path) -> dict[str, str | float]:
    with model_path.open("rb") as handle:
        model = pickle.load(handle)
    probability = float(model.predict_proba(extract_features(image_path)[None, :])[0, 1])
    label = "quality_sufficient" if probability >= 0.5 else "insufficient"
    return {"label": label, "score": probability}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--split-file",
        type=Path,
        help="Case-aware split CSV; defaults to metadata/day4_case_split.csv",
    )
    args = parser.parse_args()
    print(
        json.dumps(
            train_and_evaluate(args.dataset_root, args.output_dir, split_path=args.split_file),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
