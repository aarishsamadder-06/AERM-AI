# Project status

## AERM AI catalogue/routine upgrade — complete

- Replaced the incorrect plant/leaf flow with skin-specific language and routes.
- Added responsive landing, analysis, results, routine, and products experiences.
- Added front/left/right image cards with previews, replacement, removal, validation, loading, and error states.
- Added the requested FastAPI endpoints and in-memory multipart validation.
- Added deterministic, explicitly simulated skin findings.
- Added sample skincare products and ingredient-aware recommendation matching.
- Expanded the catalogue to 32 entries across cleanser, moisturizer, sunscreen, and serum with explicit source/sample provenance and stable placeholder imagery.
- Added catalogue API filtering/sorting by category, brand, max budget, ingredient, and fragrance-free.
- Reworked Routine into a morning/evening/weekly planner with catalogue alternatives, progress/reset, usage details, and local journal state.
- Added polished validation/loading/unavailable messaging for sign-in and sign-up, plus a clearly gated profile placeholder.
- Added API-backed frontend calls, logo usage, README, architecture documentation, and model plan.
- Added frontend and backend coverage for the Phase 1 contract.

## Configuration required

Authentication is intentionally not wired. Configure a real provider and secure server-side sessions before enabling profile/history. Do not treat the sign-in forms as an auth implementation.

## Known issues / not included

Trained ML, diagnosis, authentication, persistence, accounts, history, payments,
and clinical workflows remain out of scope until their prerequisites are available.
Catalogue prices/availability and third-party product facts can change; verify
independently.

## Phase 2 Day 1 — dataset and ML foundation status

- [x] Audited the existing predictor/API/frontend contract and preserved the
  deterministic production simulator.
- [x] Verified the public SCIN repository, schema, known data issues, access path, and
  SCIN Data Use License.
- [x] Documented why SCIN is not a valid label source for AERM's current cosmetic
  selfie-based task.
- [x] Documented the proposed single-image transfer-learning baseline and
  subject-aware split requirements.
- [x] Added `docs/DATASET_AUDIT.md` with sources and the exact blocker.
- [ ] Add a real dataset manifest, training loader, or model weights.
- [ ] Train or evaluate a real model.
- [ ] Replace the production simulator with real inference.

### Day 1 blocker

No consented, license-compatible dataset with explicit cosmetic facial labels and
subject identifiers is available in the repository or verified for this task. SCIN
contains medical dermatology-condition labels and cannot be safely remapped to
AERM's cosmetic labels. No data was downloaded or redistributed, and no fabricated
training data was created.

## Phase 2 Day 2 — dataset discovery and task selection

- [x] Compared SCIN, Fitzpatrick17k, DDI, and ISIC using official project pages,
  schemas/access instructions, and license or research-use terms.
- [x] Selected SCIN condition-gradability labels for a narrowly scoped offline
  capture-suitability baseline, not cosmetic skin analysis or diagnosis.
- [x] Documented why the selected task must not replace the current predictor or map
  to the existing cosmetic concern literals.
- [x] Documented access, license, label, grouping, and time-risk caveats for each
  candidate.
- [ ] Obtain authorized SCIN data access and verify the downloaded manifest.
- [ ] Measure actual class distribution, image dimensions, corruption, and duplicate
  rates from local files.
- [ ] Implement or train a dataset-specific baseline.

### Day 2 blocker

SCIN still requires manual retrieval and license/privacy compliance, and no dataset
files are present locally. The recommendation is therefore evidence-based but not a
claim that the data has been downloaded, validated, or trained. The production API,
frontend flow, recommendation engine, and deterministic simulator remain unchanged.

## Phase 2 Day 3 — access verification and training readiness

- [x] Followed the official SCIN notebook access instructions and confirmed the
  documented bucket, CSV paths, image prefix, and authentication options.
- [x] Verified the public metadata endpoints after reviewing the SCIN Data Use
  License; no image bytes were downloaded or retained.
- [x] Inspected the actual CSV schemas and joined 5,033 case rows to 5,033 label
  rows with unique case IDs.
- [x] Counted 10,407 image references, 10,379 listed image objects, one missing
  referenced image, and 27 repeated path references.
- [x] Verified gradability encodings and counted 3,065 majority quality-sufficient,
  1,968 majority insufficient, and 361 disagreement cases after an explicit binary
  mapping.
- [x] Confirmed `case_id` is the leakage-prevention grouping key.
- [x] Made a conditional go decision for an offline image-quality baseline only.
- [ ] Complete user-authorized local image retrieval and decode/dimension validation.
- [ ] Implement the manifest, case-aware split, baseline, and evaluation scripts.
- [ ] Train or evaluate a real model.
- [ ] Replace the production simulator with real inference.

