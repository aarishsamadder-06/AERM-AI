import os
import secrets
from functools import lru_cache

LOCAL_ORIGINS = ("http://localhost:3000", "http://127.0.0.1:3000")
VALID_SAMESITE = {"lax", "strict", "none"}


def is_production() -> bool:
    return os.getenv("AERM_ENV", "development").strip().lower() in {"production", "prod"}


@lru_cache(maxsize=1)
def session_secret() -> str:
    configured = os.getenv("AERM_SESSION_SECRET", "").strip()
    if is_production():
        if len(configured) < 32:
            raise RuntimeError(
                "AERM_SESSION_SECRET must be set to at least 32 characters in production."
            )
        return configured
    return configured or secrets.token_urlsafe(32)


def cookie_secure() -> bool:
    configured = os.getenv("AERM_COOKIE_SECURE")
    if is_production():
        if configured is None or configured.strip().lower() != "true":
            raise RuntimeError("AERM_COOKIE_SECURE=true is required in production.")
        return True
    return configured is not None and configured.strip().lower() == "true"


def cookie_samesite() -> str:
    value = os.getenv("AERM_COOKIE_SAMESITE", "lax").strip().lower()
    if value not in VALID_SAMESITE:
        raise RuntimeError(
            "AERM_COOKIE_SAMESITE must be one of: lax, strict, none."
        )
    if value == "none" and not cookie_secure():
        raise RuntimeError("AERM_COOKIE_SAMESITE=none requires AERM_COOKIE_SECURE=true.")
    return value


def allowed_origins() -> list[str]:
    configured = os.getenv("AERM_ALLOWED_ORIGINS", "")
    values = [item.strip().rstrip("/") for item in configured.split(",") if item.strip()]
    if is_production() and not values:
        raise RuntimeError(
            "AERM_ALLOWED_ORIGINS must explicitly list the production frontend origin."
        )
    origins = values or list(LOCAL_ORIGINS)
    if "*" in origins:
        raise RuntimeError(
            "AERM_ALLOWED_ORIGINS cannot contain '*' when credentialed CORS is enabled."
        )
    return origins


def validate_startup_configuration() -> None:
    session_secret()
    cookie_secure()
    cookie_samesite()
    allowed_origins()
