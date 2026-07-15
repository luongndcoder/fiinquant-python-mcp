"""Shared fixtures for fiinquant_mcp tests."""

from __future__ import annotations

import pytest

from fiinquant_mcp.config import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(
        username="test_user",
        password="test_pass",
        timeout_s=0.5,
        max_rows=5,
        max_chars=2000,
        log_level="DEBUG",
    )


@pytest.fixture
def settings_no_creds() -> Settings:
    return Settings(
        username=None,
        password=None,
        timeout_s=0.5,
        max_rows=5,
        max_chars=2000,
    )
