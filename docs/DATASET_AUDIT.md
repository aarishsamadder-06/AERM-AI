# Phase 2 Day 1-2 dataset audit

## Recommendation

Select **SCIN** for a narrowly scoped research baseline: **case/image gradability
classification**, meaning whether the available image evidence is sufficient for a
dermatologist to determine a skin condition. This is a capture-suitability task, not
cosmetic skin analysis, diagnosis, or treatment recommendation. It is the strongest
candidate reviewed here because access is public, gradability is explicitly
annotated, and stable case identifiers support leakage-safe grouping.

The recommendation is conditional. SCIN does not match AERM's controlled
front/left/right facial capture distribution, and its images show medical conditions.
The baseline should remain an offline data-preparation experiment and must not be
integrated into `/api/analyze` as a skin-feature or diagnostic predictor.

No dataset was downloaded, redistributed, or added to Git.

## Candidate comparison

| Candidate | Verified access and terms | Labels and approximate scale | Subject/grouping evidence | Fit for AERM and remaining risk |
|---|---|---|---|---|
| **SCIN** (recommended for gradability only) | Public `dx-scin-public-data` Google Cloud Storage bucket; access is described in the official repository and demo notebook. Custom SCIN Data Use License permits reproduction and adaptation subject to attribution, license notice, no additional downstream restrictions, and privacy/publicity limits. | 5,000+ volunteer contributions and 10,000+ images. Dermatologist gradability flags, differential condition labels, skin-tone labels, and user metadata are documented. Exact class distribution is not published in the README. | Stable `case_id`; up to three images per case. This supports case-aware splits, but a case is not a verified AERM front/left/right subject capture. | **Best available for an offline image-evidence/gradability gate.** Not a cosmetic-label source; medical/sensitive content, missing image, duplicates, and label gaps require validation. Commercial use and downstream packaging need legal review of the custom license and privacy terms. |
| **Fitzpatrick17k** | Official project repository provides CSV annotations and original image URLs; some URLs are broken and the authors offer an alternative image link after a form/contact step. Original images come from DermaAmin and Atlas Dermatologico under CC BY-NC-SA 3.0. | 16,577 clinical images, 114 skin conditions, at least 53 and at most 653 images per condition. Fitzpatrick labels are annotator labels for skin phenotype, not cosmetic skin health. | The published CSV has image hashes and URLs, but no verified person identifier for subject-aware splitting. | Useful for skin-tone annotation/fairness research, not a defensible cosmetic skin-type predictor. Non-commercial ShareAlike terms and inaccessible/source-dependent images make it unsuitable for this project's remaining time. |
| **DDI** (Diverse Dermatology Images) | Official Stanford project requires registration and agreement. Personal, non-commercial research only; no redistribution, commercial use, or clinical diagnosis/care; re-identification prohibited. | 656 clinical images from 570 unique patients. Pathology-confirmed diagnoses and curated Fitzpatrick I-VI skin-tone labels. | Patient count and matched diagnostic comparisons are documented, so patient-level grouping is possible. | High-quality but small, pathology/lesion-focused, access-controlled, and non-commercial. It cannot support AERM cosmetic claims and cannot be used in a commercial product without new permission. |
| **ISIC challenge data** | Official ISIC archive publishes challenge downloads; the 2016/2017 challenge tables identify CC0 releases for those subsets. | Example 2016 task: 900 training and 379 test dermoscopic lesion images with masks; 2017 task: 2,000 training images plus validation/test sets and diagnosis labels. | Challenge subsets expose image/lesion identifiers, but the reviewed official task pages do not establish person-level IDs for all images. | Strongest legal/access option for lesion segmentation or lesion classification, but dermoscopy and malignancy labels are unrelated to facial cosmetic analysis. Not appropriate for AERM's upload flow. |

The table compares source documentation rather than downloaded files. No class
counts, duplicate rates, or image statistics were inferred beyond what the official
sources state.

## Verified candidate: SCIN

