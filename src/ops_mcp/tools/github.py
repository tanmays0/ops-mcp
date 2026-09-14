"""GitHub MCP tools."""

from __future__ import annotations

import time
from typing import Any

from pydantic import SecretStr

from ops_mcp.adapters.github import GitHubClient, GitHubConfigError
from ops_mcp.config import Settings, get_settings
from ops_mcp.logging_setup import log_tool_call


def _settings_or_default(settings: Settings | None) -> Settings:
    return settings if settings is not None else get_settings()


def _token(settings: Settings) -> str:
    token = settings.github_token
    if token is None:
        raise GitHubConfigError("GitHub token missing; set OPS_MCP_GITHUB_TOKEN")
    if isinstance(token, SecretStr):
        value = token.get_secret_value()
    else:
        value = str(token)
    if not value:
        raise GitHubConfigError("GitHub token missing; set OPS_MCP_GITHUB_TOKEN")
    return value


def _client(settings: Settings, transport: Any = None) -> GitHubClient:
    return GitHubClient(
        _token(settings),
        api_base=settings.github_api_base,
        rate_per_second=settings.http_rate_per_second,
        timeout=settings.http_timeout_seconds,
        transport=transport,
    )


def github_list_issues(
    owner: str,
    repo: str,
    state: str = "open",
    labels: str | None = None,
    per_page: int = 30,
    *,
    settings: Settings | None = None,
    transport: Any = None,
) -> dict[str, Any]:
    """List issues (and PRs) for a repository filtered by state and labels.

    Args:
        owner: Repository owner.
        repo: Repository name.
        state: ``open``, ``closed``, or ``all``.
        labels: Comma-separated label filter (GitHub API semantics).
        per_page: Page size (max 100 recommended).

    Returns:
        ``{"issues": [{"number","title","state","labels","is_pull_request","html_url"}]}``
    """
    started = time.perf_counter()
    cfg = _settings_or_default(settings)
    try:
        with _client(cfg, transport=transport) as client:
            issues = client.list_issues(
                owner,
                repo,
                state=state,
                labels=labels,
                per_page=per_page,
            )
        result = {"issues": issues}
        log_tool_call(
            "github_list_issues",
            ok=True,
            latency_ms=(time.perf_counter() - started) * 1000,
        )
        return result
    except Exception as exc:
        log_tool_call(
            "github_list_issues",
            ok=False,
            latency_ms=(time.perf_counter() - started) * 1000,
            error=str(exc),
        )
        raise


def github_create_issue(
    owner: str,
    repo: str,
    title: str,
    body: str | None = None,
    labels: list[str] | None = None,
    dry_run: bool = True,
    *,
    settings: Settings | None = None,
    transport: Any = None,
) -> dict[str, Any]:
    """Create a GitHub issue. Defaults to dry-run (no remote write).

    Args:
        owner: Repository owner.
        repo: Repository name.
        title: Issue title.
        body: Optional issue body markdown.
        labels: Optional label names.
        dry_run: When True (default), return the payload that would be created
            without calling the create API. Set ``dry_run=False`` to create.

    Returns:
        Dry-run preview or created issue summary. Never includes tokens.
    """
    started = time.perf_counter()
    cfg = _settings_or_default(settings)
    preview = {
        "owner": owner,
        "repo": repo,
        "title": title,
        "body": body,
        "labels": labels or [],
    }
    try:
        if dry_run:
            result = {"dry_run": True, "would_create": preview}
            log_tool_call(
                "github_create_issue",
                ok=True,
                latency_ms=(time.perf_counter() - started) * 1000,
            )
            return result

        with _client(cfg, transport=transport) as client:
            created = client.create_issue(
                owner,
                repo,
                title=title,
                body=body,
                labels=labels,
            )
        result = {"dry_run": False, "issue": created}
        log_tool_call(
            "github_create_issue",
            ok=True,
            latency_ms=(time.perf_counter() - started) * 1000,
        )
        return result
    except Exception as exc:
        log_tool_call(
            "github_create_issue",
            ok=False,
            latency_ms=(time.perf_counter() - started) * 1000,
            error=str(exc),
        )
        raise


def github_pr_diff_summary(
    owner: str,
    repo: str,
    pull_number: int,
    *,
    settings: Settings | None = None,
    transport: Any = None,
) -> dict[str, Any]:
    """Summarize a pull request's changed files and diff stats (no patches).

    Args:
        owner: Repository owner.
        repo: Repository name.
        pull_number: Pull request number.

    Returns:
        PR metadata plus per-file addition/deletion stats without full contents.
    """
    started = time.perf_counter()
    cfg = _settings_or_default(settings)
    try:
        with _client(cfg, transport=transport) as client:
            summary = client.pr_diff_summary(owner, repo, pull_number)
        log_tool_call(
            "github_pr_diff_summary",
            ok=True,
            latency_ms=(time.perf_counter() - started) * 1000,
        )
        return summary
    except Exception as exc:
        log_tool_call(
            "github_pr_diff_summary",
            ok=False,
            latency_ms=(time.perf_counter() - started) * 1000,
            error=str(exc),
        )
        raise
