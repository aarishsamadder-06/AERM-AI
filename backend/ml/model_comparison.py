"""Compare offline SCIN image-gradability models without touching AERM inference."""

from __future__ import annotations

import argparse
import json
import pickle
import time
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression

from .quality_baseline import (
    _image_path,
    extract_quality_features,
    build_arrays,
    load_split_rows,
)

SEED = 20261030
CLASS_NAMES = ("insufficient", "quality_sufficient")


def _report(y_true: np.ndarray, predictions: np.ndarray) -> dict:
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, predictions, labels=[0, 1], zero_division=0
    )
    return {
        "n": int(len(y_true)),
        "accuracy": float(accuracy_score(y_true, predictions)),
        "precision_macro": float(precision.mean()),
        "recall_macro": float(recall.mean()),
        "f1_macro": float(f1.mean()),
        "precision_by_class": dict(zip(CLASS_NAMES, precision.tolist())),
        "recall_by_class": dict(zip(CLASS_NAMES, recall.tolist())),
        "f1_by_class": dict(zip(CLASS_NAMES, f1.tolist())),
        "confusion_matrix": confusion_matrix(y_true, predictions, labels=[0, 1]).tolist(),
    }


def _majority_report(y_true: np.ndarray) -> dict:
    majority = int(np.bincount(y_true).argmax())
    return {
        **_report(y_true, np.full(len(y_true), majority)),
        "majority_class": CLASS_NAMES[majority],
    }


def _models() -> dict[str, object]:
    return {
        "logistic_regression": Pipeline(
            [
                ("scale", StandardScaler()),
                (
                    "classifier",
                    LogisticRegression(
                        class_weight="balanced", max_iter=2000, random_state=SEED
                    ),
                ),
            ]
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced",
            random_state=SEED,
            n_jobs=-1,
        ),
        "svm_rbf": Pipeline(
            [
                ("scale", StandardScaler()),
                (
                    "classifier",
                    SVC(
                        class_weight="balanced",
                        kernel="rbf",
                        C=1.0,
                        gamma="scale",
                    ),
                ),
            ]
        ),
    }


def _build_quality_arrays(root: Path, rows: list[dict[str, str]]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    features = []
    labels = []
    splits = []
    for row in rows:
        features.append(extract_quality_features(_image_path(root, row["image_path"])))
        labels.append(1 if row["label"] == "quality_sufficient" else 0)
        splits.append(row["split"])
    return np.vstack(features), np.asarray(labels), np.asarray(splits)


def compare_models(root: Path, split_path: Path, output_dir: Path) -> dict:
    rows = load_split_rows(split_path)
    features, labels, splits = build_arrays(root, rows)
    train_mask = splits == "train"
    validation_mask = splits == "validation"
    test_mask = splits == "test"

    candidates: dict[str, dict] = {}
    for name, model in _models().items():
        started = time.perf_counter()
        model.fit(features[train_mask], labels[train_mask])
        fit_seconds = time.perf_counter() - started
        candidates[name] = {
            "model": model,
            "features": features,
            "labels": labels,
            "fit_seconds": fit_seconds,
            "validation": _report(
                labels[validation_mask], model.predict(features[validation_mask])
            ),
        }

    quality_features, quality_labels, quality_splits = _build_quality_arrays(root, rows)
    quality_model = Pipeline(
        [
            ("scale", StandardScaler()),
            (
                "classifier",
                LogisticRegression(
                    class_weight="balanced", max_iter=2000, random_state=SEED
                ),
            ),
        ]
    )
    started = time.perf_counter()
    quality_model.fit(quality_features[train_mask], quality_labels[train_mask])
    quality_fit_seconds = time.perf_counter() - started
    candidates["logistic_regression_quality_features"] = {
        "model": quality_model,
        "features": quality_features,
        "labels": quality_labels,
        "fit_seconds": quality_fit_seconds,
        "validation": _report(
            quality_labels[validation_mask],
            quality_model.predict(quality_features[validation_mask]),
        ),
    }

    selected_name = max(
        candidates,
        key=lambda name: (
            candidates[name]["validation"]["f1_macro"],
            candidates[name]["validation"]["accuracy"],
            -candidates[name]["fit_seconds"],
        ),
    )
    selected = candidates[selected_name]["model"]
    results = {
        "seed": SEED,
        "split_file": str(split_path),
        "feature_count": int(features.shape[1]),
        "feature_sets": {
            "base": "Existing 21 deterministic image features",
            "quality": "Base features plus aspect ratio, normalized dimensions, contrast, under/overexposure proportions, and Laplacian sharpness",
        },
        "selection_metric": "validation macro F1; validation accuracy and fit time break ties",
        "selection_test_policy": "Test metrics are computed once for the selected model after validation selection",
        "class_counts": {
            split: {
                "quality_sufficient": int(np.sum(labels[splits == split] == 1)),
                "insufficient": int(np.sum(labels[splits == split] == 0)),
            }
            for split in ("train", "validation", "test")
        },
        "majority_baseline": {
            split: _majority_report(labels[splits == split])
            for split in ("train", "validation", "test")
        },
        "candidates": {
            name: {
                "fit_seconds": values["fit_seconds"],
                "validation": values["validation"],
            }
            for name, values in candidates.items()
        },
        "selected_model": selected_name,
        "selected_feature_count": int(candidates[selected_name]["features"].shape[1]),
        "selected_test": _report(
            candidates[selected_name]["labels"][test_mask],
            selected.predict(candidates[selected_name]["features"][test_mask]),
        ),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "selected_quality_model.pkl").open("wb") as handle:
        pickle.dump(selected, handle)
    (output_dir / "model_comparison_metrics.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--split-file", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(compare_models(args.dataset_root, args.split_file, args.output_dir), indent=2))


if __name__ == "__main__":
    main()
