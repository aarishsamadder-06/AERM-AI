# AERM AI deployment

## Architecture

```text
Browser -> Vercel Next.js (/api/* rewrite) -> Render FastAPI -> Supabase PostgreSQL
```

FastAPI remains the authentication authority. Supabase provides PostgreSQL
storage only; Supabase Auth is not used.

## Environment variables

### Local

```text
AERM_ENV=development
AERM_COOKIE_SECURE=false
AERM_COOKIE_SAMESITE=lax
AERM_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
API_BASE_URL=http://localhost:8000
# DATABASE_URL unset: SQLite is used
AERM_DATABASE_PATH=backend/.aerm-data/auth.sqlite3
```

### Production

```text
AERM_ENV=production
DATABASE_URL=postgresql://...
AERM_SESSION_SECRET=<at least 32 random characters>
AERM_COOKIE_SECURE=true
AERM_COOKIE_SAMESITE=lax
AERM_ALLOWED_ORIGINS=https://your-app.vercel.app
API_BASE_URL=https://your-api.onrender.com
```

Production startup fails unless the session secret, HTTPS cookie setting,
explicit CORS origin, and valid cookie policy are configured. `DATABASE_URL`
selects psycopg v3 PostgreSQL; without it, local SQLite remains available.

## Deployment steps

1. Create a Supabase project and copy its PostgreSQL connection string to
   Render's `DATABASE_URL`.
2. Create a Render web service rooted at `backend`, install
   `requirements.txt`, and run `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
3. Set Render's production authentication and CORS variables.
4. Confirm Render `/api/health` and `/docs`.
5. Create a Vercel project rooted at `frontend` and set only the server-side
   `API_BASE_URL` to the Render HTTPS URL.
6. Add the final Vercel domain to Render's `AERM_ALLOWED_ORIGINS`.
7. Test registration, login, logout, CSRF token initialization, and `/api/auth/me`
   through the Vercel domain.

## PostgreSQL integration tests

Unit tests use temporary SQLite databases and never require production credentials.
To run the opt-in PostgreSQL integration test against a dedicated test database,
set `AERM_TEST_DATABASE_URL` and run:

```text
pytest -q tests/test_postgres_integration.py
```

The test creates the schema if needed and removes its uniquely generated test
user afterward. Use a disposable test database, not the production database.

## Database notes

The application creates `users` and `sessions` with PostgreSQL-safe `BIGSERIAL`,
foreign-key cascade, unique email/token hashes, text timestamps, and a session
lookup index. Password hashes remain salted PBKDF2-HMAC-SHA256. Sessions remain
cryptographically random, expire after 14 days, and can be revoked.

There is no automatic SQLite-to-Supabase data migration command. For a fresh
public deployment, let the schema initialize and register new accounts. If
existing local accounts must be retained, perform a separately reviewed,
credential-protected data migration; never commit the SQLite file or database
credentials.

## ML boundary

The optional SCIN checkpoint remains external and must not be added to Git,
Vercel, or the database. It is an image-gradability model only. Cosmetic
findings remain simulated and are not medical predictions.
