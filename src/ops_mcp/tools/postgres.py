"""Postgres MCP tools — SELECT-only + EXPLAIN."""

from __future__ import annotations

import time
from typing import Any, Sequence

from pydantic import SecretStr

from ops_mcp.adapters.postgres import PostgresClient, PostgresConfigError
from ops_mcp.config import Settings, get_settings
from ops_mcp.logging_setup import log_tool_call
from ops_mcp.security.sql_guard import SqlGuardError, assert_select_only


def _settings_or_default(settings: Settings | None) -> Settings:
    return settings if settings is not None else get_settings()


def _dsn(settings: Settings) -> SecretStr:
    url = settings.database_url
    if url is None or not url.get_secret_value():
        raise PostgresConfigError(
            "Database URL missing; set OPS_MCP_DATABASE_URL"
        )
    return url


def postgres_query_readonly(
    sql: str,
    params: Sequence[Any] | None = None,
    max_rows: int | None = None,
    *,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Execute a parameterized SELECT against Postgres.

    DDL/DML and multi-statement SQL are rejected by the SQL guard before any
    database connection is opened. Never pass secrets in ``sql``; use ``params``.
    """
    started = time.perf_counter()
    cfg = _settings_or_default(settings)
    try:
        assert_select_only(sql)
        client = PostgresClient(_dsn(cfg))
        limit = max_rows if max_rows is not None else cfg.postgres_max_rows
        result = client.query(sql, params, max_rows=limit)
        log_tool_call(
            "postgres_query_readonly",
            ok=True,
            latency_ms=(time.perf_counter() - started) * 1000,
        )
        return result
    except Exception as exc:
        log_tool_call(
            "postgres_query_readonly",
            ok=False,
            latency_ms=(time.perf_counter() - started) * 1000,
            error=str(exc),
        )
        raise


def postgres_explain(
    sql: str,
    params: Sequence[Any] | None = None,
    *,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Return EXPLAIN (FORMAT TEXT) for a SELECT without ANALYZE / execution.

    Uses the same SELECT-only gate as ``postgres_query_readonly``.
    """
    started = time.perf_counter()
    cfg = _settings_or_default(settings)
    try:
        assert_select_only(sql)
        client = PostgresClient(_dsn(cfg))
        result = client.explain(sql, params)
        log_tool_call(
            "postgres_explain",
            ok=True,
            latency_ms=(time.perf_counter() - started) * 1000,
        )
        return result
    except Exception as exc:
        log_tool_call(
            "postgres_explain",
            ok=False,
            latency_ms=(time.perf_counter() - started) * 1000,
            error=str(exc),
        )
        raise


__all__ = [
    "SqlGuardError",
    "postgres_explain",
    "postgres_query_readonly",
]
