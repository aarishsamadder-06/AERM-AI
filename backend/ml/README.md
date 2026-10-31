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
    day4_case_split.csv
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

Outputs are an external pickle checkpoint and JSON metrics report. Do not copy
dataset files, checkpoints, or credentials into Git. Raw scores are not calibrated
probabilities and must not be shown as AERM skin-analysis confidence.
