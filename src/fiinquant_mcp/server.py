"""FastMCP stdio server — official FiinQuant tool names + personal extras."""

from __future__ import annotations

import logging
from typing import Any

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


# ═══════════════════════════════════════════════════════════════════
# Official FiinQuant MCP tool names (1:1 surface)
# ═══════════════════════════════════════════════════════════════════


@mcp.tool(name="get_stock_prices", annotations=_ro())
async def tool_get_stock_prices(
    tickers: list[str] | str,
    from_date: str | None = None,
    to_date: str | None = None,
    frequency: str = "Daily",
    latest: bool = False,
    adjusted: bool = True,
    period: str | None = None,
    fields: list[str] | str | None = None,
    output_limit: int | None = None,
    include_unclosed: bool = True,
    basket: str | None = None,
    index_members: str | None = None,
) -> str:
    """Primary source for latest traded price and OHLCV time series."""
    return await market.get_stock_prices(
        tickers,
        from_date=from_date,
        to_date=to_date,
        frequency=frequency,
        latest=latest,
        adjusted=adjusted,
        period=period,
        fields=fields,
        output_limit=output_limit,
        include_unclosed=include_unclosed,
        basket=basket,
        index_members=index_members,
    )


@mcp.tool(name="get_market_statistics", annotations=_ro())
async def tool_get_market_statistics(
    tickers: list[str] | str,
    metric: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    time_filter: str = "Daily",
) -> str:
    """Market statistics (market_cap, volume/value) — not primary price source."""
    return await market.get_market_statistics(
        tickers,
        metric=metric,
        from_date=from_date,
        to_date=to_date,
        time_filter=time_filter,
    )


@mcp.tool(name="get_market_breadth", annotations=_ro())
async def tool_get_market_breadth(
    index: str = "VNINDEX",
    from_date: str | None = None,
    to_date: str | None = None,
    time_filter: str = "Daily",
) -> str:
    """Index breadth: advancing / declining / unchanged."""
    return await market.get_market_breadth(
        index=index, from_date=from_date, to_date=to_date, time_filter=time_filter
    )


@mcp.tool(name="get_index_constituents", annotations=_ro())
async def tool_get_index_constituents(index: str) -> str:
    """Member tickers of an index basket (e.g. VN30)."""
    return await market.get_index_constituents(index)


@mcp.tool(name="get_money_flow_contribution", annotations=_ro())
async def tool_get_money_flow_contribution(
    index: str | None = None,
    direction: str | None = None,
    contribution_day: str | None = None,
    limit: int | None = None,
    tickers: list[str] | str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
) -> str:
    """Index contribution / money-flow ranking (topGainers, topLosers)."""
    return await market.get_money_flow_contribution(
        index=index,
        direction=direction,
        contribution_day=contribution_day,
        limit=limit,
        tickers=tickers,
        from_date=from_date,
        to_date=to_date,
    )


@mcp.tool(name="get_realtime_bid_ask", annotations=_ro())
async def tool_get_realtime_bid_ask(
    tickers: list[str] | str,
    max_realtime_events: int = 1,
) -> str:
    """Realtime bid/ask snapshot (may be empty outside market hours)."""
    return await market.get_realtime_bid_ask(
        tickers, max_realtime_events=max_realtime_events
    )


@mcp.tool(name="get_basic_info", annotations=_ro())
async def tool_get_basic_info(tickers: list[str] | str) -> str:
    """Company name, exchange, sector, ICB classification."""
    return await universe.get_basic_info(tickers)


@mcp.tool(name="get_icb_industries", annotations=_ro())
async def tool_get_icb_industries(level: int = 2) -> str:
    """ICB industry names by level."""
    return await universe.get_icb_industries(level=level)


@mcp.tool(name="get_financial_ratios", annotations=_ro())
async def tool_get_financial_ratios(
    tickers: list[str] | str,
    years: list[int] | str | None = None,
    quarters: list[str] | str | None = None,
) -> str:
    """FiinQuantX financial ratio rows."""
    return await fundamental.get_financial_ratios(
        tickers, years=years, quarters=quarters
    )


@mcp.tool(name="get_financial_statements", annotations=_ro())
async def tool_get_financial_statements(
    tickers: list[str] | str,
    statement: str,
    years: list[int] | str | None = None,
    quarters: list[str] | str | None = None,
    audited: bool | None = None,
    type: str | None = None,  # noqa: A002
    fields: list[str] | str | None = None,
) -> str:
    """Income statement, balance sheet, cashflow, full, or note."""
    return await fundamental.get_financial_statements(
        tickers,
        statement,
        years=years,
        quarters=quarters,
        audited=audited,
        type=type,
        fields=fields,
    )


@mcp.tool(name="get_valuation_timeseries", annotations=_ro())
async def tool_get_valuation_timeseries(
    scope: str,
    tickers: list[str] | str | None = None,
    index: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    sector_level: int | None = None,
) -> str:
    """Valuation history; scope=stock|index|sector."""
    return await fundamental.get_valuation_timeseries(
        scope,
        tickers=tickers,
        index=index,
        from_date=from_date,
        to_date=to_date,
        sector_level=sector_level,
    )


