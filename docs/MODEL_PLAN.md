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

## Phase 2 Day 4 acquisition status

The official public transfer route was used after reviewing the SCIN Data Use License.
No private credentials or access-control bypass was used. The full SCIN image payload
is approximately 11.7 GiB; network throttling prevented completion in this work
session, so training is intentionally deferred.

The external data directory
`C:\Users\Aarish\AppData\Local\AERM-AI-data\scin-1.0.0` contains the official CSV
manifests and license plus 352 verified PNG files from 340 cases. All decoded
successfully, matched manifest paths, and had no duplicate SHA-256 groups in the
acquired subset. A deterministic case-aware 80/10/10 split was created outside Git
with seed `20261030`: 272 train cases, 34 validation cases, and 34 test cases.

The binary label policy is explicit: group both quality-sufficient values as the
positive class, map insufficient quality to the negative class, and exclude
disagreement/ties or unknown labels from the primary split. This subset validation
does not establish full-release image statistics or model readiness.

## Explicitly not implemented

No real model, training run, model weights, diagnosis, treatment prescription, or
production predictor replacement is part of this repository yet. Only temporary
metadata copies used during the earlier audit were removed; the Day 4 external
dataset directory is intentionally retained outside the repository for the next
authorized continuation.

## Phase 2 Day 5 baseline

The official transfer completed 10,373 of 10,379 listed image objects. Six
downloads failed due to network timeouts/connection closure, and one additional
manifest reference is absent from the official object listing. The complete
local validation found 10,373 readable PNG files, zero corrupt files, zero
unmatched local paths, and zero duplicate SHA-256 groups. Data remains outside
Git at `C:\Users\Aarish\AppData\Local\AERM-AI-data\scin-1.0.0`.

After excluding 351 locally represented disagreement cases, 4,661 cases and
9,392 image rows were split by `case_id` with seed `20261030`: 3,728 train
cases/7,497 rows, 466 validation cases/955 rows, and 467 test cases/940 rows.
The split is recorded externally as `metadata\day5_case_split.csv`.

A non-neural baseline using 21 deterministic image features, standardization,
and class-weighted logistic regression was trained and evaluated. Validation
accuracy/macro-F1 were 0.554/0.540; test accuracy/macro-F1 were 0.601/0.588.
The majority baseline was stronger on accuracy (0.610 validation and 0.628 test)
but weaker on macro-F1 (0.379 validation and 0.386 test). The checkpoint is
external at `metadata\day5-baseline-full\quality_baseline.pkl`.

This result is sufficient to prove the offline pipeline is reproducible, not to
justify deployment. PyTorch/torchvision were unavailable, so no ResNet-18
comparison was run. The baseline is not integrated into FastAPI or the frontend;
the deterministic cosmetic simulator remains unchanged. Raw scores are not
calibrated confidence values.

## Phase 2 Day 6 model comparison

The saved Day 5 result was reproduced from the external
`metadata\day5_case_split.csv` manifest. The split contains 3,728 train cases,
466 validation cases, and 467 test cases after excluding 351 locally represented
gradability-disagreement cases. All images from each case remain in one split.

Three models were compared on the same 21-feature matrix:

| Candidate | Validation accuracy | Validation macro F1 | Fit time |
|---|---:|---:|---:|
| Logistic Regression, class-weighted | 0.554 | 0.540 | 0.06 s |
| Random Forest, class-weighted | 0.614 | 0.484 | 1.55 s |
| RBF SVM, class-weighted | 0.591 | 0.562 | 3.10 s |

Seven additional capture-quality features were also evaluated with logistic
regression: aspect ratio, normalized dimensions, grayscale contrast,
under/overexposure proportions, and Laplacian sharpness. This 28-feature variant
reached validation accuracy 0.561 and macro F1 0.545, so it was not selected.
These features are derived only from image pixels and dimensions; they do not
encode labels, case IDs, or split membership.

The RBF SVM was selected by validation macro F1. It was then evaluated once on
the untouched test set: accuracy 0.605, macro precision 0.572, macro recall
0.569, and macro F1 0.570. The confusion matrix
`[[149, 201], [170, 420]]` uses labels
`[insufficient, quality_sufficient]`. The majority baseline reached test accuracy
0.628 and macro F1 0.386. The selected model therefore improves balanced
performance but not raw accuracy.

