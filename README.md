# AERM AI — catalogue and routine upgrade

A calm, responsive skin-analysis companion. Upload front, left, and right facial views to receive a deterministic simulated first read, gentle next steps, and ingredient-aware sample product matches.

## Included

- Next.js 14 + TypeScript + Tailwind frontend with `/`, `/analyze`, `/results`, `/routine`, and `/products`
- Upload cards with image previews, replacement, removal, file-type/size validation, loading and error states
- FastAPI `GET /api/health`, `POST /api/analyze`, `GET /api/products`, and `POST /api/recommendations`
- Health metadata identifies the service, demo mode, and deterministic model; analysis and recommendations accept budget/fragrance preferences
- 32-product skincare catalogue across cleanser, moisturizer, sunscreen, and serum. Catalogue filters support category, brand, max budget, ingredient, fragrance-free, and sorting; cards show provenance, match explanation fields, and a graceful image placeholder.
- `/routine` is a local-session planner with morning/evening/weekly sections, catalogue alternatives, ingredient/usage details, completion progress/reset, and a weekly journal.
- `/signin` and `/signup` validate input and honestly report that authentication is unavailable. `/profile` is a gated placeholder; no fake credentials or persistence are implemented.
- In-memory image validation and preprocessing; no image persistence
- Pillow-backed decode and minimum 128×128 pixel validation, performed entirely in memory
- Clearly labelled deterministic Phase 1 simulation and ingredient-aware matching
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

## Validation

```powershell
cd frontend
npm run test
npm run build

cd ..\backend
pytest
```

## Data provenance and known issues

The catalogue uses established brands only for high-confidence, broadly published product names/ingredient themes. Entries labelled `AERM sample` are illustrative and must not be interpreted as retailer listings; all catalogue prices and availability are approximate and should be verified before purchase. Product images are intentionally placeholders unless a trusted image URL is configured.

Authentication, profile/history persistence, and account recovery are unavailable until an auth provider, server-side session handling, and a database are configured. Routine state is local to the current browser. Product matching and skin analysis remain deterministic simulation.

## Phase 1 boundary

This is educational software, not a medical diagnostic tool. Phase 2 is intentionally not implemented: no trained inference, authentication, accounts, database/history, payments, clinical claims, or deployment infrastructure.
