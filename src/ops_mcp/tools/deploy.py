"""Deploy / CI status tools (GitHub Actions)."""

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


def deploy_status(
    owner: str,
    repo: str,
    branch: str = "main",
    *,
    settings: Settings | None = None,
    transport: Any = None,
) -> dict[str, Any]:
    """Return the latest GitHub Actions workflow run for a branch (read-only).

    Args:
        owner: Repository owner.
        repo: Repository name.
        branch: Branch to inspect (default ``main``).

    Returns:
        ``{branch, run: null | {id, name, status, conclusion, html_url, ...}}``
    """
    started = time.perf_counter()
    cfg = _settings_or_default(settings)
    try:
        with GitHubClient(
            _token(cfg),
            api_base=cfg.github_api_base,
            rate_per_second=cfg.http_rate_per_second,
            timeout=cfg.http_timeout_seconds,
            transport=transport,
        ) as client:
            run = client.latest_workflow_run(owner, repo, branch=branch)
        result = {"branch": branch, "run": run}
        log_tool_call(
            "deploy_status",
            ok=True,
            latency_ms=(time.perf_counter() - started) * 1000,
        )
        return result
    except Exception as exc:
        log_tool_call(
            "deploy_status",
            ok=False,
            latency_ms=(time.perf_counter() - started) * 1000,
            error=str(exc),
        )
        raise
