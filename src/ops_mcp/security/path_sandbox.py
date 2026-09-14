"""Path sandbox: resolve then fail closed outside allowlisted roots."""

from __future__ import annotations

from pathlib import Path


class PathSandboxError(ValueError):
    """Raised when a path escapes allowlisted roots or roots are invalid."""


def validate_roots(roots: list[Path]) -> list[Path]:
    """Resolve and validate allowlisted roots.

    Raises:
        PathSandboxError: If roots is empty or any root is missing/not a dir.
    """
    if not roots:
        raise PathSandboxError("outside allowlist")

    resolved_roots: list[Path] = []
    for root in roots:
        resolved = Path(root).expanduser().resolve()
        if not resolved.is_dir():
            raise PathSandboxError("outside allowlist")
        resolved_roots.append(resolved)
    return resolved_roots


def _is_under_root(resolved: Path, root: Path) -> bool:
    """Return True if ``resolved`` is ``root`` or a descendant of ``root``.

    Both paths MUST already be fully resolved (symlink-aware). This predicate
    is the fail-closed heart of the filesystem safety bar.
    """
    if resolved == root:
        return True
    return root in resolved.parents


def resolve_under_roots(user_path: str | Path, roots: list[Path]) -> Path:
    """Resolve ``user_path`` and ensure it stays under an allowlisted root.

    Disallows home-directory expansion shortcuts in user input (``~``) so
    agents cannot pivot via the operator's home directory.

    Raises:
        PathSandboxError: On empty roots, invalid roots, ``~`` input, or escape.
    """
    text = str(user_path)
    if text.startswith("~"):
        raise PathSandboxError("outside allowlist")

    resolved_roots = validate_roots(roots)
    # Resolve relative to CWD then check membership; never trust string prefixes.
    resolved = Path(text).resolve()

    for root in resolved_roots:
        if _is_under_root(resolved, root):
            return resolved

    raise PathSandboxError("outside allowlist")
