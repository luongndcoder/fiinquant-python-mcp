"""Free-plan limit guards."""

from __future__ import annotations

import pytest

from fiinquant_mcp.config import load_settings
from fiinquant_mcp.errors import ErrorCode, GatewayError
from fiinquant_mcp.gateway import FiinQuantGateway
from fiinquant_mcp.limits import (
    PlanLimits,
    RateLimiter,
    validate_frequency,
    validate_history_window,
    validate_ticker_count,
)


def test_free_defaults_in_settings() -> None:
    s = load_settings({"FIINQUANT_PLAN": "free"})
    assert s.plan == "free"
    assert s.max_history_days == 31
    assert s.max_realtime_tickers == 33
    assert s.requests_per_minute == 90
    assert s.requests_per_second == 80
    assert s.enforce_plan_limits is True


def test_history_window_rejects_too_long() -> None:
    limits = PlanLimits(plan="free", enforce=True, max_history_days=31)
    with pytest.raises(GatewayError) as ei:
        validate_history_window(
            limits, start="2024-01-01", end="2024-03-01"
        )
    assert ei.value.code == ErrorCode.VALIDATION
    assert "31" in ei.value.message


def test_history_window_ok_within_month() -> None:
    limits = PlanLimits(plan="free", enforce=True, max_history_days=31)
    validate_history_window(limits, start="2024-01-01", end="2024-01-20")


def test_realtime_ticker_cap() -> None:
    limits = PlanLimits(plan="free", enforce=True, max_realtime_tickers=33)
    tickers = [f"T{i}" for i in range(40)]
    with pytest.raises(GatewayError) as ei:
        validate_ticker_count(limits, tickers, realtime=True)
    assert ei.value.code == ErrorCode.VALIDATION


def test_rate_limiter_per_second() -> None:
    rl = RateLimiter(per_second=2, per_minute=90, enabled=True)
    rl.acquire()
    rl.acquire()
    with pytest.raises(GatewayError) as ei:
        rl.acquire()
    assert ei.value.code == ErrorCode.RATE_LIMIT


@pytest.mark.asyncio
async def test_gateway_enforces_history() -> None:
    class C:
        def login(self) -> None:
            return None

        def get_price_history(self, **kw):  # noqa: ANN003
            return kw

    settings = load_settings(
        {
            "FIINQUANT_USERNAME": "u",
            "FIINQUANT_PASSWORD": "p",
            "FIINQUANT_PLAN": "free",
            "FIINQUANT_ENFORCE_PLAN_LIMITS": "true",
        }
    )
    gw = FiinQuantGateway(settings, client_factory=lambda _s: C())
    with pytest.raises(GatewayError) as ei:
        await gw.call(
            "get_price_history",
            tickers=["FPT"],
            start="2024-01-01",
            end="2024-06-01",
        )
    assert ei.value.code == ErrorCode.VALIDATION


def test_frequency_allows_free_timeframes() -> None:
    limits = PlanLimits(plan="free", enforce=True)
    for f in ("1m", "5m", "15m", "1h", "4h", "Daily"):
        validate_frequency(limits, f)
