"""P0 universe tools (phase 05 — RED until 07)."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from fiinquant_mcp.errors import ErrorCode, GatewayError
from fiinquant_mcp.tools.universe import fq_list_tickers, fq_ticker_info


@pytest.mark.asyncio
async def test_universe_list_happy() -> None:
    gw = MagicMock()
    gw.call = AsyncMock(return_value=[{"ticker": "AAA"}, {"ticker": "VNM"}])
    gw.settings = MagicMock(max_rows=500, max_chars=80_000)
    raw = await fq_list_tickers(market="HOSE", gateway=gw)
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert payload["meta"]["row_count"] == 2


@pytest.mark.asyncio
async def test_universe_ticker_info_happy() -> None:
    gw = MagicMock()
    gw.call = AsyncMock(return_value={"ticker": "VNM", "name": "Vinamilk"})
    gw.settings = MagicMock(max_rows=500, max_chars=80_000)
    raw = await fq_ticker_info("VNM", gateway=gw)
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert payload["data"]["ticker"] == "VNM"


@pytest.mark.asyncio
async def test_universe_sdk_error_mapped() -> None:
    gw = MagicMock()
    gw.call = AsyncMock(side_effect=GatewayError(ErrorCode.SDK_ERROR, "upstream"))
    gw.settings = MagicMock(max_rows=500, max_chars=80_000)
    raw = await fq_list_tickers(gateway=gw)
    payload = json.loads(raw)
    assert payload["ok"] is False
    assert payload["code"] == "SDK_ERROR"
