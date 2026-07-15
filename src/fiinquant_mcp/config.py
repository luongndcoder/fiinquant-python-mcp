"""Environment-driven settings for the personal FiinQuant MCP server."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime configuration loaded from environment variables."""

    username: str | None
    password: str | None
    timeout_s: float = 30.0
    max_rows: int = 500
    max_chars: int = 80_000
    log_level: str = "INFO"

    @property
    def has_credentials(self) -> bool:
        return bool(self.username and self.password)


def load_settings(environ: dict[str, str] | None = None) -> Settings:
    """Load settings from *environ* or ``os.environ``."""
    env = environ if environ is not None else os.environ
    timeout_raw = env.get("FIINQUANT_TIMEOUT_S", "30")
    max_rows_raw = env.get("FIINQUANT_MAX_ROWS", "500")
    max_chars_raw = env.get("FIINQUANT_MAX_CHARS", "80000")
    return Settings(
        username=env.get("FIINQUANT_USERNAME") or None,
        password=env.get("FIINQUANT_PASSWORD") or None,
        timeout_s=float(timeout_raw),
        max_rows=int(max_rows_raw),
        max_chars=int(max_chars_raw),
        log_level=(env.get("FIINQUANT_LOG_LEVEL") or "INFO").upper(),
    )
