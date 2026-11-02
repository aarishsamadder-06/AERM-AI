import hashlib
import hmac
import os
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from ..config import session_secret

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:  # pragma: no cover - exercised when local SQLite is used
    psycopg = None
    dict_row = None

PG_UNIQUE_VIOLATION = psycopg.errors.UniqueViolation if psycopg else type(
    "PGUniqueViolation", (Exception,), {}
)

SESSION_COOKIE = "aerm_session"
SESSION_DAYS = 14
PBKDF2_ITERATIONS = 310_000


class UserAlreadyExistsError(Exception):
    """Raised when a normalized email is already registered."""


def database_backend() -> str:
    return "postgresql" if os.getenv("DATABASE_URL") else "sqlite"


def _database_path() -> Path:
    configured = os.getenv("AERM_DATABASE_PATH")
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parents[2] / ".aerm-data" / "auth.sqlite3"


def _connect():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        if psycopg is None:
            raise RuntimeError("psycopg is required when DATABASE_URL is configured.")
        return psycopg.connect(database_url, row_factory=dict_row)
    path = _database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    if database_backend() == "postgresql":
        with _connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id BIGSERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id BIGSERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    token_hash TEXT NOT NULL UNIQUE,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    revoked_at TEXT
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_sessions_token_hash ON sessions(token_hash)"
            )
        return
    with _connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                token_hash TEXT NOT NULL UNIQUE,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                revoked_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_sessions_token_hash ON sessions(token_hash);
            """
        )


def normalize_email(email: str) -> str:
    return email.strip().lower()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _encode_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def _verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt_hex, digest_hex = encoded.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt_hex), int(iterations)
        )
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def _token_hash(token: str) -> str:
    return hmac.new(session_secret().encode(), token.encode(), hashlib.sha256).hexdigest()


def create_user(name: str, email: str, password: str) -> dict:
    initialize_database()
    now = _now().isoformat()
    values = (name.strip(), normalize_email(email), _encode_password(password), now, now)
    try:
        with _connect() as connection:
            if database_backend() == "postgresql":
                row = connection.execute(
                    "INSERT INTO users (name, email, password_hash, created_at, updated_at) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                    values,
                ).fetchone()
                user_id = row["id"]
            else:
                cursor = connection.execute(
                    "INSERT INTO users (name, email, password_hash, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    values,
                )
                user_id = cursor.lastrowid
    except sqlite3.IntegrityError as exc:
        raise UserAlreadyExistsError from exc
    except PG_UNIQUE_VIOLATION as exc:
        raise UserAlreadyExistsError from exc
    return {"id": user_id, "name": name.strip(), "email": normalize_email(email)}


def authenticate_user(email: str, password: str) -> dict | None:
    initialize_database()
    with _connect() as connection:
        if database_backend() == "postgresql":
            row = connection.execute(
                "SELECT id, name, email, password_hash, is_active FROM users WHERE email = %s",
                (normalize_email(email),),
            ).fetchone()
        else:
            row = connection.execute(
                "SELECT id, name, email, password_hash, is_active FROM users WHERE email = ?",
                (normalize_email(email),),
            ).fetchone()
    if not row or not row["is_active"] or not _verify_password(password, row["password_hash"]):
        return None
    return {"id": row["id"], "name": row["name"], "email": row["email"]}


def create_session(user_id: int) -> tuple[str, datetime]:
    initialize_database()
    token = secrets.token_urlsafe(32)
    now = _now()
    expires = now + timedelta(days=SESSION_DAYS)
    with _connect() as connection:
        if database_backend() == "postgresql":
            connection.execute(
                "INSERT INTO sessions (user_id, token_hash, expires_at, created_at) VALUES (%s, %s, %s, %s)",
                (user_id, _token_hash(token), expires.isoformat(), now.isoformat()),
            )
        else:
            connection.execute(
                "INSERT INTO sessions (user_id, token_hash, expires_at, created_at) VALUES (?, ?, ?, ?)",
                (user_id, _token_hash(token), expires.isoformat(), now.isoformat()),
            )
    return token, expires


def get_user_for_session(token: str | None) -> dict | None:
    if not token:
        return None
    initialize_database()
    with _connect() as connection:
        placeholder = "%s" if database_backend() == "postgresql" else "?"
        active = "TRUE" if database_backend() == "postgresql" else "1"
        row = connection.execute(
            f"""
            SELECT users.id, users.name, users.email, sessions.expires_at
            FROM sessions JOIN users ON users.id = sessions.user_id
            WHERE sessions.token_hash = {placeholder}
              AND sessions.revoked_at IS NULL
              AND users.is_active = {active}
            """,
            (_token_hash(token),),
        ).fetchone()
    if not row:
        return None
    try:
        if datetime.fromisoformat(row["expires_at"]) <= _now():
            return None
    except ValueError:
        return None
    return {"id": row["id"], "name": row["name"], "email": row["email"]}


def revoke_session(token: str | None) -> None:
    if not token:
        return
    initialize_database()
    with _connect() as connection:
        placeholder = "%s" if database_backend() == "postgresql" else "?"
        connection.execute(
            f"UPDATE sessions SET revoked_at = {placeholder} WHERE token_hash = {placeholder} AND revoked_at IS NULL",
            (_now().isoformat(), _token_hash(token)),
        )
