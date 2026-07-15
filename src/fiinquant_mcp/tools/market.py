"""Market / price / breadth tools."""

from __future__ import annotations

from fiinquant_mcp.errors import ErrorCode, error_json
from fiinquant_mcp.gateway import FiinQuantGateway
from fiinquant_mcp.tools._common import resolve_gateway, run_gateway_op
from fiinquant_mcp.tools.parsing import parse_str_list, parse_tickers


async def fq_get_price_history(
    tickers: str,
    start: str,
    end: str,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    """Fetch OHLCV / price history (P0 convenience wrapper)."""
    parsed = parse_tickers(tickers)
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


async def fq_get_stock_prices(
    tickers: str,
    from_date: str | None = None,
    to_date: str | None = None,
    frequency: str = "Daily",
    latest: bool = False,
    adjusted: bool = True,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    """Primary price source: latest trade and/or OHLCV series (stocks/indexes)."""
    parsed = parse_tickers(tickers)
    if not parsed:
        return error_json(
            ErrorCode.VALIDATION,
            "tickers is required",
            hint="Example: FPT,VNM or VNINDEX",
        )
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
    )


async def fq_get_market_statistics(
    tickers: str,
    metric: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    time_filter: str = "Daily",
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    """Market statistics (market_cap, volume/value) — not primary price source."""
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


async def fq_get_market_breadth(
    index: str = "VNINDEX",
    from_date: str | None = None,
    to_date: str | None = None,
    time_filter: str = "Daily",
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    """Advancing/declining/unchanged breadth for an index."""
    gw = resolve_gateway(gateway)
    return await run_gateway_op(
        gw,
        "get_market_breadth",
        index=index,
        from_date=from_date,
        to_date=to_date,
        time_filter=time_filter,
    )


async def fq_get_index_constituents(
    index: str,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    """Member tickers of an index/basket (e.g. VN30)."""
    if not (index and index.strip()):
        return error_json(ErrorCode.VALIDATION, "index is required", hint="Example: VN30")
    gw = resolve_gateway(gateway)
    return await run_gateway_op(gw, "get_index_constituents", index=index.strip().upper())


async def fq_get_money_flow_contribution(
    index: str | None = None,
    direction: str | None = None,
    contribution_day: str | None = None,
    limit: int | None = None,
    tickers: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    """Index contribution / money-flow ranking (topGainers / topLosers)."""
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


async def fq_get_realtime_bid_ask(
    tickers: str,
    max_realtime_events: int = 1,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    """Bounded realtime bid/ask snapshot (may be empty outside session)."""
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
