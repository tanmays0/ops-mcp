"""Secret redaction for logs and tool responses."""

from __future__ import annotations

import re
from typing import Any

# GitHub PATs, Bearer headers, and common env-style assignments.
_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"(?i)Bearer\s+[A-Za-z0-9\-._~+/]+=*"),
    re.compile(
        r"(?i)(api[_-]?key|token|secret|password|authorization)"
        r"\s*[=:]\s*['\"]?([^\s'\"]+)"
    ),
)

_REDACTED = "[REDACTED]"


def redact(value: str) -> str:
    """Return ``value`` with known secret patterns replaced."""
    redacted = value
    for pattern in _PATTERNS:
        if pattern.groups:
            redacted = pattern.sub(
                lambda match: f"{match.group(1)}={_REDACTED}",
                redacted,
            )
        else:
            redacted = pattern.sub(_REDACTED, redacted)
    return redacted


def redact_obj(obj: Any) -> Any:
    """Recursively redact strings inside dicts/lists."""
    if isinstance(obj, str):
        return redact(obj)
    if isinstance(obj, dict):
        return {key: redact_obj(val) for key, val in obj.items()}
    if isinstance(obj, list):
        return [redact_obj(item) for item in obj]
    return obj
