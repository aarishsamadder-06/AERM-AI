import os
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import pytest
from fastapi.testclient import TestClient

psycopg = pytest.importorskip("psycopg")
from psycopg import sql
from psycopg.rows import dict_row

from app.services.auth import _token_hash, initialize_database


def _isolated_database_url(database_url: str, schema: str) -> str:
    parts = urlsplit(database_url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["options"] = f"-c search_path={schema}"
    return urlunsplit(parts._replace(query=urlencode(query)))


@pytest.fixture
def postgres_client(monkeypatch):
    base_database_url = os.getenv("AERM_TEST_DATABASE_URL")
    if not base_database_url:
        pytest.skip("Set AERM_TEST_DATABASE_URL to run PostgreSQL integration tests.")

    schema = f"aerm_test_{uuid.uuid4().hex}"
    isolated_database_url = _isolated_database_url(base_database_url, schema)
    with psycopg.connect(base_database_url) as connection:
        connection.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))

    monkeypatch.setenv("DATABASE_URL", isolated_database_url)
    monkeypatch.delenv("AERM_DATABASE_PATH", raising=False)
    email = f"postgres-{uuid.uuid4().hex}@example.com"
    try:
        from app.main import app

        initialize_database()
        with TestClient(app) as client:
            yield client, isolated_database_url, email, schema
    finally:
        with psycopg.connect(base_database_url) as connection:
            connection.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema))
            )


def _csrf(client: TestClient) -> str:
    return client.get("/api/auth/csrf").json()["csrf_token"]


def test_postgres_schema_and_auth_lifecycle(postgres_client):
    client, database_url, email, schema = postgres_client

    with psycopg.connect(database_url, row_factory=dict_row) as connection:
        columns = {
            row["column_name"]: row["data_type"]
            for row in connection.execute(
                """
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = %s
                  AND table_name IN ('users', 'sessions')
                """,
                (schema,),
            ).fetchall()
        }
    assert columns["id"] == "bigint"
    assert columns["user_id"] == "bigint"
    assert columns["is_active"] == "boolean"

    csrf = _csrf(client)
    registered = client.post(
        "/api/auth/register",
        json={"name": "Postgres User", "email": email, "password": "secure-pass-123"},
        headers={"X-CSRF-Token": csrf},
    )
    assert registered.status_code == 201
    assert client.get("/api/auth/me").status_code == 200

    session_token = registered.cookies["aerm_session"]
    with psycopg.connect(database_url, row_factory=dict_row) as connection:
        connection.execute(
            "UPDATE sessions SET expires_at = %s WHERE token_hash = %s",
            (
                (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(),
                _token_hash(session_token),
            ),
        )
    assert client.get("/api/auth/me").status_code == 401

    login_csrf = _csrf(client)
    logged_in = client.post(
        "/api/auth/login",
        json={"email": email, "password": "secure-pass-123"},
        headers={"X-CSRF-Token": login_csrf},
    )
    assert logged_in.status_code == 200
    login_token = logged_in.cookies["aerm_session"]

    assert client.post("/api/auth/logout").status_code == 403
    logout_csrf = client.cookies["aerm_csrf"]
    assert client.post(
        "/api/auth/logout",
        headers={"X-CSRF-Token": logout_csrf},
    ).status_code == 204
    assert client.get("/api/auth/me").status_code == 401

    with psycopg.connect(database_url, row_factory=dict_row) as connection:
        revoked = connection.execute(
            "SELECT revoked_at FROM sessions WHERE token_hash = %s",
            (_token_hash(login_token),),
        ).fetchone()
    assert revoked is not None
    assert revoked["revoked_at"] is not None
