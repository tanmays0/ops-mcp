"""Shared pytest fixtures for OpsMCP."""

from __future__ import annotations

from pathlib import Path

import pytest

from ops_mcp.config import Settings, get_settings


@pytest.fixture
def sandbox_tree(tmp_path: Path) -> dict[str, Path]:
    """Create an allowlisted tree plus an outside sibling for escape tests."""
    root = tmp_path / "allow"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()

    safe = root / "safe"
    nested = safe / "nested"
    nested.mkdir(parents=True)
    readme = safe / "readme.txt"
    readme.write_text("hello sandbox marker line\n", encoding="utf-8")
    (nested / "a.py").write_text('SANDBOX_TOKEN = "hello sandbox"\n', encoding="utf-8")

    secret_outside = outside / "secret.txt"
    secret_outside.write_text("SHOULD_NOT_LEAK\n", encoding="utf-8")

    return {
        "root": root,
        "outside": outside,
        "readme": readme,
        "secret_outside": secret_outside,
    }


@pytest.fixture
def settings_for_sandbox(sandbox_tree: dict[str, Path]) -> Settings:
    """Settings pointed at the tmp allowlisted root."""
    get_settings.cache_clear()
    settings = Settings(
        fs_roots=[sandbox_tree["root"]],
        fs_max_read_bytes=64,
        log_level="INFO",
    )
    yield settings
    get_settings.cache_clear()