### Day 3 decision and remaining blocker

SCIN is **GO for metadata/data preparation** and **CONDITIONAL GO for an offline
baseline** after the user completes authorized retrieval and confirms the license
context. It is **NO-GO for AERM API integration** because it is medical-condition
imagery, not controlled facial cosmetic data, and the proposed task is only an
image-quality gate. The existing predictor, API contract, frontend, and
recommendation flow remain unchanged.

## Phase 2 Day 4 — dataset acquisition and validation

- [x] Re-read the SCIN license and used the documented public storage download route.
- [x] Confirmed that no manual login or private credential was required for the
  public transfer path used here.
- [x] Acquired the official CSV manifests and license outside Git.
- [x] Acquired and inspected 352 PNG image files across 340 cases outside Git.
- [x] Confirmed zero Pillow decode failures, zero unmatched local image paths, and
  zero duplicate SHA-256 groups in the acquired subset.
- [x] Applied the explicit binary label policy and created a deterministic,
  case-aware split outside Git with seed `20261030`.
- [ ] Complete the full approximately 11.7 GiB image transfer; network throttling
  stopped the current partial acquisition.
- [ ] Validate full-release dimensions, formats, file sizes, missing files, and
  duplicate content after acquisition completes.
- [ ] Decide whether the completed data supports a baseline after checking sampling
  and class balance.
- [ ] Train or evaluate a real model.
- [ ] Replace the production simulator with real inference.

### Day 4 decision and Day 5 plan

Day 4 is **GO for bounded acquisition/validation** and **NO-GO for training or
production integration**. The validated data is a partial SCIN subset, not the full
release, and SCIN remains an offline medical-image gradability experiment unrelated
to AERM's cosmetic predictor. The external data directory is
`C:\Users\Aarish\AppData\Local\AERM-AI-data\scin-1.0.0`.

Day 5 should resume the authorized transfer from that directory, remove any
incomplete files, repeat the full manifest/image validation, and only then decide
whether a non-neural image-quality baseline is justified. No model weights,
training metrics, API changes, or frontend changes exist.

## Phase 2 Day 5 — complete ML baseline

- [x] Resumed the official transfer without bypassing access controls; 10,373 of
  10,379 listed image objects completed.
- [x] Recorded six network failures and the one additional missing manifest path.
- [x] Validated 10,373 image bytes: all decoded as PNG, with zero corrupt files,
  zero unmatched local paths, and zero duplicate SHA-256 groups.
- [x] Applied the disagreement policy: 351 locally represented cases with mixed
  gradability labels were excluded from the primary binary dataset.
- [x] Created the deterministic case-aware split outside Git with seed `20261030`:
  3,728 train cases/7,497 rows, 466 validation cases/955 rows, and 467 test
  cases/940 rows.
- [x] Trained and evaluated a reproducible 21-feature class-weighted logistic
  regression baseline outside Git.
- [x] Compared the baseline with a majority-class baseline using accuracy,
  precision, recall, macro F1, confusion matrices, and per-class metrics.
- [x] Added repository-side ML module and tests without changing the production
  predictor, API, frontend, or recommendation flow.

### Day 5 results and boundary

Validation accuracy/macro-F1 were `0.554/0.540`; test accuracy/macro-F1 were
`0.601/0.588`. Majority accuracy was `0.610` validation and `0.628` test, with
macro F1 `0.379` and `0.386`. The baseline improves macro F1 but not accuracy,
and is not reliable enough for deployment or integration. The external
checkpoint is
`C:\Users\Aarish\AppData\Local\AERM-AI-data\scin-1.0.0\metadata\day5-baseline-full\quality_baseline.pkl`.
PyTorch/torchvision were unavailable, so a ResNet-18 comparison was not run.
SCIN remains an offline image-gradability experiment, not a cosmetic or medical
predictor. Day 6 is needed for either the six-file retrieval retry and/or a
transfer-learning comparison; production integration remains out of scope.

## Phase 2 Day 6 — model improvement and finalization

- [x] Re-verified the saved Day 5 metrics and reproduced the 21-feature baseline
  from the external case-aware split.
- [x] Compared Logistic Regression, Random Forest, and RBF SVM on identical
  training/validation rows with class weighting where supported.
- [x] Added and evaluated seven non-leaky capture-quality features: aspect ratio,
  normalized dimensions, contrast, under/overexposure proportions, and Laplacian
  sharpness.
- [x] Selected the model using validation macro F1 only, with validation accuracy
  and fit time as tie-breakers; the test set was evaluated once afterward.
- [x] Saved the selected checkpoint and complete comparison metrics outside Git.
- [x] Verified independent checkpoint inference and retained the production
  predictor, FastAPI contract, frontend, and recommendation engine unchanged.

