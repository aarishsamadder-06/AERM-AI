# AERM AI — catalogue and routine upgrade

A calm, responsive skin-analysis companion. Upload front, left, and right facial views to receive a deterministic simulated first read, gentle next steps, and ingredient-aware sample product matches.

## Included

- Next.js 14 + TypeScript + Tailwind frontend with `/`, `/analyze`, `/results`, `/routine`, and `/products`
- Upload cards with image previews, replacement, removal, file-type/size validation, loading and error states
- FastAPI `GET /api/health`, `POST /api/analyze`, `GET /api/products`, and `POST /api/recommendations`
- Health metadata identifies the service, demo mode, deterministic model, and whether the optional image-quality gate is configured; analysis and recommendations accept budget/fragrance preferences
- 32-product skincare catalogue across cleanser, moisturizer, sunscreen, and serum. Catalogue filters support category, brand, max budget, ingredient, fragrance-free, and sorting; cards show provenance, match explanation fields, and a graceful image placeholder.
- `/routine` is a local-session planner with morning/evening/weekly sections, catalogue alternatives, ingredient/usage details, completion progress/reset, and a weekly journal.
- `/signin`, `/signup`, and `/profile` use backend-owned local authentication with SQLite, PBKDF2 password hashing, and HTTP-only session cookies for development.
- In-memory image validation and preprocessing; no image persistence
- Pillow-backed decode and minimum 128×128 pixel validation, performed entirely in memory
- Clearly labelled deterministic Phase 1 simulation and ingredient-aware matching
- Optional SCIN image-gradability results for front, left, and right views, kept separate from cosmetic findings
- Logo, responsive visual system, frontend Vitest test, backend Pytest tests

## Run locally (exact startup)

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:3000. The frontend defaults to `http://localhost:8000`; set `NEXT_PUBLIC_API_URL` to override it.

Run the backend before using Analyze or Products. If PowerShell execution policy blocks activation, run `backend\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000` from `backend` instead.

Authentication uses an external-to-Git SQLite file at `backend/.aerm-data/auth.sqlite3`
by default. Local development generates a random per-process session secret when
`AERM_SESSION_SECRET` is unset. Production requires `AERM_ENV=production`,
`AERM_SESSION_SECRET` with at least 32 characters, `AERM_COOKIE_SECURE=true`,
and an explicit `AERM_ALLOWED_ORIGINS` value. Production must run behind HTTPS.
The cookie policy defaults to `SameSite=Lax`; only use `SameSite=None` with HTTPS
and `Secure` cookies. Never use `*` with credentialed CORS.

For local HTTP development:

```powershell
$env:AERM_ENV = "development"
$env:AERM_COOKIE_SECURE = "false"
$env:AERM_COOKIE_SAMESITE = "lax"
$env:AERM_ALLOWED_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000"
```

For production, provide secrets through the deployment secret manager rather than
committing a `.env` file:

```text
AERM_ENV=production
AERM_SESSION_SECRET=<random value of at least 32 characters>
AERM_COOKIE_SECURE=true
AERM_COOKIE_SAMESITE=lax
AERM_ALLOWED_ORIGINS=https://your-frontend.example
AERM_QUALITY_MODEL_SHA256=<sha256 of the trusted external checkpoint>
```

Unsafe cookie-authenticated requests use a CSRF double-submit token. The frontend
obtains `/api/auth/csrf` and sends `X-CSRF-Token` for logout; keep this protection
for future authenticated mutations.

### Optional SCIN image-quality gate

Keep the verified checkpoint outside Git and configure it before starting the
backend:

```powershell
$env:AERM_QUALITY_MODEL_PATH = "C:\Users\Aarish\AppData\Local\AERM-AI-data\scin-1.0.0\metadata\day6-model-comparison\selected_quality_model.pkl"
cd backend
uvicorn app.main:app --reload --port 8000
```

`GET /api/health` then reports `image_quality_gate_configured: true`. The
results page shows one `quality_sufficient` or `insufficient` status per view.
The raw SVM decision score is displayed only as a decision score, never as a
probability or skin-analysis confidence. If the variable is unset, the API
returns `image_quality: null` and the existing results flow remains compatible.

## Validation

```powershell
cd frontend
npm run test
npm run build

cd ..\backend
pytest
```

## Authentication API

- `POST /api/auth/register` creates an account, hashes the password, and starts a session.
- `POST /api/auth/login` verifies credentials and starts a session.
- `GET /api/auth/me` returns the current session user or `401`.
- `POST /api/auth/logout` revokes the current session and clears the cookie.

