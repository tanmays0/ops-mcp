"""Structured logging with secret redaction."""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from ops_mcp.security.secrets import redact, redact_obj


class RedactingFilter(logging.Filter):
    """Ensure log messages never contain raw tokens."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = redact(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = redact_obj(record.args)
            elif isinstance(record.args, tuple):
                record.args = tuple(redact_obj(arg) for arg in record.args)
        return True


class JsonFormatter(logging.Formatter):
    """Emit one JSON object per log line."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for key in ("tool", "ok", "latency_ms", "error"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(redact_obj(payload), default=str)


def configure_logging(level: str = "INFO") -> None:
    """Configure root logging once for the server process."""
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level.upper())

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RedactingFilter())
    root.addHandler(handler)


def log_tool_call(
    tool: str,
    *,
    ok: bool,
    latency_ms: float,
    error: str | None = None,
) -> None:
    """Emit a structured tool-call log line."""
    logger = logging.getLogger("ops_mcp.tools")
    extra = {
        "tool": tool,
        "ok": ok,
        "latency_ms": round(latency_ms, 3),
        "error": redact(error) if error else None,
    }
    logger.info(
        "tool_call tool=%s ok=%s latency_ms=%s",
        tool,
        ok,
        extra["latency_ms"],
        extra=extra,
    )
