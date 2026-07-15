"""FastMCP stdio server — P0 + P1 tools aligned with FiinQuant MCP surface."""

from __future__ import annotations

import logging

from mcp.server.fastmcp import FastMCP

from fiinquant_mcp import __version__
from fiinquant_mcp.tools import fundamental, health, market, meta, screening, universe

mcp = FastMCP("fiinquant_mcp")


def _ro(**extra: bool) -> dict:
    base = {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
    base.update(extra)
    return base


# ── Health ──────────────────────────────────────────────────────────


@mcp.tool(name="fq_ping", annotations=_ro(openWorldHint=False))
async def tool_fq_ping() -> str:
    """Health check for the personal FiinQuant MCP process (no credentials required)."""
    return await health.fq_ping()


@mcp.tool(name="fq_session_status", annotations=_ro(openWorldHint=False))
async def tool_fq_session_status() -> str:
    """Show credentials/session status and supported Gateway ops."""
    return await health.fq_session_status()


@mcp.tool(name="fq_list_ops", annotations=_ro(openWorldHint=False))
async def tool_fq_list_ops() -> str:
    """List logical Gateway operations this MCP can dispatch."""
    return await meta.fq_list_ops()


# ── Market ──────────────────────────────────────────────────────────


@mcp.tool(name="fq_get_price_history", annotations=_ro())
async def tool_fq_get_price_history(tickers: str, start: str, end: str) -> str:
    """OHLCV convenience (tickers CSV, start/end YYYY-MM-DD)."""
    return await market.fq_get_price_history(tickers, start, end)


@mcp.tool(name="fq_get_stock_prices", annotations=_ro())
async def tool_fq_get_stock_prices(
    tickers: str,
    from_date: str | None = None,
    to_date: str | None = None,
    frequency: str = "Daily",
    latest: bool = False,
    adjusted: bool = True,
) -> str:
    """Primary price tool: latest trade and/or OHLCV for stocks/indexes."""
    return await market.fq_get_stock_prices(
        tickers,
        from_date=from_date,
        to_date=to_date,
        frequency=frequency,
        latest=latest,
        adjusted=adjusted,
    )


@mcp.tool(name="fq_get_market_statistics", annotations=_ro())
async def tool_fq_get_market_statistics(
    tickers: str,
    metric: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    time_filter: str = "Daily",
) -> str:
    """Market stats (market_cap, volume/value). Prefer fq_get_stock_prices for OHLCV."""
    return await market.fq_get_market_statistics(
        tickers,
        metric=metric,
        from_date=from_date,
        to_date=to_date,
        time_filter=time_filter,
    )


@mcp.tool(name="fq_get_market_breadth", annotations=_ro())
async def tool_fq_get_market_breadth(
    index: str = "VNINDEX",
    from_date: str | None = None,
    to_date: str | None = None,
    time_filter: str = "Daily",
) -> str:
    """Index breadth: advancing / declining / unchanged."""
    return await market.fq_get_market_breadth(
        index=index,
        from_date=from_date,
        to_date=to_date,
        time_filter=time_filter,
    )


@mcp.tool(name="fq_get_index_constituents", annotations=_ro())
async def tool_fq_get_index_constituents(index: str) -> str:
    """Members of an index basket (e.g. VN30)."""
    return await market.fq_get_index_constituents(index)


@mcp.tool(name="fq_get_money_flow_contribution", annotations=_ro())
async def tool_fq_get_money_flow_contribution(
    index: str | None = None,
    direction: str | None = None,
    contribution_day: str | None = None,
    limit: int | None = None,
    tickers: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
) -> str:
    """Money-flow / index contribution ranking (topGainers, topLosers)."""
    return await market.fq_get_money_flow_contribution(
        index=index,
        direction=direction,
        contribution_day=contribution_day,
        limit=limit,
        tickers=tickers,
        from_date=from_date,
        to_date=to_date,
    )


@mcp.tool(name="fq_get_realtime_bid_ask", annotations=_ro())
async def tool_fq_get_realtime_bid_ask(
    tickers: str,
    max_realtime_events: int = 1,
) -> str:
    """Realtime bid/ask snapshot (may be empty outside market hours)."""
    return await market.fq_get_realtime_bid_ask(
        tickers, max_realtime_events=max_realtime_events
    )


# ── Universe ────────────────────────────────────────────────────────


@mcp.tool(name="fq_list_tickers", annotations=_ro())
async def tool_fq_list_tickers(market: str | None = None) -> str:
    """List tickers (optional market filter HOSE/HNX/UPCOM)."""
    return await universe.fq_list_tickers(market=market)


@mcp.tool(name="fq_ticker_info", annotations=_ro())
async def tool_fq_ticker_info(ticker: str) -> str:
    """Basic metadata for one ticker."""
    return await universe.fq_ticker_info(ticker)


@mcp.tool(name="fq_get_basic_info", annotations=_ro())
async def tool_fq_get_basic_info(tickers: str) -> str:
    """Company name, exchange, sector, ICB classification."""
    return await universe.fq_get_basic_info(tickers)


@mcp.tool(name="fq_get_icb_industries", annotations=_ro())
async def tool_fq_get_icb_industries(level: int = 2) -> str:
    """ICB industry list by level."""
    return await universe.fq_get_icb_industries(level=level)


# ── Fundamental ─────────────────────────────────────────────────────


@mcp.tool(name="fq_get_financial_ratios", annotations=_ro())
async def tool_fq_get_financial_ratios(
    tickers: str,
    years: str | None = None,
    quarters: str | None = None,
) -> str:
    """Financial ratios. years/quarters as CSV when needed."""
    return await fundamental.fq_get_financial_ratios(
        tickers, years=years, quarters=quarters
    )


@mcp.tool(name="fq_get_financial_statements", annotations=_ro())
async def tool_fq_get_financial_statements(
    tickers: str,
    statement: str,
    years: str | None = None,
    quarters: str | None = None,
    audited: bool | None = None,
) -> str:
    """BCTC: income_statement | balance_sheet | cashflow | full | note."""
    return await fundamental.fq_get_financial_statements(
        tickers,
        statement,
        years=years,
        quarters=quarters,
        audited=audited,
    )


@mcp.tool(name="fq_get_valuation_timeseries", annotations=_ro())
async def tool_fq_get_valuation_timeseries(
    scope: str,
    tickers: str | None = None,
    index: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    sector_level: int | None = None,
) -> str:
    """Valuation history; scope=stock|index|sector."""
    return await fundamental.fq_get_valuation_timeseries(
        scope,
        tickers=tickers,
        index=index,
        from_date=from_date,
        to_date=to_date,
        sector_level=sector_level,
    )


@mcp.tool(name="fq_get_equity_snapshot", annotations=_ro())
async def tool_fq_get_equity_snapshot(
    tickers: str,
    metrics: str | None = None,
    as_of_date: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> str:
    """Point-in-time snapshot (pe/pb, market_cap, liquidity, foreign room)."""
    return await fundamental.fq_get_equity_snapshot(
        tickers,
        metrics=metrics,
        as_of_date=as_of_date,
        limit=limit,
        offset=offset,
    )


# ── Screening / TA ──────────────────────────────────────────────────


@mcp.tool(name="fq_screen_stocks", annotations=_ro())
async def tool_fq_screen_stocks(
    filters: str | None = None,
    exchanges: str | None = None,
    sectors: str | None = None,
    sort_by: str | None = None,
    sort_order: str | None = None,
    limit: int | None = 50,
    screener_date: str | None = None,
    fields: str | None = None,
) -> str:
    """Stock screening. filters is JSON array string of indicator rules."""
    return await screening.fq_screen_stocks(
        filters=filters,
        exchanges=exchanges,
        sectors=sectors,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        screener_date=screener_date,
        fields=fields,
    )


@mcp.tool(name="fq_get_technical_indicators", annotations=_ro())
async def tool_fq_get_technical_indicators(
    tickers: str,
    indicators: str,
    by: str = "1d",
    lasted: bool = True,
    adjusted: bool = True,
    period: str | None = None,
) -> str:
    """TA indicators. indicators JSON e.g. [{"name":"rsi","window":14}]."""
    return await screening.fq_get_technical_indicators(
        tickers,
        indicators,
        by=by,
        lasted=lasted,
        adjusted=adjusted,
        period=period,
    )


@mcp.tool(name="fq_detect_pattern", annotations=_ro())
async def tool_fq_detect_pattern(pattern: str, params: str | None = None) -> str:
    """Pattern detection (doji, engulfing, support/resistance, …)."""
    return await screening.fq_detect_pattern(pattern, params=params)


@mcp.tool(name="fq_get_rrg_analysis", annotations=_ro())
async def tool_fq_get_rrg_analysis(
    tickers: str,
    benchmark: str = "VNINDEX",
    params: str | None = None,
) -> str:
    """Relative Rotation Graph vs benchmark."""
    return await screening.fq_get_rrg_analysis(
        tickers, benchmark=benchmark, params=params
    )


@mcp.tool(name="fq_get_rebalance", annotations=_ro())
async def tool_fq_get_rebalance(
    index: str = "VN30",
    budget: float = 1_000_000_000,
) -> str:
    """Index rebalance allocation for a cash budget."""
    return await screening.fq_get_rebalance(index=index, budget=budget)


@mcp.tool(name="fq_run_custom_analysis", annotations=_ro())
async def tool_fq_run_custom_analysis(
    analysis_id: str | None = None,
    params: str | None = None,
) -> str:
    """Run FiinQuant custom analysis; omit analysis_id to list available."""
    return await screening.fq_run_custom_analysis(
        analysis_id=analysis_id, params=params
    )


# ── Meta / escape hatch ─────────────────────────────────────────────


@mcp.tool(name="fq_search_methods", annotations=_ro())
async def tool_fq_search_methods(
    query: str,
    limit: int = 10,
    mode: str = "quick",
) -> str:
    """Discover FiinQuantX methods / screening indicators."""
    return await meta.fq_search_methods(query, limit=limit, mode=mode)


@mcp.tool(name="fq_call_method", annotations=_ro())
async def tool_fq_call_method(
    method_id: str,
    params: str | None = None,
    dry_run: bool = False,
) -> str:
    """Call a FiinQuantX method by id when no domain tool fits."""
    return await meta.fq_call_method(method_id, params=params, dry_run=dry_run)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger(__name__).info(
        "starting fiinquant_mcp v%s (stdio)",
        __version__,
    )
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
