"""SELECT-only SQL allowlist using sqlglot AST parsing.

Fail closed before any database connection. Multi-statement SQL,
DDL/DML, COPY, SELECT INTO, and EXPLAIN (handled by a separate tool)
are rejected.
"""

from __future__ import annotations

import sqlglot
from sqlglot import exp


class SqlGuardError(ValueError):
    """Raised when SQL is not a single allowlisted SELECT."""


_FORBIDDEN: tuple[type[exp.Expression], ...] = (
    exp.Drop,
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Create,
    exp.Alter,
    exp.TruncateTable,
    exp.Copy,
    exp.Command,
    exp.Grant,
    exp.Revoke,
    exp.Merge,
    exp.Replace,
    exp.Set,
    exp.Use,
    exp.Transaction,
    exp.Commit,
    exp.Rollback,
)


def assert_select_only(sql: str) -> None:
    """Validate ``sql`` is a single SELECT (or WITH…SELECT) with no writes.

    Raises:
        SqlGuardError: On empty input, parse failure, multi-statement,
            non-SELECT roots, SELECT INTO, or forbidden nodes in the tree.
    """
    if sql is None or not str(sql).strip():
        raise SqlGuardError("SQL rejected: empty statement")

    try:
        statements = sqlglot.parse(str(sql), read="postgres")
    except sqlglot.errors.ParseError as exc:
        raise SqlGuardError("SQL rejected: parse error") from exc

    statements = [stmt for stmt in statements if stmt is not None]
    if not statements:
        raise SqlGuardError("SQL rejected: empty statement")
    if len(statements) != 1:
        raise SqlGuardError("SQL rejected: multiple statements")

    root = statements[0]
    if not isinstance(root, exp.Select):
        raise SqlGuardError("SQL rejected: not a SELECT")

    if root.args.get("into") is not None:
        raise SqlGuardError("SQL rejected: SELECT INTO not allowed")

    for node in root.walk():
        if isinstance(node, _FORBIDDEN):
            raise SqlGuardError("SQL rejected: forbidden statement type")
