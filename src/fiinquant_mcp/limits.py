"""FiinQuant plan limits — defaults match Free / Trải nghiệm Miễn phí.

Official free tier (as of user account comparison):
  - Max connections: 1
  - Requests / month: 100_000
  - Requests / minute: 90
  - Requests / second: 80
  - Realtime max tickers: 33
  - Timeframes: 1m, 5m, 15m, 1h, 4h
  - Max history depth: 1 month
"""

from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Iterable

from fiinquant_mcp.errors import ErrorCode, GatewayError

# Free-tier constants (documented defaults)
FREE_MAX_CONNECTIONS = 1
FREE_REQUESTS_PER_MONTH = 100_000
FREE_REQUESTS_PER_MINUTE = 90
FREE_REQUESTS_PER_SECOND = 80
FREE_MAX_REALTIME_TICKERS = 33
FREE_MAX_HISTORY_DAYS = 31
FREE_INTRADAY_TIMEFRAMES = frozenset({"1m", "5m", "15m", "1h", "4h", "1M", "5M", "15M", "1H", "4H"})
# Daily/weekly still useful for EOD research; free plan may allow EOD with 1-month depth.
ALLOWED_FREQUENCIES = frozenset(
    {
        "1m",
        "5m",
        "15m",
        "1h",
        "4h",
        "Daily",
        "1d",
        "daily",
        "Weekly",
        "Monthly",
        "Quarterly",
        "Yearly",
    }
)


@dataclass(frozen=True, slots=True)
class PlanLimits:
    """Runtime plan limits (env-overridable)."""

    plan: str = "free"
    enforce: bool = True
    max_connections: int = FREE_MAX_CONNECTIONS
    requests_per_minute: int = FREE_REQUESTS_PER_MINUTE
    requests_per_second: int = FREE_REQUESTS_PER_SECOND
    max_realtime_tickers: int = FREE_MAX_REALTIME_TICKERS
    max_history_days: int = FREE_MAX_HISTORY_DAYS

    @property
    def is_free(self) -> bool:
        return self.plan.lower() in {"free", "trial", "mienphi", "miễn phí", "demo"}


