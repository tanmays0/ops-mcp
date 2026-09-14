"""Application settings loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ENV_FILE = _REPO_ROOT / ".env"


class Settings(BaseSettings):
    """Runtime configuration for OpsMCP.

    Environment variables use the ``OPS_MCP_`` prefix.
    ``OPS_MCP_FS_ROOTS`` is a colon-separated list of absolute paths.
    Secrets load from process env and from ``<repo>/.env`` (gitignored).
    """

    model_config = SettingsConfigDict(
        env_prefix="OPS_MCP_",
        env_file=str(_ENV_FILE) if _ENV_FILE.is_file() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    fs_roots: Annotated[list[Path], NoDecode] = Field(default_factory=list)
    fs_max_read_bytes: int = 65_536
    log_level: str = "INFO"

    github_token: SecretStr | None = None
    github_api_base: str = "https://api.github.com"
    http_rate_per_second: float = 5.0
    http_timeout_seconds: float = 30.0

    database_url: SecretStr | None = None
    postgres_max_rows: int = 500

    @field_validator("fs_roots", mode="before")
    @classmethod
    def _parse_fs_roots(cls, value: object) -> list[Path] | object:
        if value is None or value == "":
            return []
        if isinstance(value, list):
            return [Path(str(item)) for item in value]
        if isinstance(value, (str, Path)):
            raw = str(value)
            parts = [part for part in raw.split(":") if part]
            return [Path(part) for part in parts]
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings. Call ``get_settings.cache_clear()`` in tests."""
    return Settings()
