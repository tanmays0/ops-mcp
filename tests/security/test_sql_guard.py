"""Fail-closed SELECT-only SQL guard tests."""

from __future__ import annotations

import pytest

from ops_mcp.security.sql_guard import SqlGuardError, assert_select_only


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT 1",
        "SELECT id FROM users WHERE email = %s",
        "WITH c AS (SELECT 1) SELECT * FROM c",
        "-- DROP\nSELECT 1",
    ],
)
def test_sql_guard_allows_selects(sql: str) -> None:
    assert_select_only(sql)


@pytest.mark.parametrize(
    "sql",
    [
        "DROP TABLE users",
        "INSERT INTO users(email) VALUES ('x')",
        "UPDATE users SET email='x'",
        "DELETE FROM users",
        "SELECT 1; DROP TABLE users",
        "/* SELECT 1 */ DROP TABLE users",
        "SELECT 1; SELECT 2",
        "   ",
        "",
        "SELECT * INTO tmp FROM users",
        "COPY users TO STDOUT",
        "EXPLAIN SELECT 1",
    ],
)
def test_sql_guard_rejects_unsafe(sql: str) -> None:
    with pytest.raises(SqlGuardError):
        assert_select_only(sql)
