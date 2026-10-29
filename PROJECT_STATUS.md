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