@mcp.tool(name="get_equity_snapshot", annotations=_ro())
async def tool_get_equity_snapshot(
    tickers: list[str] | str,
    metrics: list[str] | str | None = None,
    as_of_date: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> str:
    """Point-in-time snapshot (pe/pb, market_cap, liquidity, foreign room)."""
    return await fundamental.get_equity_snapshot(
        tickers,
        metrics=metrics,
        as_of_date=as_of_date,
        limit=limit,
        offset=offset,
    )


@mcp.tool(name="screen_stocks", annotations=_ro())
async def tool_screen_stocks(
    filters: list[Any] | str | None = None,
    exchanges: list[str] | str | None = None,
    sectors: list[str] | str | None = None,
    sort_by: str | None = None,
    sort_order: str | None = None,
    limit: int | None = 50,
    screener_date: str | None = None,
    fields: list[str] | str | None = None,
) -> str:
    """Screen stocks using StockScreening-style filters."""
    return await screening.screen_stocks(
        filters=filters,
        exchanges=exchanges,
        sectors=sectors,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        screener_date=screener_date,
        fields=fields,
    )


@mcp.tool(name="get_technical_indicators", annotations=_ro())
async def tool_get_technical_indicators(
    tickers: list[str] | str,
    indicators: list[Any] | str,
    by: str = "1d",
    lasted: bool = True,
    adjusted: bool = True,
    period: str | None = None,
) -> str:
    """FiinIndicator values (RSI, MACD, SMA, EMA, …)."""
    return await screening.get_technical_indicators(
        tickers,
        indicators,
        by=by,
        lasted=lasted,
        adjusted=adjusted,
        period=period,
    )


@mcp.tool(name="detect_pattern", annotations=_ro())
async def tool_detect_pattern(
    pattern: str,
    params: dict[str, Any] | str | None = None,
) -> str:
    """Pattern method (doji, engulfing, support/resistance, …)."""
    return await screening.detect_pattern(pattern, params=params)


@mcp.tool(name="get_rrg_analysis", annotations=_ro())
async def tool_get_rrg_analysis(
    tickers: list[str] | str,
    benchmark: str = "VNINDEX",
    params: dict[str, Any] | str | None = None,
) -> str:
    """Relative Rotation Graph vs benchmark."""
    return await screening.get_rrg_analysis(
        tickers, benchmark=benchmark, params=params
    )


@mcp.tool(name="get_rebalance", annotations=_ro())
async def tool_get_rebalance(
    index: str = "VN30",
    budget: float = 1_000_000_000,
) -> str:
    """Index rebalance allocation for a budget."""
    return await screening.get_rebalance(index=index, budget=budget)


@mcp.tool(name="run_custom_analysis", annotations=_ro())
async def tool_run_custom_analysis(
    analysis_id: str | None = None,
    params: dict[str, Any] | str | None = None,
) -> str:
    """Run declared custom analyses; omit analysis_id to list available."""
    return await screening.run_custom_analysis(
        analysis_id=analysis_id, params=params
    )


@mcp.tool(name="fiinquantx_search_methods", annotations=_ro())
async def tool_fiinquantx_search_methods(
    query: str,
    limit: int = 10,
    mode: str = "quick",
) -> str:
    """Discover FiinQuantX methods / screening indicators."""
    return await meta.fiinquantx_search_methods(query, limit=limit, mode=mode)


@mcp.tool(name="fiinquantx_call_method", annotations=_ro())
async def tool_fiinquantx_call_method(
    method_id: str,
    params: dict[str, Any] | str | None = None,
    dry_run: bool = False,
) -> str:
    """Call a registered FiinQuantX method by id (escape hatch)."""
    return await meta.fiinquantx_call_method(
        method_id, params=params, dry_run=dry_run
    )


@mcp.tool(name="report_issue", annotations=_ro(openWorldHint=False))
async def tool_report_issue(
    user_question: str,
    claude_issue: str,
    tool_name: str = "",
    kind: str = "bug",
    severity: str = "medium",
    expected: str = "",
    actual: str = "",
    details: str = "",
) -> str:
    """Report MCP/provider issue (local log only on personal MCP)."""
    return await meta.report_issue(
        user_question,
        claude_issue,
        tool_name=tool_name,
        kind=kind,
        severity=severity,
        expected=expected,
        actual=actual,
        details=details,
    )


# ═══════════════════════════════════════════════════════════════════
# Personal extras (keep — reliability / convenience)
# ═══════════════════════════════════════════════════════════════════


@mcp.tool(name="fq_ping", annotations=_ro(openWorldHint=False))
async def tool_fq_ping() -> str:
    """[extra] Health check — no credentials required."""
    return await health.fq_ping()


@mcp.tool(name="fq_session_status", annotations=_ro(openWorldHint=False))
async def tool_fq_session_status() -> str:
    """[extra] Credentials, session, free-tier plan limits."""
    return await health.fq_session_status()


@mcp.tool(name="fq_list_ops", annotations=_ro(openWorldHint=False))
async def tool_fq_list_ops() -> str:
    """[extra] List Gateway logical operations."""
    return await meta.fq_list_ops()


@mcp.tool(name="fq_get_price_history", annotations=_ro())
async def tool_fq_get_price_history(
    tickers: list[str] | str,
    start: str,
    end: str,
) -> str:
    """[extra] Simple OHLCV helper (start/end). Prefer get_stock_prices for full API."""
    return await market.fq_get_price_history(tickers, start, end)


@mcp.tool(name="fq_list_tickers", annotations=_ro())
async def tool_fq_list_tickers(market: str | None = None) -> str:
    """[extra] List tickers by market (HOSE/HNX/UPCOM)."""
    return await universe.fq_list_tickers(market=market)


@mcp.tool(name="fq_ticker_info", annotations=_ro())
async def tool_fq_ticker_info(ticker: str) -> str:
    """[extra] Basic metadata for one ticker."""
    return await universe.fq_ticker_info(ticker)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger(__name__).info(
        "starting fiinquant_mcp v%s (stdio) — official names + extras",
        __version__,
    )
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
