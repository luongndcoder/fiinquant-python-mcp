"""Universe / ticker metadata tools."""

from __future__ import annotations

from fiinquant_mcp.errors import ErrorCode, error_json
from fiinquant_mcp.gateway import FiinQuantGateway
from fiinquant_mcp.tools._common import resolve_gateway, run_gateway_op


async def fq_list_tickers(
    market: str | None = None,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    """List tickers, optionally filtered by market (e.g. HOSE, HNX)."""
    gw = resolve_gateway(gateway)
    return await run_gateway_op(gw, "list_tickers", market=market)


async def fq_ticker_info(
    ticker: str,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    """Basic metadata for a single ticker."""
    t = (ticker or "").strip().upper()
    if not t:
        return error_json(
            ErrorCode.VALIDATION,
            "ticker is required",
            hint="Example: VNM",
        )
    gw = resolve_gateway(gateway)
    return await run_gateway_op(gw, "ticker_info", ticker=t)
