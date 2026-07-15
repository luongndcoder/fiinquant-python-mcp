"""P1 domain tools — happy + validation paths."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from fiinquant_mcp.errors import ErrorCode, GatewayError
from fiinquant_mcp.tools import fundamental, market, meta, screening, universe


def _gw(result=None, error: GatewayError | None = None) -> MagicMock:
    gw = MagicMock()
    gw.settings = MagicMock(max_rows=500, max_chars=80_000)
    if error is not None:
        gw.call = AsyncMock(side_effect=error)
    else:
        gw.call = AsyncMock(return_value=result if result is not None else {"ok": True})
    return gw


@pytest.mark.asyncio
async def test_financial_ratios_happy() -> None:
    gw = _gw([{"ticker": "FPT", "roe": 25}])
    raw = await fundamental.fq_get_financial_ratios("FPT", gateway=gw)
    payload = json.loads(raw)
    assert payload["ok"] is True
    gw.call.assert_awaited()
    assert gw.call.await_args.args[0] == "get_financial_ratios"


@pytest.mark.asyncio
async def test_financial_statements_invalid_type() -> None:
    gw = _gw()
    raw = await fundamental.fq_get_financial_statements(
        "FPT", "income", gateway=gw
    )
    payload = json.loads(raw)
    assert payload["ok"] is False
    assert payload["code"] == "VALIDATION"
    gw.call.assert_not_awaited()


@pytest.mark.asyncio
async def test_financial_statements_happy() -> None:
    gw = _gw([{"line": "revenue", "value": 1}])
    raw = await fundamental.fq_get_financial_statements(
        "FPT", "income_statement", years="2023,2024", gateway=gw
    )
    payload = json.loads(raw)
    assert payload["ok"] is True
    kwargs = gw.call.await_args.kwargs
    assert kwargs["statement"] == "income_statement"
    assert kwargs["years"] == [2023, 2024]


@pytest.mark.asyncio
async def test_screen_stocks_bad_json() -> None:
    gw = _gw()
    raw = await screening.fq_screen_stocks(filters="not-json", gateway=gw)
    payload = json.loads(raw)
    assert payload["ok"] is False
    assert payload["code"] == "VALIDATION"


@pytest.mark.asyncio
async def test_screen_stocks_happy_caps_limit() -> None:
    gw = _gw([{"ticker": "AAA"}])
    raw = await screening.fq_screen_stocks(
        filters='[{"indicator":"roe","operator":"gt","value":20}]',
        limit=999,
        gateway=gw,
    )
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert gw.call.await_args.kwargs["limit"] == 200


@pytest.mark.asyncio
async def test_technical_indicators_happy() -> None:
    gw = _gw([{"rsi": 55}])
    raw = await screening.fq_get_technical_indicators(
        "VNM",
        '[{"name":"rsi","window":14}]',
        gateway=gw,
    )
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert gw.call.await_args.args[0] == "get_technical_indicators"


@pytest.mark.asyncio
async def test_stock_prices_and_index() -> None:
    gw = _gw([{"close": 100}])
    raw = await market.fq_get_stock_prices("FPT", latest=True, gateway=gw)
    assert json.loads(raw)["ok"] is True
    raw2 = await market.fq_get_index_constituents("vn30", gateway=gw)
    assert json.loads(raw2)["ok"] is True
    assert gw.call.await_args.kwargs["index"] == "VN30"


@pytest.mark.asyncio
async def test_basic_info_and_snapshot() -> None:
    gw = _gw({"name": "FPT"})
    raw = await universe.fq_get_basic_info("FPT", gateway=gw)
    assert json.loads(raw)["ok"] is True
    raw2 = await fundamental.fq_get_equity_snapshot("FPT", metrics="pe,pb", gateway=gw)
    assert json.loads(raw2)["ok"] is True
    assert gw.call.await_args.kwargs["metrics"] == ["pe", "pb"]


@pytest.mark.asyncio
async def test_list_ops_no_network() -> None:
    raw = await meta.fq_list_ops()
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert payload["data"]["count"] >= 15
    assert "screen_stocks" in payload["data"]["ops"]


@pytest.mark.asyncio
async def test_call_method_dry_run() -> None:
    gw = _gw()
    raw = await meta.fq_call_method(
        "SomeMethod", params='{"a":1}', dry_run=True, gateway=gw
    )
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert payload["data"]["dry_run"] is True
    gw.call.assert_not_awaited()


@pytest.mark.asyncio
async def test_sdk_error_envelope() -> None:
    gw = _gw(error=GatewayError(ErrorCode.SDK_ERROR, "boom"))
    raw = await market.fq_get_market_breadth(gateway=gw)
    payload = json.loads(raw)
    assert payload["ok"] is False
    assert payload["code"] == "SDK_ERROR"
