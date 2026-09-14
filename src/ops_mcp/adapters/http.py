"""Rate-limited HTTP helpers built on httpx."""

from __future__ import annotations

from typing import Any

import httpx

from ops_mcp.security.rate_limit import TokenBucket


class RateLimitedClient:
    """httpx client wrapper that acquires a token before each request."""

    def __init__(
        self,
        *,
        bucket: TokenBucket,
        timeout: float = 30.0,
        headers: dict[str, str] | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._bucket = bucket
        self._client = httpx.Client(
            timeout=timeout,
            headers=headers or {},
            transport=transport,
        )

    def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        self._bucket.acquire()
        return self._client.request(method, url, **kwargs)

    def get(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("POST", url, **kwargs)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> RateLimitedClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