- **Source:** [google-research-datasets/scin](https://github.com/google-research-datasets/scin)
- **Data access:** The repository points to the public `dx-scin-public-data` Google
  Cloud Storage bucket and documents a demo notebook for access.
- **Scale:** The project describes 5,000+ volunteer contributions and 10,000+ images.
  These are contribution/image totals, not a validated class distribution for AERM.
- **Labels:** The schema includes dermatologist-provided differential skin-condition
  labels, gradability flags, condition symptoms, body parts, self-reported
  Fitzpatrick skin type, dermatologist-estimated Fitzpatrick type, and Monk Skin
  Tone labels.
- **Image structure:** A case can contain up to three images with shot types such as
  `CLOSE_UP`, `AT_AN_ANGLE`, and `AT_DISTANCE`. This is not the same as a controlled
  front/left/right facial capture protocol.
- **Known data issues:** The project documents 15 duplicate images appearing 42
  times, 48 gradable cases without a skin-condition label, and one missing image.
- **License:** SCIN uses its own SCIN Data Use License. It grants broad use subject
  to attribution, license-notice, no additional downstream restrictions, and a
  strict prohibition on re-identifying or re-linking de-identified subjects. The
  license also disclaims endorsement and does not grant publicity/privacy rights.

Sources reviewed:

- [SCIN README](https://github.com/google-research-datasets/scin/blob/main/README.md)
- [SCIN schema](https://github.com/google-research-datasets/scin/blob/main/dataset_schema.md)
- [SCIN Data Use License](https://github.com/google-research-datasets/scin/blob/main/LICENSE)
- [SCIN missing-image issue](https://github.com/google-research-datasets/scin/issues/1)
- [SCIN DOI record](https://zenodo.org/doi/10.5281/zenodo.10819503)

## Why SCIN is not a cosmetic predictor dataset

SCIN's primary labels describe medical dermatology conditions and differential
diagnoses. Training AERM's existing cosmetic labels from those conditions would create
label leakage and an invalid semantic mapping. Ordinary photographs cannot support
claims about hydration, sebum production, skin-barrier health, allergies, or
dermatological disease without appropriate measurements, labels, and validation.

The dataset also does not establish that each case contains the three controlled
facial views required by `/api/analyze`, and the repository does not publish a
validated AERM-compatible class-count table. Those gaps must be resolved before a
reproducible split or training result can be claimed.

## Proposed Day 2 task

**Task:** binary case/image gradability classification using SCIN's
`dermatologist_gradable_for_skin_condition_*` labels.

**Intended output:** an offline research value such as `gradable` or `insufficient
image evidence`, with an abstention/unknown state when graders disagree or labels
are absent. It must not be surfaced as a medical diagnosis or as AERM's cosmetic
skin-profile confidence.

**Preparation constraints:**

- Split by `case_id`, never by individual image path.
- Exclude or separately report cases with missing labels, grader disagreement, or
  missing image files.
- Deduplicate by image hash and report the documented SCIN duplicates.
- Preserve the original license and attribution notice in any derived manifest or
  model release.
- Verify that the chosen label aggregation rule is documented before training.
- Measure class balance from the downloaded manifest; do not assume the distribution.

This task is useful to AERM only as a future upload-quality signal. It does not
replace the current predictor and does not validate any existing cosmetic concern
labels.

## Day 3 access verification and data inspection

The official SCIN demo notebook specifies:

- Google Cloud project: `dx-scin-public`
- Bucket: `dx-scin-public-data`
- Case metadata: `dataset/scin_cases.csv`
- Label metadata: `dataset/scin_labels.csv`
- Images: `dataset/images/`
- Colab authentication, or `gcloud` authentication when run locally

The bucket's official Google Cloud Storage JSON API was reachable during this audit.
Only the two CSV metadata files and object metadata were inspected; no image bytes
were downloaded, retained, or added to the repository. The SCIN license was reviewed
before this inspection.

### Verified manifest facts

The public CSV manifests and image-object listing returned these reproducible facts:

| Check | Result |
|---|---:|
| Case rows | 5,033 |
| Label rows | 5,033 |
| Unique case IDs | 5,033 |
| Duplicate case IDs in either CSV | 0 |
| Cases without a label row | 0 |
| Image path references | 10,407 |
| Unique referenced image paths | 10,380 |
| Listed image objects | 10,379 |
| Missing referenced image paths | 1 (`dataset/images/-2243186711511406658.png`) |
| Referenced-path duplicates | 27 |
| Cases with 1 / 2 / 3 images | 1,948 / 796 / 2,289 |
| `CLOSE_UP` / `AT_AN_ANGLE` / `AT_DISTANCE` references | 5,029 / 3,015 / 2,364 |

The 27 repeated path references are consistent with the repository's documented
statement that 15 duplicate images appear 42 times total. A content-hash audit of
the listed object metadata did not establish additional duplicate object files; the
image bytes were not downloaded for this check.

### Verified gradability facts

The label CSV contains three dermatologist gradability columns. Values observed are:

- `DEFAULT_YES_IMAGE_QUALITY_SUFFICIENT`
- `NO_IMAGE_QUALITY_INSUFFICIENT`
- `YES_IMAGE_QUALITY_SUFFICIENT_NO_DISCERNIBLE_PATHOLOGY`

There are no cases missing all gradability values. There are 3,065 cases whose
majority of available graders indicates **quality sufficient** after grouping the
two `YES` variants, and 1,968 cases whose majority indicates **insufficient**.
There are 361 cases with disagreement across the three available gradability
annotations; these must not be silently forced into a training label. There are
1,972 cases without a dermatologist condition-name label, which is expected for an
image-quality/gradability task but makes condition prediction unsuitable.

This supports a defensible **binary image-quality sufficiency** task if the mapping
and majority rule are documented. It does not by itself support binary
“condition determinable” classification, because “sufficient image quality but no
discernible pathology” is semantically distinct and should be retained for a
three-way or abstention-aware analysis.

## Go/no-go decision

- **GO:** metadata inspection and manifest/data-preparation work. The official access
  path, schema, case grouping, and gradability fields are verifiable.
- **CONDITIONAL GO:** an offline baseline after the user completes authorized local
  retrieval, confirms the SCIN license obligations for the intended use, and stores
  the data outside Git. Start with a majority-labelled binary image-quality task,
  retain disagreement/unknown cases for analysis, and split by `case_id`.
- **NO-GO:** training or integrating a real model into AERM today. The image files
  have not been locally downloaded and decoded, the source is medical-condition
  imagery rather than AERM facial selfies, and the task is only an upload-quality
  gate. The existing predictor and API must remain unchanged.

### Manual steps requiring user action

To prepare a local experiment, the user must:

1. Review and accept the SCIN Data Use License and confirm that the intended
   research/commercial context is permitted.
2. Authenticate through the official SCIN notebook in Colab, or install the Google
   Cloud CLI and authenticate locally as described by the notebook.
3. Retrieve the two CSV manifests and image objects into a protected, non-Git data
   directory. Do not place the data, credentials, or derived sensitive files in this
   repository.
4. Provide the local dataset root to a future preparation command so it can verify
   image decoding, dimensions, missing files, duplicate hashes, and the
   case-aware split.

No account approval was requested or bypassed during this audit. Public bucket
visibility was used only for the documented metadata endpoints.

Until then, the current deterministic simulator remains the only production
predictor. It is still clearly labelled as simulated and was not replaced.

## Baseline decision once data is available

Start with a documented non-neural image-quality baseline as a sanity check, then
compare a small ResNet-18 or EfficientNet-B0 transfer-learning classifier against the
dataset size and available hardware. Prefer the smallest model that provides a
reproducible, auditable baseline. Do not select weights solely because a model is
popular, and do not treat raw softmax scores as calibrated probabilities.

## Day 4 acquisition and validation

The official SCIN bucket and license were rechecked before acquisition. The bucket
was readable through its documented public Google Cloud Storage download route, so no
manual Google login or private credential was required for this transfer. The full
image payload is approximately 11.7 GiB; the transfer was stopped after network
throttling rather than claiming a complete download.

Downloaded data is stored outside the repository at:

`C:\Users\Aarish\AppData\Local\AERM-AI-data\scin-1.0.0`

The local acquisition currently contains the two CSV manifests, the SCIN license,
and a bounded partial image set. Incomplete `.part` files were removed after the
validation pass. No dataset file, archive, credential, or derived manifest was
placed in Git.

### Actual local validation

The validation inspected **352 image files across 340 cases**. All 352 files:

- decoded successfully with Pillow;
- were PNG files;
- matched an official `dataset/images/` manifest path;
- had no corrupt-file errors; and
- had no duplicate SHA-256 content groups within the acquired subset.

The 352 local references correspond to 352 official manifest references. The full
manifest still reports 10,407 references and one missing object; those full-corpus
facts were not reinterpreted as locally acquired files.

### Label policy and local split

The primary binary policy maps both quality-sufficient values to
`quality_sufficient`, maps `NO_IMAGE_QUALITY_INSUFFICIENT` to `insufficient`, and
excludes majority ties or grader disagreement from the primary binary split. Missing
or unknown labels remain outside the split.

For the 340 locally represented cases, no case was excluded by this policy. A
deterministic split using seed `20261030` was written outside Git to
`metadata\day4_case_split.csv`:

| Split | Cases | Quality sufficient | Insufficient | Image rows |
|---|---:|---:|---:|---:|
| Train | 272 | 170 | 114 | 284 |
| Validation | 34 | 19 | 15 | 34 |
| Test | 34 | 22 | 12 | 34 |

The split is case-aware: every image from a case remains in one split. The test
split has more image rows than cases because some cases contain multiple acquired
images. The external report is at `metadata\day4_validation_report.json`.

### Day 4 decision

This is **GO for acquisition/validation of the bounded subset** and **NO-GO for
training or production integration today**. The subset is too incomplete to
represent the full SCIN release, and SCIN remains a medical-condition image source
for an offline image-quality experiment rather than AERM cosmetic analysis.

Day 5 should either resume and complete the authorized transfer, or explicitly
freeze this subset as a pilot and document why its sampling is adequate before
training. No real model, accuracy, or API integration claim is made.

## Day 5 acquisition, validation, and baseline

The authorized resume completed 10,373 of the 10,379 listed image objects. Six
objects could not be retrieved because of timeout or remote-connection failures:
`-3726235413659361442.png`, `-4411279915061191754.png`,
`-4883252151958637737.png`, `-617765021333018481.png`,
`-6828666395047918317.png`, and `-844617859903194673.png`. Together with the one
manifest reference that is absent from the official object listing, seven
referenced paths are unavailable locally. No incomplete `.part` file is treated
as a validated image.

The completed local validation inspected 10,373 image bytes. All decoded with
Pillow and were PNG files; there were no corrupt files, unmatched local paths,
or duplicate SHA-256 content groups. The files covered 5,012 cases. The primary
label policy excluded 351 locally represented cases with any mixed gradability
labels; no locally represented case had all gradability labels missing. The
remaining 4,661 cases produced 9,392 image rows.

Using seed `20261030`, a deterministic case-aware split was written outside Git
to `metadata\day5_case_split.csv`:

| Split | Cases | Image rows | Quality sufficient | Insufficient |
|---|---:|---:|---:|---:|
| Train | 3,728 | 7,497 | 4,555 | 2,942 |
| Validation | 466 | 955 | 583 | 372 |
| Test | 467 | 940 | 590 | 350 |

No case or image hash appears in more than one split. The external validation
report is `metadata\day5_validation_report.json`.

### Offline baseline result

A genuine but intentionally lightweight baseline was trained offline using
21 handcrafted RGB, brightness, saturation, and finite-difference edge features,
`StandardScaler`, and class-weighted logistic regression. The checkpoint and
metrics are outside Git at
`metadata\day5-baseline-full\quality_baseline.pkl` and
`metadata\day5-baseline-full\quality_baseline_metrics.json`.

| Evaluation | Accuracy | Macro F1 | Majority accuracy | Majority macro F1 |
|---|---:|---:|---:|---:|
| Validation | 0.554 | 0.540 | 0.610 | 0.379 |
| Test | 0.601 | 0.588 | 0.628 | 0.386 |

The test confusion matrix, with labels `[insufficient, quality_sufficient]`, is
`[[199, 151], [224, 366]]`. The model improves macro F1 over the majority
baseline but not accuracy. This is an offline research result, not a calibrated
probability, production quality gate, cosmetic predictor, or medical model.

## Day 6 model comparison and finalization

The Day 5 baseline was independently reproduced from the external
`metadata\day5_case_split.csv` split. The same 3,728 train cases, 466 validation
cases, and 467 test cases were used for every candidate. The test set was not
used for model selection.

| Candidate | Validation accuracy | Validation macro F1 | Test evaluation |
|---|---:|---:|---|
| Logistic Regression, 21 features | 0.554 | 0.540 | Not selected |
| Random Forest, 21 features | 0.614 | 0.484 | Not selected |
| RBF SVM, 21 features | 0.591 | 0.562 | Selected |
| Logistic Regression, 28 quality features | 0.561 | 0.545 | Not selected |

The seven added quality features were aspect ratio, normalized dimensions,
grayscale contrast, under/overexposure proportions, and Laplacian sharpness.
They are image-derived and do not use labels, case identity, or split membership.
The RBF SVM was selected by validation macro F1, then evaluated once on the
untouched test set: accuracy 0.605, macro precision 0.572, macro recall 0.569,
and macro F1 0.570. Its confusion matrix was
`[[149, 201], [170, 420]]` for labels
`[insufficient, quality_sufficient]`. The majority baseline remained higher on
test accuracy at 0.628 but had macro F1 0.386.

The selected checkpoint and complete comparison report are outside Git at
`metadata\day6-model-comparison\selected_quality_model.pkl` and
`metadata\day6-model-comparison\model_comparison_metrics.json`. Independent
inference was verified using the checkpoint. Its SVM decision score is not a
calibrated probability. No SCIN result was integrated into AERM production.
