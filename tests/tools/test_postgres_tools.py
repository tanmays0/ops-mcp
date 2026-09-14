"""Postgres tool tests — SQL guard before connect + live Compose DB."""

from __future__ import annotations

import json
import os

import pytest
from pydantic import SecretStr

from ops_mcp.adapters.postgres import PostgresClient, PostgresConfigError
from ops_mcp.config import Settings
from ops_mcp.security.sql_guard import SqlGuardError
from ops_mcp.tools.postgres import postgres_explain, postgres_query_readonly

DSN = os.environ.get(
    "OPS_MCP_DATABASE_URL",
    "postgresql://opsmcp:opsmcp@localhost:5432/opsmcp",
)


def _pg_settings(**kwargs: object) -> Settings:
    base: dict[str, object] = {
        "fs_roots": [],
        "database_url": SecretStr(DSN),
        "postgres_max_rows": 500,
    }
    base.update(kwargs)
    return Settings(**base)  # type: ignore[arg-type]


def _db_available() -> bool:
    try:
        client = PostgresClient(DSN)
        client.scalar("SELECT 1")
        return True
    except Exception:
        return False


requires_postgres = pytest.mark.skipif(
    not _db_available(),
    reason="Postgres not reachable on OPS_MCP_DATABASE_URL",
)


def test_drop_rejected_before_connect(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(self: PostgresClient) -> object:
        raise AssertionError("must not connect on unsafe SQL")

    monkeypatch.setattr(PostgresClient, "_connect", boom)
    with pytest.raises(SqlGuardError):
        postgres_query_readonly("DROP TABLE users", settings=_pg_settings())


def test_stacked_rejected_via_tool() -> None:
    with pytest.raises(SqlGuardError):
        postgres_query_readonly(
            "SELECT 1; DROP TABLE users",
            settings=_pg_settings(),
        )


def test_missing_dsn_config_error() -> None:
    with pytest.raises(PostgresConfigError):
        postgres_query_readonly(
            "SELECT 1",
            settings=_pg_settings(database_url=None),
        )


@pytest.mark.postgres
@requires_postgres
def test_select_users_seed() -> None:
    result = postgres_query_readonly(
        "SELECT email FROM users ORDER BY id",
        settings=_pg_settings(),
    )
    assert result["row_count"] >= 1
    assert "email" in result["columns"]
    emails = [row["email"] for row in result["rows"]]
    assert "alice@example.com" in emails


@pytest.mark.postgres
@requires_postgres
def test_parameterized_select() -> None:
    result = postgres_query_readonly(
        "SELECT email FROM users WHERE id = %s",
        params=(1,),
        settings=_pg_settings(),
    )
    assert result["row_count"] == 1
    assert result["rows"][0]["email"]


@pytest.mark.postgres
@requires_postgres
def test_explain_does_not_change_row_count() -> None:
    client = PostgresClient(DSN)
    before = client.scalar("SELECT COUNT(*) FROM orders")
    plan = postgres_explain(
        "SELECT * FROM orders WHERE status = %s",
        params=("paid",),
        settings=_pg_settings(),
    )
    after = client.scalar("SELECT COUNT(*) FROM orders")
    assert before == after
    assert plan["plan"]
    assert "orders" in plan["plan"].lower() or "seq" in plan["plan"].lower() or "scan" in plan["plan"].lower()


@pytest.mark.postgres
@requires_postgres
def test_response_omits_dsn_password() -> None:
    result = postgres_query_readonly("SELECT 1 AS n", settings=_pg_settings())
    dumped = json.dumps(result)
    assert "opsmcp:opsmcp" not in dumped
    assert "@localhost" not in dumped
