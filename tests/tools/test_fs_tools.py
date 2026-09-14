"""Filesystem tool tests — escape attempts must fail closed."""

from __future__ import annotations

from pathlib import Path

import pytest

from ops_mcp.config import Settings
from ops_mcp.security.path_sandbox import PathSandboxError
from ops_mcp.security.secrets import redact
from ops_mcp.tools.fs import fs_read_file, fs_search


def test_fs_read_file_allowlisted(
    sandbox_tree: dict[str, Path],
    settings_for_sandbox: Settings,
) -> None:
    result = fs_read_file(str(sandbox_tree["readme"]), settings=settings_for_sandbox)
    assert "hello sandbox" in result["content"]
    assert result["truncated"] is False
    assert result["encoding"] == "utf-8"


def test_fs_read_file_escape_fails(
    sandbox_tree: dict[str, Path],
    settings_for_sandbox: Settings,
) -> None:
    with pytest.raises(PathSandboxError):
        fs_read_file(str(sandbox_tree["secret_outside"]), settings=settings_for_sandbox)


def test_fs_read_file_dotdot_escape_fails(
    sandbox_tree: dict[str, Path],
    settings_for_sandbox: Settings,
) -> None:
    escape = sandbox_tree["root"] / ".." / "outside" / "secret.txt"
    with pytest.raises(PathSandboxError):
        result = fs_read_file(str(escape), settings=settings_for_sandbox)
        assert "SHOULD_NOT_LEAK" not in str(result)


def test_fs_read_file_truncates(
    sandbox_tree: dict[str, Path],
    settings_for_sandbox: Settings,
) -> None:
    big = sandbox_tree["root"] / "safe" / "big.txt"
    big.write_text("x" * 200, encoding="utf-8")
    result = fs_read_file(str(big), max_bytes=32, settings=settings_for_sandbox)
    assert result["truncated"] is True
    assert result["size"] <= 32
    assert len(result["content"].encode("utf-8")) <= 32


def test_fs_search_finds_literal(
    sandbox_tree: dict[str, Path],
    settings_for_sandbox: Settings,
) -> None:
    result = fs_search("hello sandbox", settings=settings_for_sandbox)
    assert len(result["hits"]) >= 1
    for hit in result["hits"]:
        assert str(sandbox_tree["root"].resolve()) in hit["path"]
        assert "hello sandbox" in hit["text"]


def test_fs_search_escape_root_fails(
    sandbox_tree: dict[str, Path],
    settings_for_sandbox: Settings,
) -> None:
    with pytest.raises(PathSandboxError):
        fs_search("SHOULD_NOT_LEAK", root=str(sandbox_tree["outside"]), settings=settings_for_sandbox)


def test_redact_github_pat() -> None:
    fake = "Authorization: token ghp_abcdefghijklmnopqrstuvwxyz0123456789"
    redacted = redact(fake)
    assert "ghp_" not in redacted or "[REDACTED]" in redacted
    assert "abcdefghijklmnopqrstuvwxyz0123456789" not in redacted
