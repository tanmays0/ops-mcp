"""FastMCP stdio server for OpsMCP."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, Sequence, TypedDict

from fastmcp import FastMCP

from ops_mcp.config import Settings, get_settings
from ops_mcp.logging_setup import configure_logging
from ops_mcp.security.path_sandbox import validate_roots
from ops_mcp.tools import deploy as deploy_tools
from ops_mcp.tools import fs as fs_tools
from ops_mcp.tools import github as github_tools
from ops_mcp.tools import postgres as postgres_tools


class AppState(TypedDict):
    settings: Settings


@asynccontextmanager
async def lifespan(server: FastMCP[AppState]) -> AsyncIterator[AppState]:
    """Load settings, validate FS roots, configure logging."""
    get_settings.cache_clear()
    settings = get_settings()
    configure_logging(settings.log_level)
    validate_roots(settings.fs_roots)
    yield {"settings": settings}


mcp = FastMCP("ops-mcp", lifespan=lifespan)


@mcp.tool
def fs_search(
    query: str,
    root: str | None = None,
    max_results: int = 50,
) -> dict[str, Any]:
    """Search allowlisted filesystem roots for a literal substring.

    Returns matches only under ``OPS_MCP_FS_ROOTS``. Paths that escape the
    sandbox (including via ``..`` or symlinks) are rejected.
    """
    return fs_tools.fs_search(query=query, root=root, max_results=max_results)


@mcp.tool
def fs_read_file(
    path: str,
    max_bytes: int | None = None,
) -> dict[str, Any]:
    """Read a file under allowlisted roots with a hard size limit.

    Symlink and ``..`` escapes fail closed. Content is UTF-8 decoded with
    replacement characters; ``truncated`` is true when the file exceeded the cap.
    """
    return fs_tools.fs_read_file(path=path, max_bytes=max_bytes)


@mcp.tool
def github_list_issues(
    owner: str,
    repo: str,
    state: str = "open",
    labels: str | None = None,
    per_page: int = 30,
) -> dict[str, Any]:
    """List GitHub issues/PRs for a repo by state and labels.

    Requires ``OPS_MCP_GITHUB_TOKEN``. Returns number, title, state, labels.
    """
    return github_tools.github_list_issues(
        owner=owner,
        repo=repo,
        state=state,
        labels=labels,
        per_page=per_page,
    )


@mcp.tool
def github_create_issue(
    owner: str,
    repo: str,
    title: str,
    body: str | None = None,
    labels: list[str] | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Create a GitHub issue. Defaults to dry_run=True (no remote write).

    Set ``dry_run=False`` only when the user explicitly confirms creation.
    Never returns credentials.
    """
    return github_tools.github_create_issue(
        owner=owner,
        repo=repo,
        title=title,
        body=body,
        labels=labels,
        dry_run=dry_run,
    )


@mcp.tool
def github_pr_diff_summary(
    owner: str,
    repo: str,
    pull_number: int,
) -> dict[str, Any]:
    """Summarize a PR's changed files and diff stats without full patches."""
    return github_tools.github_pr_diff_summary(
        owner=owner,
        repo=repo,
        pull_number=pull_number,
    )


@mcp.tool
def postgres_query_readonly(
    sql: str,
    params: Sequence[Any] | None = None,
    max_rows: int | None = None,
) -> dict[str, Any]:
    """Run a parameterized SELECT against Postgres (DDL/DML rejected first).

    Requires ``OPS_MCP_DATABASE_URL``. Multi-statement and write SQL fail closed
    before any connection is opened.
    """
    return postgres_tools.postgres_query_readonly(
        sql=sql,
        params=params,
        max_rows=max_rows,
    )


@mcp.tool
def postgres_explain(
    sql: str,
    params: Sequence[Any] | None = None,
) -> dict[str, Any]:
    """EXPLAIN (FORMAT TEXT) a SELECT without ANALYZE / executing side effects."""
    return postgres_tools.postgres_explain(sql=sql, params=params)


@mcp.tool
def deploy_status(
    owner: str,
    repo: str,
    branch: str = "main",
) -> dict[str, Any]:
    """Latest GitHub Actions workflow run for a branch (read-only)."""
    return deploy_tools.deploy_status(owner=owner, repo=repo, branch=branch)


def main() -> None:
    """Run the MCP server over stdio (Cursor default)."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
