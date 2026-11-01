# AERM AI architecture

The application is a deliberately small, stateless skin-care companion. The browser uploads three facial views, FastAPI validates and preprocesses them in memory, and a deterministic simulator returns a clearly labelled educational result. When configured, a separate SCIN RBF SVM assesses image gradability only.

```text
Browser (Next.js)
  ├─ / — landing page and Phase 1 scope
  ├─ /analyze — front/left/right cards, previews, replacement, removal, validation
  ├─ /results — simulated finding, separate optional image-quality statuses, observations, recommendations, product matches
  ├─ /routine — static gentle routine guidance
  └─ /products — API-backed product catalogue

FastAPI
  ├─ app/main.py — CORS and application setup
  ├─ app/api/routes.py — multipart validation and API contracts
  ├─ app/schemas.py — Pydantic response/request models
  ├─ app/services/predictor.py — in-memory deterministic simulation and ingredient matching
  └─ app/services/quality_gate.py — optional external SCIN checkpoint adapter
  └─ app/services/auth.py — SQLite users and server-side session cookies
```

## API contract

- `GET /api/health` returns service status, `demo_mode`, the model identifier `phase1-deterministic-skin-simulator`, and `image_quality_gate_configured`.
- `POST /api/analyze` accepts multipart fields `front`, `left`, and `right`, plus optional `budget_inr` and `fragrance_free`. Each image must be a non-empty, decodable JPG, PNG, or WEBP under 10 MB and at least 128×128 pixels. Pillow verifies and inspects dimensions in memory; bytes are never persisted. The response includes structured views, detected concerns, matched ingredients, rationale, routine steps, observations, recommendations, products, and optional `image_quality`.
- When `AERM_QUALITY_MODEL_PATH` points to the trusted external checkpoint, `image_quality.views` contains one `quality_sufficient` or `insufficient` result per view plus a raw, uncalibrated SVM `decision_score`. An unset variable returns `image_quality: null`; an invalid configured checkpoint returns HTTP 503.
- `GET /api/products` returns sample products with category, INR price, brand, ingredients, source/sample flags, fragrance-free status, availability, concerns, usage, and matching rationale.
- `POST /api/recommendations` accepts concerns plus optional `budget_inr`, `fragrance_free`, and `preferred_ingredients`. It returns filtered products, a routine, matched ingredients, and explanations.
- `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`, and `POST /api/auth/logout` provide local development authentication using PBKDF2 password hashes and HTTP-only session cookies. The SQLite database is external to Git by default.

The predictor hashes the three filenames and bytes to choose one stable simulated skin finding. It is not trained ML, medical diagnosis, or clinical advice. The separate SCIN quality gate is not a skin-condition predictor. Email verification, password recovery, account history, treatment claims, and cosmetic trained inference remain excluded.

## Model selection boundary

The verified quality-gate checkpoint is the external Day 6 RBF SVM selected from
the four reproducible traditional candidates by validation macro F1. The current
environment does not include PyTorch, torchvision, or Transformers, and no
verified deep-learning checkpoints were available, so no deep-learning candidate
was integrated or represented as superior. The checkpoint remains outside Git;
the quality-gate API contract and per-view response are unchanged.
