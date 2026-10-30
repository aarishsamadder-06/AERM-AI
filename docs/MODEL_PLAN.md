# Model plan

## Current implementation

The application still uses a deterministic simulator. It hashes the three uploaded
image names and bytes, selects a stable skin-signal scenario, and returns educational
observations. This keeps local demos and tests repeatable without pretending to
provide clinical or trained-model inference.

Images are validated by MIME type, size, file signatures, Pillow decoding, and
minimum dimensions. They are held in memory only for the request and are not written
to disk or sent to a third-party service.

## Phase 2 Day 1-3 audit outcome

No dataset or ML training module has been added. The verified SCIN dataset is a
medical dermatology-condition dataset with its own data-use license, not a validated
source for AERM's intended cosmetic facial labels. See
[`docs/DATASET_AUDIT.md`](DATASET_AUDIT.md) for the source, schema, license,
known issues, candidate comparison, recommendation, and the exact boundary.

The strongest available candidate is SCIN for an **offline binary gradability
classifier** based on dermatologist labels indicating whether the image evidence is
sufficient to determine a skin condition. This is a capture-suitability task only.
It must not be mapped to AERM's cosmetic concern literals, used as diagnosis, or
treated as calibrated confidence. SCIN access is public but still requires manual
data retrieval and compliance with its custom license.

The official notebook and bucket metadata were followed without downloading image
bytes. The two public CSV manifests contain 5,033 joined cases and expose the three
gradability fields. After grouping the two quality-sufficient values, majority
aggregation gives 3,065 quality-sufficient cases and 1,968 insufficient cases; 361
cases have grader disagreement. One referenced image object is missing. These are
metadata-audit counts, not training results.

Fitzpatrick17k, DDI, and ISIC were also reviewed. Fitzpatrick17k has useful skin-tone
annotations but broken/source-dependent image access, no verified subject IDs, and
CC BY-NC-SA terms. DDI has pathology-confirmed labels and patient grouping but
requires registration and is personal non-commercial research only. ISIC has openly
downloadable CC0 challenge subsets but contains dermoscopic lesion tasks unrelated
to facial cosmetic analysis.

The repository currently has no training framework, checkpoint, weight file, dataset
manifest, or inference adapter. This is intentional: adding them before a defensible
dataset and task definition would create a misleading baseline.

## Defensible task boundary

Potential future image labels must be limited to visible, annotatable properties.
The project must not infer allergies, hydration, sebum production, barrier health,
medical disease, or treatment response from ordinary selfies without appropriate
measurements, labels, and validation. Skin-type language must be defined by an
annotation protocol rather than inferred from demographic identity or appearance.

The proposed gradability task is separate from this boundary: it estimates image
evidence sufficiency, not skin condition, skin type, hydration, sebum, barrier
health, allergy, or disease.

## Planned data pipeline after the blocker is resolved

1. Register the dataset source, license, consent basis, label definitions, and
   version in a manifest outside Git for large files.
2. Validate image decoding, dimensions, missing labels, duplicate hashes, and class
   distribution.
3. For SCIN, split by `case_id` into train/validation/test. Never place images from
   the same case in multiple splits. Treat grader disagreement and the
   `YES_IMAGE_QUALITY_SUFFICIENT_NO_DISCERNIBLE_PATHOLOGY` value as explicit
   categories or an `unknown`/abstention state unless the binary quality-sufficiency
   mapping is pre-registered.
4. Define deterministic preprocessing and task-appropriate augmentations.
5. Record the random seed, dataset version, label mapping, environment, and hardware.
6. Train a single-image transfer-learning baseline first.
7. Evaluate macro-F1, per-class recall/precision, calibration, subgroup performance,
   and abstention/error cases before considering API integration.
8. Keep multi-view fusion, real-time inference, and calibrated confidence as later
   work.

## Baseline selection

Once the user completes authorized local retrieval and the manifest is verified,
start with a non-neural image-quality baseline (for example, documented
pixel/blur/exposure features plus logistic regression) as a sanity check. Then
compare a small ResNet-18 or EfficientNet-B0 transfer-learning classifier against
the dataset size and available hardware.
Prefer the smallest model that provides a reproducible, auditable baseline. Do not
select weights solely because a model is popular, and do not treat raw softmax scores
as calibrated probabilities.

## Explicitly not implemented

No real model, training run, model weights, diagnosis, treatment prescription, or
production predictor replacement is part of this repository yet. Only temporary
metadata copies were used for this audit and were removed after inspection.