The current implementation is suitable for local academic demonstration. It does
not yet include email verification, password-reset email delivery, rate limiting,
account deletion, migrations, or production database operations.

The SCIN checkpoint is a Python pickle and must be treated as executable trusted
input. Keep it outside Git, restrict filesystem write access, and set
`AERM_QUALITY_MODEL_SHA256` in production so the API verifies the exact artifact
before loading it. The checkpoint remains image-gradability-only and is not a
cosmetic or medical diagnosis model.

## Data provenance and known issues

The catalogue uses established brands only for high-confidence, broadly published product names/ingredient themes. Entries labelled `AERM sample` are illustrative and must not be interpreted as retailer listings; all catalogue prices and availability are approximate and should be verified before purchase. Product images are intentionally placeholders unless a trusted image URL is configured.

Profile authentication is functional for local development. Analysis history,
account recovery, email verification, and persistent routine/history storage are
not implemented. Routine state remains local to the current browser. Product
matching and cosmetic skin findings remain deterministic simulation.
The optional SCIN gate is genuine ML for image gradability only; it does not
predict acne, pigmentation, hydration, sebum, allergies, skin type, barrier
health, or diagnosis.

## Phase 2 Day 1 ML audit

The repository does not contain a dataset, training module, model weights, or trained
inference path. The current predictor remains a deterministic simulation. A verified
SCIN dataset audit is documented in [`docs/DATASET_AUDIT.md`](docs/DATASET_AUDIT.md);
SCIN is a medical dermatology-condition dataset and is not being used as a cosmetic
selfie label source. No dataset was downloaded or added to Git.

Production cosmetic training remains blocked until a consented, license-compatible
dataset provides explicit non-medical cosmetic labels and subject identifiers for
leakage-safe splits. The repository's offline SCIN work is only an image-gradability
research experiment.

An offline SCIN image-gradability baseline and optional FastAPI quality gate now
exist under `backend/ml/` and `backend/app/services/quality_gate.py`. The gate
uses external data/checkpoint files only and does not replace the production
simulator. Run the experiment with the command in
[`backend/ml/README.md`](backend/ml/README.md) after acquiring SCIN outside Git.
The verified checkpoint runtime is `scikit-learn==1.8.0`. Day 1
pretrained-model research is documented in [`docs/MODEL_PLAN.md`](docs/MODEL_PLAN.md);
no unverified dermatology checkpoint has been connected to the application.

## Phase 1 and Phase 2 boundary

This is educational software, not a medical diagnostic tool. Phase 2 has not
replaced the cosmetic predictor: no cosmetic trained inference, clinical claims,
payments, or deployment infrastructure is implemented. Local demonstration
authentication and a SQLite session store are implemented, but account history,
email verification, password recovery, and production database operations are
not. The separate SCIN integration is image-gradability research only and is not
cosmetic or medical skin analysis.

## Final model benchmark decision

The verified production quality model remains the Day 6 RBF SVM. Its validation
macro F1 was `0.562`, compared with `0.545` for the quality-feature logistic
regression, `0.540` for logistic regression, and `0.484` for random forest. On
the untouched test split it achieved accuracy `0.605`, macro F1 `0.570`, and
insufficient-class recall `0.426`; these results are not clinical validation.

The requested deep-learning candidates were not benchmarked in this environment
because PyTorch, torchvision, and Transformers are unavailable and no verified
candidate checkpoints were present locally. No unverified architecture was
integrated. The RBF checkpoint remains external at
`C:\Users\Aarish\AppData\Local\AERM-AI-data\scin-1.0.0\metadata\day6-model-comparison\selected_quality_model.pkl`.

## Practical demonstration sequence

1. Start FastAPI with the optional checkpoint configured, then confirm
   `http://localhost:8000/api/health` returns `status: "ok"` and
   `image_quality_gate_configured: true`.
2. Start Next.js and open `http://localhost:3000`.
3. Open Analyze, add front, left, and right images, and verify previews,
   replacement, removal, and the loading state.
4. Submit the analysis and inspect the separate Capture check panel. Retry any
   view marked `Quality insufficient`; treat its score as a raw decision score.
5. Confirm the green simulated first-analysis card and product matches are
   clearly separate from the quality results.
6. Open Products and Routine to demonstrate catalogue filtering, matching, and
   local routine planning.

If the checkpoint is unavailable, unset `AERM_QUALITY_MODEL_PATH` to demonstrate
the backward-compatible `image_quality: null` flow. A missing configured
checkpoint is reported as an explicit backend error rather than silently
falling back.
