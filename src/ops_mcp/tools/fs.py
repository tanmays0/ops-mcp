"""Filesystem MCP tools: sandboxed search and read."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from ops_mcp.config import Settings, get_settings
from ops_mcp.logging_setup import log_tool_call
from ops_mcp.security.path_sandbox import PathSandboxError, resolve_under_roots, validate_roots

_BINARY_PROBE_BYTES = 8192


def _settings_or_default(settings: Settings | None) -> Settings:
    return settings if settings is not None else get_settings()


def _is_probably_binary(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            chunk = handle.read(_BINARY_PROBE_BYTES)
    except OSError:
        return True
    return b"\x00" in chunk


def fs_search(
    query: str,
    root: str | None = None,
    max_results: int = 50,
    *,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Search allowlisted roots for a literal substring.

    Args:
        query: Case-sensitive literal substring to find.
        root: Optional path that must resolve under an allowlisted root.
            When omitted, all configured roots are searched.
        max_results: Maximum number of hits to return (default 50).

    Returns:
        ``{"hits": [{"path", "line", "text"}, ...]}``

    Raises:
        PathSandboxError: If ``root`` escapes the allowlist or roots are invalid.
    """
    started = time.perf_counter()
    cfg = _settings_or_default(settings)
    try:
        if not query:
            result: dict[str, Any] = {"hits": []}
            log_tool_call("fs_search", ok=True, latency_ms=(time.perf_counter() - started) * 1000)
            return result

        roots = validate_roots(cfg.fs_roots)
        search_roots: list[Path]
        if root is not None:
            search_roots = [resolve_under_roots(root, roots)]
            if not search_roots[0].is_dir():
                raise PathSandboxError("outside allowlist")
        else:
            search_roots = roots

        hits: list[dict[str, Any]] = []
        limit = max(1, max_results)

        for search_root in search_roots:
            for path in search_root.rglob("*"):
                if len(hits) >= limit:
                    break
                if not path.is_file():
                    continue
                try:
                    safe_path = resolve_under_roots(path, roots)
                except PathSandboxError:
                    continue
                if _is_probably_binary(safe_path):
                    continue
                try:
                    text = safe_path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    if query in line:
                        hits.append(
                            {
                                "path": str(safe_path),
                                "line": line_no,
                                "text": line[:500],
                            }
                        )
                        if len(hits) >= limit:
                            break
            if len(hits) >= limit:
                break

        result = {"hits": hits}
        log_tool_call("fs_search", ok=True, latency_ms=(time.perf_counter() - started) * 1000)
        return result
    except Exception as exc:
        log_tool_call(
            "fs_search",
            ok=False,
            latency_ms=(time.perf_counter() - started) * 1000,
            error=str(exc),
        )
        raise


def fs_read_file(
    path: str,
    max_bytes: int | None = None,
    *,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Read a file under allowlisted roots with a hard size cap.

    Args:
        path: File path that must resolve inside an allowlisted root.
        max_bytes: Optional per-call cap; never exceeds server ``fs_max_read_bytes``.

    Returns:
        ``{"path", "size", "truncated", "content", "encoding"}``

    Raises:
        PathSandboxError: If the path escapes the allowlist.
        IsADirectoryError: If the path is a directory.
        FileNotFoundError: If the path does not exist.
    """
    started = time.perf_counter()
    cfg = _settings_or_default(settings)
    try:
        safe_path = resolve_under_roots(path, cfg.fs_roots)
        if safe_path.is_dir():
            raise IsADirectoryError(f"path is a directory: {safe_path}")
        if not safe_path.is_file():
            raise FileNotFoundError(f"file not found: {safe_path}")

        cap = cfg.fs_max_read_bytes
        if max_bytes is not None:
            cap = min(max(0, max_bytes), cfg.fs_max_read_bytes)

        data = safe_path.read_bytes()
        truncated = len(data) > cap
        chunk = data[:cap]
        content = chunk.decode("utf-8", errors="replace")
        result = {
            "path": str(safe_path),
            "size": len(chunk),
            "truncated": truncated,
            "content": content,
            "encoding": "utf-8",
        }
        log_tool_call("fs_read_file", ok=True, latency_ms=(time.perf_counter() - started) * 1000)
        return result
    except Exception as exc:
        log_tool_call(
            "fs_read_file",
            ok=False,
            latency_ms=(time.perf_counter() - started) * 1000,
            error=str(exc),
        )
        raise
