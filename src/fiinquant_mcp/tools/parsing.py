"""Shared input parsing helpers for tools."""

from __future__ import annotations

import json
from typing import Any


def parse_tickers(tickers: str | list[str] | None) -> list[str]:
    if tickers is None:
        return []
    if isinstance(tickers, list):
        return [str(t).strip().upper() for t in tickers if str(t).strip()]
    parts = [p.strip().upper() for p in str(tickers).replace(";", ",").split(",")]
    return [p for p in parts if p]


def parse_jsonish(value: str | None) -> Any:
    """Parse optional JSON string; return None if empty; raise ValueError if invalid."""
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    return json.loads(text)


def parse_str_list(value: str | None) -> list[str] | None:
    if value is None or not str(value).strip():
        return None
    return [p.strip() for p in str(value).replace(";", ",").split(",") if p.strip()]


def parse_int_list(value: str | None) -> list[int] | None:
    items = parse_str_list(value)
    if items is None:
        return None
    return [int(x) for x in items]
