"""Simple token-bucket rate limiter for outbound API calls."""

from __future__ import annotations

import threading
import time


class RateLimitExceeded(RuntimeError):
    """Raised when an outbound call would exceed the configured rate."""


class TokenBucket:
    """Thread-safe token bucket.

    Args:
        rate: Tokens added per second.
        capacity: Maximum burst size.
    """

    def __init__(self, rate: float, capacity: float) -> None:
        if rate <= 0 or capacity <= 0:
            raise ValueError("rate and capacity must be positive")
        self._rate = rate
        self._capacity = capacity
        self._tokens = capacity
        self._updated = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._updated
        self._updated = now
        self._tokens = min(self._capacity, self._tokens + elapsed * self._rate)

    def try_acquire(self, tokens: float = 1.0) -> bool:
        """Consume ``tokens`` if available; otherwise return False."""
        with self._lock:
            self._refill()
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False

    def acquire(self, tokens: float = 1.0) -> None:
        """Consume ``tokens`` or raise ``RateLimitExceeded`` (fail closed)."""
        if not self.try_acquire(tokens):
            raise RateLimitExceeded("outbound rate limit exceeded")
