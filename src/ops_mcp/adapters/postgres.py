"""Postgres adapter — parameterized queries only, after SQL guard."""

from __future__ import annotations

from typing import Any, Sequence

import psycopg
from psycopg.rows import dict_row
from pydantic import SecretStr

from ops_mcp.security.sql_guard import assert_select_only


class PostgresConfigError(RuntimeError):
    """Raised when the database URL is missing or empty."""


class PostgresClient:
    """Thin sync Postgres client. Never logs or returns the DSN."""

    def __init__(self, database_url: str | SecretStr) -> None:
        if isinstance(database_url, SecretStr):
            dsn = database_url.get_secret_value()
        else:
            dsn = database_url
        if not dsn:
            raise PostgresConfigError(
                "Database URL missing; set OPS_MCP_DATABASE_URL"
            )
        self._dsn = dsn

    def _connect(self) -> psycopg.Connection:
        return psycopg.connect(self._dsn, row_factory=dict_row)

    def query(
        self,
        sql: str,
        params: Sequence[Any] | None = None,
        *,
        max_rows: int = 500,
    ) -> dict[str, Any]:
        """Run a guarded parameterized SELECT and return row dicts."""
        assert_select_only(sql)
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params or ())
                rows = cur.fetchmany(max_rows + 1)
                truncated = len(rows) > max_rows
                rows = rows[:max_rows]
                columns = [col.name for col in cur.description] if cur.description else []
        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "truncated": truncated,
        }

    def explain(
        self,
        sql: str,
        params: Sequence[Any] | None = None,
    ) -> dict[str, Any]:
        """Run EXPLAIN (FORMAT TEXT) for a guarded SELECT (no ANALYZE)."""
        assert_select_only(sql)
        explain_sql = f"EXPLAIN (FORMAT TEXT) {sql}"
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(explain_sql, params or ())
                lines = [row["QUERY PLAN"] for row in cur.fetchall()]
        return {"plan": "\n".join(lines)}

    def scalar(self, sql: str, params: Sequence[Any] | None = None) -> Any:
        """Execute a guarded SELECT and return the first cell (tests/helpers)."""
        assert_select_only(sql)
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params or ())
                row = cur.fetchone()
        if row is None:
            return None
        return next(iter(row.values()))