The external selected checkpoint is
`C:\Users\Aarish\AppData\Local\AERM-AI-data\scin-1.0.0\metadata\day6-model-comparison\selected_quality_model.pkl`,
with metrics in the adjacent `model_comparison_metrics.json`. Independent
inference returns a class label and SVM decision score; it is not a calibrated
probability. The checkpoint is not connected to FastAPI or the frontend.

This comparison does not make SCIN a cosmetic dataset and does not justify
predicting skin type, acne severity, hydration, sebum, allergies, barrier health,
or medical diagnosis. The existing deterministic AERM predictor remains the
production path.

## Day 1 pretrained-model audit

The verified local runtime is Python with Pillow, NumPy, and
`scikit-learn==1.8.0`. The external SCIN RBF SVM checkpoint loads successfully
under that version and produces a raw image-gradability decision score. It remains
the only model verified end to end in the current environment.

| Candidate | Verified artifacts and task | License/access | Day 1 decision |
|---|---|---|---|
| `LaurianeMD/vit-skin-disease` | Public `model.safetensors` (343,285,496 bytes), ViT-Base/16, 224x224, 22 dermatological condition classes; Transformers loading path documented | Model card license is marked “More Information Needed”; underlying dataset is linked to a Kaggle skin-disease dataset | Do not select until licensing and label provenance are resolved; not a cosmetic predictor |
| `redlessone/DermFM-Zero` | Public Hugging Face model; PanDerm-L/16 plus PubMedBERT, prompt-based zero-shot dermatology classification, native-resolution support | CC BY-NC-ND 4.0, non-commercial academic research; access terms/login required; heavyweight PyTorch/open-clip stack | Not practical for this deadline or commercial/hosted integration |
| `google/derm-foundation` | Public Hugging Face TensorFlow/Keras model; 448x448 PNG input and 6,144-dimensional embedding output | Health AI Developer Foundations Terms of Use; distribution/hosted-service restrictions apply | Not a direct predictor; would require a separately trained downstream classifier |
| `imfarzanansari/skintelligent-acne` | Public `model.safetensors` (343,233,204 bytes), Transformers image classifier with levels -1 through 4 | MIT checkpoint license; model card provides the severity labels | Technically plausible after installing PyTorch/Transformers, but only acne severity and not validated for this app or current labels |

The model-card metrics and claims above were not treated as AERM results. No
pretrained candidate was downloaded or integrated on Day 1. The repository has no
PyTorch, torchvision, Transformers, or TensorFlow dependency, and adding a
~343 MB checkpoint plus a deep-learning runtime without a validated task would
not produce a defensible cosmetic analysis.

### Practical integration design

1. Keep the existing `POST /api/analyze` contract and in-memory upload validation.
2. Run the SCIN SVM as an optional, separate image-quality gate before any future
   skin-analysis model; never map its label to skin type, acne, hydration,
   sebum, allergy, barrier health, or diagnosis.
3. Add a future model adapter under `backend/app/services/` only after a model
   has verified weights, explicit labels matching the supported output, tested
   preprocessing, and representative validation data.
4. Convert the adapter output into the existing structured response only through
   explicitly supported cosmetic labels; keep recommendation matching rule-based
   until those labels are genuinely validated.
5. Add model loading/inference tests and startup health metadata before changing
   frontend behavior.

Day 2 should either validate a legally usable, technically compatible acne or
cosmetic model on representative images, or stop and preserve the simulator.
No genuine cosmetic predictor is selected by this audit.

## Day 2 verified integration boundary

Because no pretrained cosmetic model with verified labels and licensing was
available, the only genuine ML capability integrated is the SCIN image-gradability
gate. It is implemented in `backend/app/services/quality_gate.py` and is enabled
only when `AERM_QUALITY_MODEL_PATH` points to the external Day 6 RBF SVM checkpoint.
The gate evaluates front, left, and right uploads independently and adds an
optional `image_quality` object to `AnalysisResponse`.

The existing simulated `finding`, concern literals, recommendations, routine, and
product matching are unchanged. The SCIN labels are never converted into acne,
skin type, hydration, sebum, allergy, pigmentation, barrier, or diagnosis
outputs. Without the environment variable, the field is `null`; with an invalid
configured path, the API returns HTTP 503 explicitly.
