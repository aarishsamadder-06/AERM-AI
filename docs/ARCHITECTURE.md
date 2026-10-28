# AERM AI architecture

Phase 1 is a deliberately small, stateless skin-care companion. The browser uploads three facial views, FastAPI validates and preprocesses them in memory, and a deterministic simulator returns a clearly labelled educational result.

```text
Browser (Next.js)
  ├─ / — landing page and Phase 1 scope
  ├─ /analyze — front/left/right cards, previews, replacement, removal, validation
  ├─ /results — simulated finding, observations, recommendations, product matches
  ├─ /routine — static gentle routine guidance
  └─ /products — API-backed product catalogue

FastAPI
  ├─ app/main.py — CORS and application setup
  ├─ app/api/routes.py — multipart validation and API contracts
  ├─ app/schemas.py — Pydantic response/request models
  └─ app/services/predictor.py — in-memory deterministic simulation and ingredient matching
```

## API contract

- `GET /api/health` returns service status, `demo_mode`, and the model identifier `phase1-deterministic-skin-simulator`.
- `POST /api/analyze` accepts multipart fields `front`, `left`, and `right`, plus optional `budget_inr` and `fragrance_free`. Each image must be a non-empty, decodable JPG, PNG, or WEBP under 10 MB and at least 128×128 pixels. Pillow verifies and inspects dimensions in memory; bytes are never persisted. The response includes structured views, detected concerns, matched ingredients, rationale, routine steps, observations, recommendations, and products.
- `GET /api/products` returns sample products with category, INR price, brand, ingredients, source/sample flags, fragrance-free status, availability, concerns, usage, and matching rationale.
- `POST /api/recommendations` accepts concerns plus optional `budget_inr`, `fragrance_free`, and `preferred_ingredients`. It returns filtered products, a routine, matched ingredients, and explanations.

The predictor hashes the three filenames and bytes to choose one stable simulated skin finding. It is not trained ML, medical diagnosis, or clinical advice. Authentication, storage, accounts, treatment claims, and Phase 2 inference are intentionally excluded.
