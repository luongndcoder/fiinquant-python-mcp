"""Fundamental / valuation tools."""

from __future__ import annotations

from fiinquant_mcp.errors import ErrorCode, error_json
from fiinquant_mcp.gateway import FiinQuantGateway
from fiinquant_mcp.tools._common import resolve_gateway, run_gateway_op
from fiinquant_mcp.tools.parsing import parse_int_list, parse_jsonish, parse_str_list, parse_tickers

_STATEMENT_TYPES = {
    "income_statement",
    "balance_sheet",
    "cashflow",
    "full",
    "note",
}


async def fq_get_financial_ratios(
    tickers: str,
    years: str | None = None,
    quarters: str | None = None,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    """Financial ratios (ROE, ROA, PE, …). years/quarters optional CSV."""
    parsed = parse_tickers(tickers)
    if not parsed:
        return error_json(ErrorCode.VALIDATION, "tickers is required")
    try:
        years_list = parse_int_list(years)
        quarters_list = parse_str_list(quarters)
    except ValueError as exc:
        return error_json(ErrorCode.VALIDATION, f"invalid years/quarters: {exc}")
    gw = resolve_gateway(gateway)
    return await run_gateway_op(
        gw,
        "get_financial_ratios",
        tickers=parsed,
        years=years_list,
        quarters=quarters_list,
    )


async def fq_get_financial_statements(
    tickers: str,
    statement: str,
    years: str | None = None,
    quarters: str | None = None,
    audited: bool | None = None,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    """BCTC: income_statement | balance_sheet | cashflow | full | note."""
    parsed = parse_tickers(tickers)
    if not parsed:
        return error_json(ErrorCode.VALIDATION, "tickers is required")
    st = (statement or "").strip().lower()
    if st not in _STATEMENT_TYPES:
        return error_json(
            ErrorCode.VALIDATION,
            f"statement must be one of {sorted(_STATEMENT_TYPES)}",
        )
    try:
        years_list = parse_int_list(years)
        quarters_list = parse_str_list(quarters)
    except ValueError as exc:
        return error_json(ErrorCode.VALIDATION, f"invalid years/quarters: {exc}")
    gw = resolve_gateway(gateway)
    return await run_gateway_op(
        gw,
        "get_financial_statements",
        tickers=parsed,
        statement=st,
        years=years_list,
        quarters=quarters_list,
        audited=audited,
    )


async def fq_get_valuation_timeseries(
    scope: str,
    tickers: str | None = None,
    index: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    sector_level: int | None = None,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    """Valuation history for stock | index | sector scope."""
    sc = (scope or "").strip().lower()
    if sc not in {"stock", "index", "sector"}:
        return error_json(
            ErrorCode.VALIDATION,
            "scope must be stock|index|sector",
        )
    gw = resolve_gateway(gateway)
    return await run_gateway_op(
        gw,
        "get_valuation_timeseries",
        scope=sc,
        tickers=parse_tickers(tickers) or None,
        index=index,
        from_date=from_date,
        to_date=to_date,
        sector_level=sector_level,
    )


async def fq_get_equity_snapshot(
    tickers: str,
    metrics: str | None = None,
    as_of_date: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    """Point-in-time snapshot (pe/pb, market_cap, liquidity, foreign room, …)."""
    parsed = parse_tickers(tickers)
    if not parsed:
        return error_json(ErrorCode.VALIDATION, "tickers is required")
    metrics_list = parse_str_list(metrics)
    gw = resolve_gateway(gateway)
    return await run_gateway_op(
        gw,
        "get_equity_snapshot",
        tickers=parsed,
        metrics=metrics_list,
        as_of_date=as_of_date,
        limit=limit,
        offset=offset,
    )
