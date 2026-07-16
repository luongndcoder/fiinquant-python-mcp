"""Fundamental / valuation tools (official names)."""

from __future__ import annotations

from typing import Any

from fiinquant_mcp.errors import ErrorCode, error_json
from fiinquant_mcp.gateway import FiinQuantGateway
from fiinquant_mcp.tools._common import resolve_gateway, run_gateway_op
from fiinquant_mcp.tools.parsing import parse_int_list, parse_str_list, parse_tickers

_STATEMENT_TYPES = {
    "income_statement",
    "balance_sheet",
    "cashflow",
    "full",
    "note",
}


async def get_financial_ratios(
    tickers: str | list[str],
    years: str | list[int] | list[str] | None = None,
    quarters: str | list[str] | None = None,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
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


async def get_financial_statements(
    tickers: str | list[str],
    statement: str,
    years: str | list[int] | list[str] | None = None,
    quarters: str | list[str] | None = None,
    audited: bool | None = None,
    type: str | None = None,  # noqa: A002 — official param name
    fields: str | list[str] | None = None,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
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
        type=type,
        fields=parse_str_list(fields),
    )


async def get_valuation_timeseries(
    scope: str,
    tickers: str | list[str] | None = None,
    index: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    sector_level: int | None = None,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    sc = (scope or "").strip().lower()
    if sc not in {"stock", "index", "sector"}:
        return error_json(ErrorCode.VALIDATION, "scope must be stock|index|sector")
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


async def get_equity_snapshot(
    tickers: str | list[str],
    metrics: str | list[str] | None = None,
    as_of_date: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    parsed = parse_tickers(tickers)
    if not parsed:
        return error_json(ErrorCode.VALIDATION, "tickers is required")
    gw = resolve_gateway(gateway)
    return await run_gateway_op(
        gw,
        "get_equity_snapshot",
        tickers=parsed,
        metrics=parse_str_list(metrics),
        as_of_date=as_of_date,
        limit=limit,
        offset=offset,
    )


fq_get_financial_ratios = get_financial_ratios
fq_get_financial_statements = get_financial_statements
fq_get_valuation_timeseries = get_valuation_timeseries
fq_get_equity_snapshot = get_equity_snapshot
