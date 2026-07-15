"""Tests for FiinQuantGateway reliability kit (phase 02 — expect RED until 04)."""

from __future__ import annotations

import time
from typing import Any

import pytest

from fiinquant_mcp.config import Settings
from fiinquant_mcp.errors import ErrorCode, GatewayError
from fiinquant_mcp.gateway import FiinQuantGateway


class FakeClient:
    """Injectable client for Gateway unit tests."""

    def __init__(
        self,
        *,
        fail_login: bool = False,
        raise_on_call: Exception | None = None,
        sleep_s: float = 0.0,
        fail_first_n: int = 0,
        session_expired_once: bool = False,
    ) -> None:
        self.fail_login = fail_login
        self.raise_on_call = raise_on_call
        self.sleep_s = sleep_s
        self.fail_first_n = fail_first_n
        self.session_expired_once = session_expired_once
        self.login_calls = 0
        self.call_count = 0
        self._expired_raised = False

    def login(self) -> None:
        self.login_calls += 1
        if self.fail_login:
            raise RuntimeError("bad credentials")

    def get_price_history(
        self,
        tickers: list[str],
        start: str,
        end: str,
        **kwargs: Any,
    ) -> Any:
        return self._op("get_price_history", tickers=tickers, start=start, end=end, **kwargs)

    def list_tickers(self, market: str | None = None) -> Any:
        return self._op("list_tickers", market=market)

    def ticker_info(self, ticker: str) -> Any:
        return self._op("ticker_info", ticker=ticker)

    def _op(self, name: str, **kwargs: Any) -> Any:
        self.call_count += 1
        if self.sleep_s:
            time.sleep(self.sleep_s)
        if self.session_expired_once and not self._expired_raised:
            self._expired_raised = True
            raise RuntimeError("session expired")
        if self.fail_first_n > 0:
            self.fail_first_n -= 1
            raise RuntimeError("transient")
        if self.raise_on_call is not None:
            raise self.raise_on_call
        return {"op": name, "kwargs": kwargs, "rows": [{"ok": True}]}


def _gateway(settings: Settings, client: FakeClient) -> FiinQuantGateway:
    return FiinQuantGateway(settings, client_factory=lambda _s: client)


@pytest.mark.asyncio
async def test_G1_no_credentials_auth_error(settings_no_creds: Settings) -> None:
    client = FakeClient()
    gw = _gateway(settings_no_creds, client)
    with pytest.raises(GatewayError) as ei:
        await gw.call("get_price_history", tickers=["AAA"], start="2024-01-01", end="2024-01-10")
    assert ei.value.code == ErrorCode.AUTH
    assert client.login_calls == 0


@pytest.mark.asyncio
async def test_G2_mock_client_success(settings: Settings) -> None:
    client = FakeClient()
    gw = _gateway(settings, client)
    result = await gw.call(
        "get_price_history",
        tickers=["FPT"],
        start="2024-01-01",
        end="2024-01-05",
    )
    assert result["op"] == "get_price_history"
    assert client.login_calls >= 1
    assert client.call_count == 1


@pytest.mark.asyncio
async def test_G3_sdk_exception_maps_to_sdk_error(settings: Settings) -> None:
    client = FakeClient(raise_on_call=RuntimeError("upstream boom"))
    gw = _gateway(settings, client)
    with pytest.raises(GatewayError) as ei:
        await gw.call("list_tickers", market="HOSE")
    assert ei.value.code == ErrorCode.SDK_ERROR
    assert "boom" in ei.value.message


@pytest.mark.asyncio
async def test_G4_slow_call_timeout(settings: Settings) -> None:
    # settings fixture timeout_s=0.5
    client = FakeClient(sleep_s=2.0)
    gw = _gateway(settings, client)
    with pytest.raises(GatewayError) as ei:
        await gw.call("ticker_info", ticker="VNM")
    assert ei.value.code == ErrorCode.TIMEOUT


@pytest.mark.asyncio
async def test_G5_session_expired_reauth_once(settings: Settings) -> None:
    client = FakeClient(session_expired_once=True)
    gw = _gateway(settings, client)
    result = await gw.call("list_tickers")
    assert result["op"] == "list_tickers"
    # login: initial + re-auth
    assert client.login_calls >= 2
    assert client.call_count >= 2


@pytest.mark.asyncio
async def test_G6_sequential_calls_same_gateway(settings: Settings) -> None:
    client = FakeClient()
    gw = _gateway(settings, client)
    r1 = await gw.call("list_tickers")
    r2 = await gw.call("ticker_info", ticker="AAA")
    assert r1["op"] == "list_tickers"
    assert r2["op"] == "ticker_info"
    assert client.login_calls == 1  # session reused
