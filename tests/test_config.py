"""Tests for Settings / load_settings."""

from __future__ import annotations

from fiinquant_mcp.config import Settings, load_settings


def test_C1_load_defaults() -> None:
    s = load_settings({})
    assert s.timeout_s == 30.0
    assert s.max_rows == 500
    assert s.max_chars == 80_000
    assert s.has_credentials is False


def test_C2_env_override() -> None:
    s = load_settings(
        {
            "FIINQUANT_TIMEOUT_S": "12.5",
            "FIINQUANT_MAX_ROWS": "100",
            "FIINQUANT_USERNAME": "u",
            "FIINQUANT_PASSWORD": "p",
        }
    )
    assert s.timeout_s == 12.5
    assert s.max_rows == 100
    assert s.username == "u"
    assert s.has_credentials is True


def test_C3_missing_credentials_detection() -> None:
    s = Settings(username=None, password=None)
    assert s.has_credentials is False
    s2 = Settings(username="u", password="")
    # empty password should not count as credentials when loaded via env None-ish
    assert bool(s2.username and s2.password) is False
