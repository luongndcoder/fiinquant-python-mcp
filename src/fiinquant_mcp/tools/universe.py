"""Universe / ticker metadata tools."""

from __future__ import annotations

from fiinquant_mcp.errors import ErrorCode, error_json
from fiinquant_mcp.gateway import FiinQuantGateway
from fiinquant_mcp.tools._common import resolve_gateway, run_gateway_op
from fiinquant_mcp.tools.parsing import parse_tickers


async def get_basic_info(
    tickers: str | list[str],
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    parsed = parse_tickers(tickers)
    if not parsed:
        return error_json(ErrorCode.VALIDATION, "tickers is required")
    gw = resolve_gateway(gateway)
    return await run_gateway_op(gw, "get_basic_info", tickers=parsed)


async def get_icb_industries(
    level: int = 2,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    gw = resolve_gateway(gateway)
    return await run_gateway_op(gw, "get_icb_industries", level=level)


async def fq_list_tickers(
    market: str | None = None,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    """Personal extra: list tickers by market."""
    gw = resolve_gateway(gateway)
    return await run_gateway_op(gw, "list_tickers", market=market)


async def fq_ticker_info(
    ticker: str,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    """Personal extra: single ticker metadata."""
    t = (ticker or "").strip().upper()
    if not t:
        return error_json(ErrorCode.VALIDATION, "ticker is required", hint="Example: VNM")
    gw = resolve_gateway(gateway)
    return await run_gateway_op(gw, "ticker_info", ticker=t)


fq_get_basic_info = get_basic_info
fq_get_icb_industries = get_icb_industries