def _parse_date(value: str | date | datetime | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    # YYYY-MM-DD
    try:
        return date.fromisoformat(text[:10])
    except ValueError as exc:
        raise GatewayError(
            ErrorCode.VALIDATION,
            f"Invalid date '{value}' (expect YYYY-MM-DD)",
            hint="Use ISO dates like 2024-01-15",
        ) from exc


def validate_history_window(
    limits: PlanLimits,
    *,
    start: str | date | None = None,
    end: str | date | None = None,
    from_date: str | date | None = None,
    to_date: str | date | None = None,
) -> None:
    """Reject ranges longer than plan max history depth."""
    if not limits.enforce:
        return
    a = _parse_date(start) or _parse_date(from_date)
    b = _parse_date(end) or _parse_date(to_date) or date.today()
    if a is None:
        return
    if b < a:
        raise GatewayError(
            ErrorCode.VALIDATION,
            "end/to_date must be on or after start/from_date",
        )
    span = (b - a).days
    if span > limits.max_history_days:
        raise GatewayError(
            ErrorCode.VALIDATION,
            f"History window {span}d exceeds plan limit {limits.max_history_days}d "
            f"(FiinQuant free = 1 month)",
            hint=f"Shorten range to ≤ {limits.max_history_days} days or upgrade plan",
        )


def validate_ticker_count(
    limits: PlanLimits,
    tickers: Iterable[str] | None,
    *,
    realtime: bool = False,
) -> None:
    if not limits.enforce or tickers is None:
        return
    n = len(list(tickers))
    if realtime and n > limits.max_realtime_tickers:
        raise GatewayError(
            ErrorCode.VALIDATION,
            f"Realtime allows max {limits.max_realtime_tickers} tickers on free plan "
            f"(got {n})",
            hint="Split into smaller batches (≤33) or upgrade plan",
        )


def validate_frequency(limits: PlanLimits, frequency: str | None) -> None:
    if not limits.enforce or not frequency:
        return
    freq = frequency.strip()
    if freq not in ALLOWED_FREQUENCIES and freq not in FREE_INTRADAY_TIMEFRAMES:
        raise GatewayError(
            ErrorCode.VALIDATION,
            f"Unsupported frequency '{frequency}' for free-tier timeframes",
            hint="Use 1m, 5m, 15m, 1h, 4h, or Daily",
        )


class RateLimiter:
    """Thread-safe sliding-window limiter for req/s and req/min."""

    def __init__(
        self,
        *,
        per_second: int,
        per_minute: int,
        enabled: bool = True,
    ) -> None:
        self.per_second = max(1, per_second)
        self.per_minute = max(1, per_minute)
        self.enabled = enabled
        self._lock = threading.Lock()
        self._hits: deque[float] = deque()

    def acquire(self) -> None:
        if not self.enabled:
            return
        now = time.monotonic()
        with self._lock:
            self._prune(now)
            sec = sum(1 for t in self._hits if now - t < 1.0)
            minute = len(self._hits)
            if sec >= self.per_second:
                raise GatewayError(
                    ErrorCode.RATE_LIMIT,
                    f"Rate limit: {self.per_second} requests/second (free plan)",
                    hint="Slow down tool calls; free tier allows 80 req/s, 90 req/min",
                )
            if minute >= self.per_minute:
                raise GatewayError(
                    ErrorCode.RATE_LIMIT,
                    f"Rate limit: {self.per_minute} requests/minute (free plan)",
                    hint="Wait a few seconds; free tier = 90 req/min, 100k/month",
                )
            self._hits.append(now)

    def _prune(self, now: float) -> None:
        while self._hits and now - self._hits[0] >= 60.0:
            self._hits.popleft()

    def snapshot(self) -> dict[str, Any]:
        now = time.monotonic()
        with self._lock:
            self._prune(now)
            return {
                "enabled": self.enabled,
                "per_second": self.per_second,
                "per_minute": self.per_minute,
                "hits_last_minute": len(self._hits),
            }


def clamp_date_range_kwargs(limits: PlanLimits, kwargs: dict[str, Any]) -> dict[str, Any]:
    """Validate history-related kwargs in place; returns kwargs for chaining."""
    validate_history_window(
        limits,
        start=kwargs.get("start"),
        end=kwargs.get("end"),
        from_date=kwargs.get("from_date"),
        to_date=kwargs.get("to_date"),
    )
    if "frequency" in kwargs:
        validate_frequency(limits, kwargs.get("frequency"))
    by = kwargs.get("by")
    if limits.enforce and by in {"30m", "30M"}:
        raise GatewayError(
            ErrorCode.VALIDATION,
            "Timeframe 30m is not on free-plan list (1m,5m,15m,1h,4h)",
            hint="Pick 15m or 1h instead",
        )
    tickers = kwargs.get("tickers")
    if isinstance(tickers, (list, tuple)):
        # treat latest/realtime style ops cautiously when many tickers
        if kwargs.get("latest") or kwargs.get("max_realtime_events") is not None:
            validate_ticker_count(limits, tickers, realtime=True)
        elif len(tickers) > limits.max_realtime_tickers * 3:
            # soft guard: very large batches burn free quota fast
            raise GatewayError(
                ErrorCode.VALIDATION,
                f"Too many tickers in one call ({len(tickers)}). "
                f"Free plan is easy to exhaust — batch ≤ {limits.max_realtime_tickers}.",
                hint="Split tickers into smaller requests",
            )
    return kwargs


def default_end_if_missing(start: str | None, end: str | None, max_days: int) -> str | None:
    """If only start given, cap end at start+max_days or today."""
    if end or not start:
        return end
    a = _parse_date(start)
    if a is None:
        return end
    capped = min(date.today(), a + timedelta(days=max_days))
    return capped.isoformat()
