# Offline SCIN quality baseline

This module is an offline research experiment for SCIN's image-quality/gradability
labels. It is not the AERM production predictor, a cosmetic skin classifier, or a
medical diagnosis model. It does not change FastAPI routes or application inference.

The dataset must be acquired outside Git through the official SCIN route. The
expected external directory contains:

```text
scin-1.0.0/
  images/
  metadata/
  day5_case_split.csv
```

Run from the repository root:

```powershell
python -m backend.ml.quality_baseline `
  --dataset-root C:\Users\Aarish\AppData\Local\AERM-AI-data\scin-1.0.0 `
  --split-file C:\Users\Aarish\AppData\Local\AERM-AI-data\scin-1.0.0\metadata\day5_case_split.csv `
  --output-dir C:\Users\Aarish\AppData\Local\AERM-AI-data\scin-1.0.0\metadata\day5-baseline
```

The baseline converts each image to RGB, resizes to 128×128, and extracts simple
brightness, color, saturation, and finite-difference edge features. It trains a
class-weighted logistic regression after standardization. The case-aware split
manifest is never reshuffled, and the test set is not used for model selection.

The Day 6 comparison command writes `selected_quality_model.pkl` and
`model_comparison_metrics.json` beside the external dataset. The selected SVM
checkpoint exposes a decision score rather than a probability. Do not copy
dataset files, checkpoints, or credentials into Git. Scores are not calibrated
probabilities and must not be shown as AERM skin-analysis confidence.
The checkpoint was verified with `scikit-learn==1.8.0`; keep that version when
loading the pickle to avoid serialization or estimator compatibility drift.
Pickle is executable serialization: load checkpoints only from a trusted,
read-only external location. Production FastAPI startup/inference requires
`AERM_QUALITY_MODEL_SHA256` to match the checkpoint's SHA-256 digest. Never place
the dataset or checkpoint in Git.

## Comprehensive benchmark boundary

The available reproducible benchmark covers the four traditional candidates
listed in `model_comparison.py`. A deep-learning comparison was not run because
the current environment has no PyTorch, torchvision, or Transformers
installation, and no verified local candidate checkpoints were available.
Therefore the existing RBF SVM was retained rather than replaced on architecture
claims alone. No benchmark artifact, dataset, or checkpoint is required in Git;
the external Day 6 metrics remain the source of truth for the production gate.

Run standalone inference without retraining:

```powershell
python -m backend.ml.predict_quality `
  --checkpoint C:\Users\Aarish\AppData\Local\AERM-AI-data\scin-1.0.0\metadata\day6-model-comparison\selected_quality_model.pkl `
  --image C:\path\to\your\image.png
```

The command loads the external checkpoint, extracts the same 21 base features
used by the selected SVM, and prints `quality_sufficient` or `insufficient`.
The decision score is only a raw SVM score and is not a calibrated probability,
skin-analysis confidence, diagnosis, or cosmetic skin prediction.

## Optional FastAPI image-quality gate

The verified checkpoint can be exposed as a separate per-view quality signal
without changing the existing cosmetic analysis fields:

```powershell
$env:AERM_QUALITY_MODEL_PATH = "C:\Users\Aarish\AppData\Local\AERM-AI-data\scin-1.0.0\metadata\day6-model-comparison\selected_quality_model.pkl"
$env:AERM_QUALITY_MODEL_SHA256 = "<sha256 of the trusted checkpoint>"
cd backend
uvicorn app.main:app --reload --port 8000
```

With the variable set, `POST /api/analyze` adds `image_quality.views`, containing
one `quality_sufficient` or `insufficient` result for each submitted view and a
raw SVM decision score. Without the variable, `image_quality` is `null`, so
existing clients continue to receive the original response fields. A missing or
unreadable configured checkpoint returns HTTP 503 rather than silently falling
back.

Run the Day 6 comparison from the repository root with:

```powershell
python -m backend.ml.model_comparison `
  --dataset-root C:\Users\Aarish\AppData\Local\AERM-AI-data\scin-1.0.0 `
  --split-file C:\Users\Aarish\AppData\Local\AERM-AI-data\scin-1.0.0\metadata\day5_case_split.csv `
  --output-dir C:\Users\Aarish\AppData\Local\AERM-AI-data\scin-1.0.0\metadata\day6-model-comparison
```
