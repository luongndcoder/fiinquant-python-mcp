"""P0 market tools (phase 05 — RED until 07)."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from fiinquant_mcp.errors import ErrorCode, GatewayError
from fiinquant_mcp.tools.market import fq_get_price_history


@pytest.mark.asyncio
async def test_T2_get_price_history_happy() -> None:
    gw = MagicMock()
    gw.call = AsyncMock(
        return_value=[{"ticker": "FPT", "close": 100}, {"ticker": "FPT", "close": 101}]
    )
    gw.settings = MagicMock(max_rows=500, max_chars=80_000)
    raw = await fq_get_price_history(
        "FPT",
        "2024-01-01",
        "2024-01-10",
        gateway=gw,
    )
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert payload["meta"]["row_count"] == 2
    gw.call.assert_awaited_once()
    args, kwargs = gw.call.await_args
    assert args[0] == "get_price_history"
    assert kwargs["tickers"] == ["FPT"]


@pytest.mark.asyncio
async def test_T3_get_price_history_timeout_envelope() -> None:
    gw = MagicMock()
    gw.call = AsyncMock(
        side_effect=GatewayError(ErrorCode.TIMEOUT, "exceeded 30s", hint="narrow range")
    )
    gw.settings = MagicMock(max_rows=500, max_chars=80_000)
    raw = await fq_get_price_history("FPT", "2020-01-01", "2024-01-01", gateway=gw)
    payload = json.loads(raw)
    assert payload["ok"] is False
    assert payload["code"] == "TIMEOUT"


@pytest.mark.asyncio
async def test_T4_get_price_history_empty_ticker_validation() -> None:
    gw = MagicMock()
    gw.call = AsyncMock()
    gw.settings = MagicMock(max_rows=500, max_chars=80_000)
    raw = await fq_get_price_history("  ", "2024-01-01", "2024-01-10", gateway=gw)
    payload = json.loads(raw)
    assert payload["ok"] is False
    assert payload["code"] == "VALIDATION"
    gw.call.assert_not_awaited()
