"""deploy_status tests (mocked GitHub Actions API)."""

from __future__ import annotations

import json

import httpx
import pytest
from pydantic import SecretStr

from ops_mcp.adapters.github import GitHubConfigError
from ops_mcp.config import Settings
from ops_mcp.tools.deploy import deploy_status


def _settings(**kwargs: object) -> Settings:
    base: dict[str, object] = {
        "fs_roots": [],
        "github_token": SecretStr("test-token-not-real"),
        "github_api_base": "https://api.github.com",
        "http_rate_per_second": 100.0,
    }
    base.update(kwargs)
    return Settings(**base)  # type: ignore[arg-type]


def test_deploy_status_maps_latest_run() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert "actions/runs" in str(request.url)
        assert "branch=main" in str(request.url)
        return httpx.Response(
            200,
            json={
                "workflow_runs": [
                    {
                        "id": 99,
                        "name": "CI",
                        "status": "completed",
                        "conclusion": "success",
                        "event": "push",
                        "head_branch": "main",
                        "html_url": "https://github.com/acme/widgets/actions/runs/99",
                        "created_at": "2026-09-12T00:00:00Z",
                        "updated_at": "2026-09-12T00:01:00Z",
                    }
                ]
            },
        )

    result = deploy_status(
        "acme",
        "widgets",
        settings=_settings(),
        transport=httpx.MockTransport(handler),
    )
    assert result["branch"] == "main"
    assert result["run"]["conclusion"] == "success"
    assert "test-token" not in json.dumps(result)


def test_deploy_status_empty_runs() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"workflow_runs": []})

    result = deploy_status(
        "acme",
        "widgets",
        branch="develop",
        settings=_settings(),
        transport=httpx.MockTransport(handler),
    )
    assert result["branch"] == "develop"
    assert result["run"] is None


def test_deploy_status_missing_token() -> None:
    with pytest.raises(GitHubConfigError):
        deploy_status("acme", "widgets", settings=_settings(github_token=None))
