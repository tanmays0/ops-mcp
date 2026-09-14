# Data Model: OpsMCP Server (Week 1 focus)

## Settings

- `fs_roots: list[Path]` — absolute allowlisted directories
- `fs_max_read_bytes: int` — hard cap on `fs_read_file`
- `log_level: str`

## PathSandboxError

Raised when a path escapes allowlisted roots or roots are invalid/empty.
Message MUST NOT reveal useful probing beyond "outside allowlist".

## FsSearchHit

- `path: str` — resolved path under an allowlisted root
- `line: int` — 1-based line number
- `text: str` — matching line content (may be truncated for display)

## FsReadResult

- `path: str`
- `size: int` — bytes read (possibly truncated)
- `truncated: bool`
- `content: str` — UTF-8 with `errors=replace`
- `encoding: str` — `"utf-8"`

## ToolCallLog (observability)

- `tool: str`
- `ok: bool`
- `latency_ms: float`
- `error: str | null` — redacted