### Day 6 comparison

| Candidate | Validation accuracy | Validation macro F1 | Fit time |
|---|---:|---:|---:|
| Logistic Regression, 21 features | 0.554 | 0.540 | 0.06 s |
| Random Forest, 21 features | 0.614 | 0.484 | 1.55 s |
| RBF SVM, 21 features | 0.591 | 0.562 | 3.10 s |
| Logistic Regression, 28 quality features | 0.561 | 0.545 | 0.05 s |

The RBF SVM was selected by validation macro F1. On the untouched test set it
achieved accuracy `0.605`, macro F1 `0.570`, macro precision `0.572`, and macro
recall `0.569`. Its confusion matrix, with labels
`[insufficient, quality_sufficient]`, was `[[149, 201], [170, 420]]`.
The majority baseline achieved test accuracy `0.628` and macro F1 `0.386`.
Therefore the selected model improves macro F1 but not accuracy and is not
validated for deployment.

The external checkpoint is
`C:\Users\Aarish\AppData\Local\AERM-AI-data\scin-1.0.0\metadata\day6-model-comparison\selected_quality_model.pkl`;
metrics are in the adjacent `model_comparison_metrics.json`. The score is a
decision score, not calibrated confidence. No inference integration was performed.

### Day 6 completion decision

Day 6 is complete for the planned offline comparison and finalization. The project
is ready for a Phase 1/early-Phase-2 demonstration of the existing application,
with the SCIN experiment shown only as a separate research artifact. It is not
ready to demonstrate ML-powered cosmetic skin analysis. Remaining work includes
retrying six unavailable SCIN files if needed, broader external validation,
calibration, subgroup/error analysis, and a genuinely suitable cosmetic dataset.

## Phase 2 Day 1 — pretrained model selection and inference audit

- [x] Audited Git state, API contracts, upload workflow, predictor, dependencies,
  SCIN tooling, and external checkpoint location.
- [x] Verified the SCIN RBF SVM with `scikit-learn==1.8.0` and ran sample inference.
- [x] Verified public weight availability and documented preprocessing, labels,
  licenses, and limitations for LaurianeMD ViT Skin Disease, DermFM-Zero,
  Google Derm Foundation, and the MIT acne-severity checkpoint.
- [x] Kept the SCIN image-gradability model separate from cosmetic skin analysis.
- [x] Documented an integration design without changing `/api/analyze`, the
  production predictor, frontend behavior, or recommendation engine.
- [ ] Select and integrate a genuine cosmetic predictor; no Day 1 candidate has
  verified labels and validation suitable for that purpose.

### Day 1 decision

The practical verified model remains the external SCIN RBF SVM for an offline
image-gradability signal only. No pretrained skin-condition model is selected for
production integration: LaurianeMD has incomplete license metadata, DermFM-Zero
is non-commercial and heavyweight, Google Derm Foundation is an embedding model
under HAI-DEF terms, and the acne model has a narrower unsupported output scope.
The existing deterministic predictor remains the application path.

## Phase 2 Day 2 — verified image-quality integration

- [x] Added an isolated SCIN RBF SVM adapter at
  `backend/app/services/quality_gate.py`.
- [x] Reused the exact 21-feature extraction path from `backend/ml/quality_baseline.py`
  for in-memory FastAPI uploads.
- [x] Added optional per-view `image_quality` output to `AnalysisResponse` without
  removing or changing existing fields.
- [x] Added explicit `AERM_QUALITY_MODEL_PATH` configuration; unset means `null`,
  while an invalid configured checkpoint returns HTTP 503.
- [x] Preserved the SCIN model as image-gradability only and left cosmetic
  findings/recommendations simulated and rule-based.
- [x] Added adapter/API tests and verified the real external checkpoint through
  the analysis route.

### Day 2 boundary

No acne, skin-type, hydration, allergy, pigmentation, sebum, barrier-health, or
diagnostic inference was added. Frontend behavior was not changed; existing
clients remain compatible because `image_quality` is optional. Day 3 may add an
explicit frontend display for the separate quality signal, but must not present it
as cosmetic analysis or medical confidence.

## Phase 2 Day 3 — frontend and end-to-end integration

- [x] Added optional `image_quality` TypeScript types matching the FastAPI
  response schema.
- [x] Added separate front, left, and right image-quality status cards to the
  results page.
- [x] Added explicit retry guidance for `quality_insufficient` views and kept
  raw SVM decision scores labelled as non-probability scores.
- [x] Preserved the legacy `image_quality: null` response path and all existing
  upload, navigation, catalogue, routine, and simulated-result behavior.
- [x] Verified the real external checkpoint through FastAPI and confirmed the
  frontend-compatible per-view payload.

