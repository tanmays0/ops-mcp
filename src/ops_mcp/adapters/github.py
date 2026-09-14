"""GitHub REST API adapter."""

from __future__ import annotations

from typing import Any

import httpx

from ops_mcp.adapters.http import RateLimitedClient
from ops_mcp.security.rate_limit import TokenBucket


class GitHubConfigError(RuntimeError):
    """Raised when GitHub credentials/config are missing."""


class GitHubAPIError(RuntimeError):
    """Raised when the GitHub API returns an error response."""


class GitHubClient:
    """Thin GitHub REST client. Never logs or returns the token."""

    def __init__(
        self,
        token: str,
        *,
        api_base: str = "https://api.github.com",
        rate_per_second: float = 5.0,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if not token:
            raise GitHubConfigError(
                "GitHub token missing; set OPS_MCP_GITHUB_TOKEN"
            )
        self._api_base = api_base.rstrip("/")
        bucket = TokenBucket(rate=rate_per_second, capacity=max(rate_per_second, 1.0))
        self._http = RateLimitedClient(
            bucket=bucket,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "ops-mcp",
            },
            transport=transport,
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> GitHubClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _url(self, path: str) -> str:
        return f"{self._api_base}{path}"

    def _handle(self, response: httpx.Response) -> Any:
        if response.status_code >= 400:
            # Do not include response headers (may echo auth); keep body short.
            detail = response.text[:300]
            raise GitHubAPIError(
                f"GitHub API error {response.status_code}: {detail}"
            )
        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    def list_issues(
        self,
        owner: str,
        repo: str,
        *,
        state: str = "open",
        labels: str | None = None,
        per_page: int = 30,
    ) -> list[dict[str, Any]]:
        params: dict[str, str | int] = {
            "state": state,
            "per_page": per_page,
        }
        if labels:
            params["labels"] = labels
        response = self._http.get(
            self._url(f"/repos/{owner}/{repo}/issues"),
            params=params,
        )
        payload = self._handle(response)
        assert isinstance(payload, list)
        # GitHub includes PRs in /issues; keep them but mark pull_request.
        return [
            {
                "number": item["number"],
                "title": item["title"],
                "state": item["state"],
                "labels": [label["name"] for label in item.get("labels", [])],
                "is_pull_request": "pull_request" in item,
                "html_url": item.get("html_url"),
            }
            for item in payload
        ]

    def create_issue(
        self,
        owner: str,
        repo: str,
        *,
        title: str,
        body: str | None = None,
        labels: list[str] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"title": title}
        if body is not None:
            payload["body"] = body
        if labels:
            payload["labels"] = labels
        response = self._http.post(
            self._url(f"/repos/{owner}/{repo}/issues"),
            json=payload,
        )
        data = self._handle(response)
        assert isinstance(data, dict)
        return {
            "number": data["number"],
            "title": data["title"],
            "state": data["state"],
            "html_url": data.get("html_url"),
        }

    def pr_diff_summary(
        self,
        owner: str,
        repo: str,
        pull_number: int,
    ) -> dict[str, Any]:
        pr_resp = self._http.get(
            self._url(f"/repos/{owner}/{repo}/pulls/{pull_number}")
        )
        pr = self._handle(pr_resp)
        assert isinstance(pr, dict)

        files_resp = self._http.get(
            self._url(f"/repos/{owner}/{repo}/pulls/{pull_number}/files"),
            params={"per_page": 100},
        )
        files = self._handle(files_resp)
        assert isinstance(files, list)

        file_summaries = [
            {
                "filename": item.get("filename"),
                "status": item.get("status"),
                "additions": item.get("additions"),
                "deletions": item.get("deletions"),
                "changes": item.get("changes"),
                # Intentionally omit patch / full contents.
            }
            for item in files
        ]
        return {
            "number": pr.get("number"),
            "title": pr.get("title"),
            "state": pr.get("state"),
            "additions": pr.get("additions"),
            "deletions": pr.get("deletions"),
            "changed_files": pr.get("changed_files"),
            "files": file_summaries,
        }

    def latest_workflow_run(
        self,
        owner: str,
        repo: str,
        *,
        branch: str = "main",
    ) -> dict[str, Any] | None:
        """Return the latest Actions workflow run for ``branch``, or None."""
        response = self._http.get(
            self._url(f"/repos/{owner}/{repo}/actions/runs"),
            params={"branch": branch, "per_page": 1},
        )
        payload = self._handle(response)
        assert isinstance(payload, dict)
        runs = payload.get("workflow_runs") or []
        if not runs:
            return None
        run = runs[0]
        return {
            "id": run.get("id"),
            "name": run.get("name"),
            "status": run.get("status"),
            "conclusion": run.get("conclusion"),
            "event": run.get("event"),
            "head_branch": run.get("head_branch"),
            "html_url": run.get("html_url"),
            "created_at": run.get("created_at"),
            "updated_at": run.get("updated_at"),
        }
