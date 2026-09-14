"""Fail-closed path sandbox tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from ops_mcp.security.path_sandbox import PathSandboxError, resolve_under_roots, validate_roots


def test_path_inside_root_ok(sandbox_tree: dict[str, Path]) -> None:
    root = sandbox_tree["root"]
    readme = sandbox_tree["readme"]
    resolved = resolve_under_roots(str(readme), [root])
    assert resolved == readme.resolve()
    assert root.resolve() in resolved.parents or resolved == root.resolve()


def test_dotdot_escape_fails(sandbox_tree: dict[str, Path]) -> None:
    root = sandbox_tree["root"]
    escape = root / ".." / "outside" / "secret.txt"
    with pytest.raises(PathSandboxError):
        resolve_under_roots(str(escape), [root])


def test_absolute_outside_fails(sandbox_tree: dict[str, Path]) -> None:
    root = sandbox_tree["root"]
    secret = sandbox_tree["secret_outside"]
    with pytest.raises(PathSandboxError):
        resolve_under_roots(str(secret), [root])


def test_symlink_escape_fails(sandbox_tree: dict[str, Path]) -> None:
    root = sandbox_tree["root"]
    secret = sandbox_tree["secret_outside"]
    link = root / "safe" / "leak_link"
    link.symlink_to(secret)
    with pytest.raises(PathSandboxError):
        resolve_under_roots(str(link), [root])


def test_empty_roots_fail(sandbox_tree: dict[str, Path]) -> None:
    with pytest.raises(PathSandboxError):
        resolve_under_roots(str(sandbox_tree["readme"]), [])


def test_validate_roots_missing_dir(tmp_path: Path) -> None:
    missing = tmp_path / "nope"
    with pytest.raises(PathSandboxError):
        validate_roots([missing])


def test_tilde_path_fails(sandbox_tree: dict[str, Path]) -> None:
    with pytest.raises(PathSandboxError):
        resolve_under_roots("~/something", [sandbox_tree["root"]])


def test_encoded_dotdot_segments_fail(sandbox_tree: dict[str, Path]) -> None:
    root = sandbox_tree["root"]
    # Nested .. after a real child still escapes after resolve.
    sneaky = str(root / "safe" / ".." / ".." / "outside" / "secret.txt")
    with pytest.raises(PathSandboxError):
        resolve_under_roots(sneaky, [root])