### Day 3 boundary

The frontend displays image gradability separately from the simulated cosmetic
finding. No acne, pigmentation, hydration, sebum, allergy, skin-type, barrier,
or diagnostic prediction is presented. The SCIN score is never rendered as
confidence or probability.

## Phase 4 — final QA and project completion

- [x] Audited the frontend pages, upload workflow, results display, catalogue,
  routine, authentication placeholders, backend routes, schemas, predictor,
  quality gate, and environment configuration.
- [x] Completed backend, frontend, production-build, Python compilation,
  whitespace, and configured-checkpoint integration validation.
- [x] Added the practical local demonstration sequence and corrected stale
  documentation that described the integrated quality gate as offline-only.
- [x] Verified edge-case handling for missing uploads, unsupported/corrupt/tiny
  images, invalid checkpoints, unconfigured quality gate behavior, and backend
  errors.

### Final project boundary

The demonstrable application combines a genuine SCIN image-gradability gate
with explicitly simulated cosmetic findings and rule-based recommendations.
The SCIN model is not validated for cosmetic skin analysis or medical diagnosis.
External dataset files and the checkpoint remain outside Git. Authentication,
persistence, accounts, clinical workflows, payments, production deployment, and
cosmetic trained inference remain future work.

## Authentication implementation

- [x] Added local SQLite user and session persistence outside Git.
- [x] Added PBKDF2 password hashing with per-user random salts.
- [x] Added register, login, current-user, and logout endpoints.
- [x] Added HTTP-only, SameSite-configured session cookies and session revocation.
- [x] Connected Sign Up, Sign In, Profile, and navigation to the backend session.
- [x] Added backend registration/login/logout/session regression coverage.
- [ ] Add email verification, password reset delivery, rate limiting, migrations,
  account deletion, and production database operations.

## Final model benchmark decision

- [x] Rechecked the external Day 6 metrics and selected RBF SVM checkpoint.
- [x] Confirmed the existing four-candidate traditional comparison remains
  reproducible with the case-aware train/validation/test split.
- [x] Confirmed the current environment lacks PyTorch, torchvision, and
  Transformers, so the requested deep-learning candidates were not benchmarked.
- [x] Retained the RBF SVM and preserved the existing FastAPI response contract,
  per-view quality labels, error handling, and frontend integration.
- [x] Kept model artifacts outside Git.

The RBF SVM remains the best verified candidate in this environment by
validation macro F1 (`0.562`) and insufficient-class recall (`0.430` on
validation). Its untouched test results are accuracy `0.605`, macro F1 `0.570`,
and insufficient-class recall `0.426`. These are SCIN image-gradability results,
not cosmetic or clinical performance. Because the deep-learning candidates
could not be executed or verified locally, no claim of comprehensive
architecture superiority is made and no replacement was integrated.

## Security and deployment hardening

- [x] Removed the predictable production session-secret fallback. Local
  development uses a random per-process secret when no secret is supplied;
  production requires `AERM_SESSION_SECRET` with at least 32 characters.
- [x] Required `AERM_COOKIE_SECURE=true` in production and validated
  `AERM_COOKIE_SAMESITE`; `SameSite=None` requires Secure cookies.
- [x] Made credentialed CORS origins configurable with
  `AERM_ALLOWED_ORIGINS`; wildcard origins are rejected.
- [x] Added a CSRF double-submit token for cookie-authenticated logout and wired
  the frontend to send the token.
- [x] Added production checkpoint SHA-256 verification through
  `AERM_QUALITY_MODEL_SHA256` and documented pickle trust requirements.
- [x] Expanded `.gitignore` and verified local auth databases and model artifacts
  are not tracked.

Production prerequisites are HTTPS, a secret-managed session secret, explicit
frontend origins, a writable protected database location, and a trusted
read-only external SCIN checkpoint with a configured SHA-256 digest. The SCIN
model remains image-gradability-only; cosmetic findings remain simulated.

## Free deployment preparation

- [x] Added psycopg v3 PostgreSQL support selected by `DATABASE_URL`.
- [x] Preserved SQLite as the local fallback when `DATABASE_URL` is unset.
- [x] Added PostgreSQL-safe `users` and `sessions` initialization while
  preserving PBKDF2 hashes, session expiry, revocation, and CSRF behavior.
- [x] Added a server-side Next.js `/api/*` rewrite using `API_BASE_URL`; no
  database credentials or backend URL are exposed through `NEXT_PUBLIC_*`.
- [x] Added Vercel, Render, and Supabase setup documentation.

Live Supabase connectivity was not tested because no database credentials were
provided. The local SQLite suite and PostgreSQL driver installation were
verified; production deployment remains intentionally unperformed.
