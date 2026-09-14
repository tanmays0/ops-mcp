"""GitHub tool and adapter tests (mocked HTTP; dry-run gate)."""

from __future__ import annotations

import json

import httpx
import pytest
from pydantic import SecretStr

from ops_mcp.adapters.github import GitHubConfigError
from ops_mcp.config import Settings
from ops_mcp.security.rate_limit import RateLimitExceeded, TokenBucket
from ops_mcp.tools.github import (
    github_create_issue,
    github_list_issues,
    github_pr_diff_summary,
)


def _settings(**kwargs: object) -> Settings:
    base = {
        "fs_roots": [],
        "github_token": SecretStr("test-token-not-real"),
        "github_api_base": "https://api.github.com",
        "http_rate_per_second": 100.0,
        "http_timeout_seconds": 5.0,
    }
    base.update(kwargs)
    return Settings(**base)  # type: ignore[arg-type]


def test_token_bucket_fail_closed() -> None:
    bucket = TokenBucket(rate=1.0, capacity=1.0)
    assert bucket.try_acquire() is True
    with pytest.raises(RateLimitExceeded):
        bucket.acquire()


def test_github_create_issue_dry_run_default_no_http() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("dry_run must not call GitHub")

    transport = httpx.MockTransport(handler)
    result = github_create_issue(
        "acme",
        "widgets",
        title="Bug",
        body="details",
        labels=["bug"],
        settings=_settings(),
        transport=transport,
    )
    assert result["dry_run"] is True
    assert result["would_create"]["title"] == "Bug"
    assert "test-token" not in json.dumps(result)


def test_github_create_issue_write_when_dry_run_false() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert "Authorization" in request.headers
        return httpx.Response(
            201,
            json={
                "number": 42,
                "title": "Bug",
                "state": "open",
                "html_url": "https://github.com/acme/widgets/issues/42",
            },
        )

    result = github_create_issue(
        "acme",
        "widgets",
        title="Bug",
        dry_run=False,
        settings=_settings(),
        transport=httpx.MockTransport(handler),
    )
    assert result["dry_run"] is False
    assert result["issue"]["number"] == 42


def test_github_list_issues_maps_fields() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert "labels=backend" in str(request.url)
        return httpx.Response(
            200,
            json=[
                {
                    "number": 7,
                    "title": "API",
                    "state": "open",
                    "labels": [{"name": "backend"}],
                    "html_url": "https://github.com/acme/widgets/issues/7",
                }
            ],
        )

    result = github_list_issues(
        "acme",
        "widgets",
        labels="backend",
        settings=_settings(),
        transport=httpx.MockTransport(handler),
    )
    assert result["issues"][0]["number"] == 7
    assert result["issues"][0]["labels"] == ["backend"]
    assert result["issues"][0]["is_pull_request"] is False


def test_github_pr_diff_summary_omits_patch() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.endswith("/pulls/9"):
            return httpx.Response(
                200,
                json={
                    "number": 9,
                    "title": "Feat",
                    "state": "open",
                    "additions": 10,
                    "deletions": 2,
                    "changed_files": 1,
                },
            )
        if path.endswith("/pulls/9/files"):
            return httpx.Response(
                200,
                json=[
                    {
                        "filename": "a.py",
                        "status": "modified",
                        "additions": 10,
                        "deletions": 2,
                        "changes": 12,
                        "patch": "@@ secret patch should not leak @@",
                    }
                ],
            )
        return httpx.Response(404, json={"message": "not found"})

    result = github_pr_diff_summary(
        "acme",
        "widgets",
        9,
        settings=_settings(),
        transport=httpx.MockTransport(handler),
    )
    dumped = json.dumps(result)
    assert "patch" not in result["files"][0]
    assert "secret patch" not in dumped
    assert result["files"][0]["filename"] == "a.py"


def test_github_missing_token_fails() -> None:
    with pytest.raises(GitHubConfigError):
        github_list_issues(
            "acme",
            "widgets",
            settings=_settings(github_token=None),
        )
