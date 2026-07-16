"""Market / price / breadth tools (official + convenience)."""

from __future__ import annotations

from typing import Any

from fiinquant_mcp.errors import ErrorCode, error_json
from fiinquant_mcp.gateway import FiinQuantGateway
from fiinquant_mcp.tools._common import resolve_gateway, run_gateway_op
from fiinquant_mcp.tools.parsing import parse_tickers


async def get_stock_prices(
    tickers: str | list[str],
    from_date: str | None = None,
    to_date: str | None = None,
    frequency: str = "Daily",
    latest: bool = False,
    adjusted: bool = True,
    period: str | None = None,
    fields: str | list[str] | None = None,
    output_limit: int | None = None,
    include_unclosed: bool = True,
    basket: str | None = None,
    index_members: str | None = None,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    """Primary price source (official name)."""
    parsed = parse_tickers(tickers)
    if not parsed:
        return error_json(
            ErrorCode.VALIDATION,
            "tickers is required",
            hint="Example: [\"FPT\",\"VNM\"] or FPT,VNM",
        )
    from fiinquant_mcp.tools.parsing import parse_str_list

    gw = resolve_gateway(gateway)
    return await run_gateway_op(
        gw,
        "get_stock_prices",
        tickers=parsed,
        from_date=from_date,
        to_date=to_date,
        frequency=frequency,
        latest=latest,
        adjusted=adjusted,
        period=period,
        fields=parse_str_list(fields),
        output_limit=output_limit,
        include_unclosed=include_unclosed,
        basket=basket,
        index_members=index_members,
    )


async def fq_get_price_history(
    tickers: str | list[str],
    start: str,
    end: str,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    """Convenience OHLCV wrapper (personal extra, not official name)."""
    parsed = parse_tickers(tickers)
    if not parsed:
        return error_json(
            ErrorCode.VALIDATION,
            "tickers must be a non-empty list",
            hint="Example: FPT,VNM",
        )
    if not (start and str(start).strip()) or not (end and str(end).strip()):
        return error_json(
            ErrorCode.VALIDATION,
            "start and end dates are required (YYYY-MM-DD)",
        )
    gw = resolve_gateway(gateway)
    return await run_gateway_op(
        gw,
        "get_price_history",
        tickers=parsed,
        start=str(start).strip(),
        end=str(end).strip(),
    )


async def get_market_statistics(
    tickers: str | list[str],
    metric: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    time_filter: str = "Daily",
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    parsed = parse_tickers(tickers)
    if not parsed:
        return error_json(ErrorCode.VALIDATION, "tickers is required")
    gw = resolve_gateway(gateway)
    return await run_gateway_op(
        gw,
        "get_market_statistics",
        tickers=parsed,
        metric=metric,
        from_date=from_date,
        to_date=to_date,
        time_filter=time_filter,
    )


async def get_market_breadth(
    index: str = "VNINDEX",
    from_date: str | None = None,
    to_date: str | None = None,
    time_filter: str = "Daily",
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    gw = resolve_gateway(gateway)
    return await run_gateway_op(
        gw,
        "get_market_breadth",
        index=index,
        from_date=from_date,
        to_date=to_date,
        time_filter=time_filter,
    )


async def get_index_constituents(
    index: str,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    if not (index and str(index).strip()):
        return error_json(ErrorCode.VALIDATION, "index is required", hint="Example: VN30")
    gw = resolve_gateway(gateway)
    return await run_gateway_op(
        gw, "get_index_constituents", index=str(index).strip().upper()
    )


async def get_money_flow_contribution(
    index: str | None = None,
    direction: str | None = None,
    contribution_day: str | None = None,
    limit: int | None = None,
    tickers: str | list[str] | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    gw = resolve_gateway(gateway)
    return await run_gateway_op(
        gw,
        "get_money_flow_contribution",
        index=index,
        direction=direction,
        contribution_day=contribution_day,
        limit=limit,
        tickers=parse_tickers(tickers) or None,
        from_date=from_date,
        to_date=to_date,
    )


async def get_realtime_bid_ask(
    tickers: str | list[str],
    max_realtime_events: int = 1,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    parsed = parse_tickers(tickers)
    if not parsed:
        return error_json(ErrorCode.VALIDATION, "tickers is required")
    gw = resolve_gateway(gateway)
    return await run_gateway_op(
        gw,
        "get_realtime_bid_ask",
        tickers=parsed,
        max_realtime_events=max_realtime_events,
    )


# Back-compat aliases used by older tests/imports
fq_get_stock_prices = get_stock_prices
fq_get_market_statistics = get_market_statistics
fq_get_market_breadth = get_market_breadth
fq_get_index_constituents = get_index_constituents
fq_get_money_flow_contribution = get_money_flow_contribution
fq_get_realtime_bid_ask = get_realtime_bid_ask
