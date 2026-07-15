"""Market / price history tools."""

from __future__ import annotations

from fiinquant_mcp.errors import ErrorCode, error_json
from fiinquant_mcp.gateway import FiinQuantGateway
from fiinquant_mcp.tools._common import resolve_gateway, run_gateway_op


def _parse_tickers(tickers: str) -> list[str]:
    parts = [p.strip().upper() for p in tickers.replace(";", ",").split(",")]
    return [p for p in parts if p]


async def fq_get_price_history(
    tickers: str,
    start: str,
    end: str,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    """Fetch OHLCV / price history for one or more tickers (comma-separated)."""
    parsed = _parse_tickers(tickers)
    if not parsed:
        return error_json(
            ErrorCode.VALIDATION,
            "tickers must be a non-empty comma-separated list",
            hint="Example: FPT,VNM",
        )
    if not (start and start.strip()) or not (end and end.strip()):
        return error_json(
            ErrorCode.VALIDATION,
            "start and end dates are required (YYYY-MM-DD)",
        )
    gw = resolve_gateway(gateway)
    return await run_gateway_op(
        gw,
        "get_price_history",
        tickers=parsed,
        start=start.strip(),
        end=end.strip(),
    )
