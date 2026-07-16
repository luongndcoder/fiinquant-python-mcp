"""Screening and technical analysis tools (official names)."""

from __future__ import annotations

from typing import Any

from fiinquant_mcp.errors import ErrorCode, error_json
from fiinquant_mcp.gateway import FiinQuantGateway
from fiinquant_mcp.tools._common import resolve_gateway, run_gateway_op
from fiinquant_mcp.tools.parsing import parse_jsonish, parse_str_list, parse_tickers


async def screen_stocks(
    filters: str | list[Any] | dict[str, Any] | None = None,
    exchanges: str | list[str] | None = None,
    sectors: str | list[str] | None = None,
    sort_by: str | None = None,
    sort_order: str | None = None,
    limit: int | None = 50,
    screener_date: str | None = None,
    fields: str | list[str] | None = None,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    try:
        filters_obj = parse_jsonish(filters)
    except Exception as exc:  # noqa: BLE001
        return error_json(
            ErrorCode.VALIDATION,
            f"filters must be valid JSON/list: {exc}",
            hint='Example: [{"indicator":"roe","operator":"gt","value":15}]',
        )
    if limit is not None and limit > 200:
        limit = 200
    gw = resolve_gateway(gateway)
    return await run_gateway_op(
        gw,
        "screen_stocks",
        filters=filters_obj,
        exchanges=parse_str_list(exchanges),
        sectors=parse_str_list(sectors),
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        screener_date=screener_date,
        fields=parse_str_list(fields),
    )


async def get_technical_indicators(
    tickers: str | list[str],
    indicators: str | list[Any] | dict[str, Any],
    by: str = "1d",
    lasted: bool = True,
    adjusted: bool = True,
    period: str | None = None,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    parsed = parse_tickers(tickers)
    if not parsed:
        return error_json(ErrorCode.VALIDATION, "tickers is required")
    try:
        indicators_obj = parse_jsonish(indicators)
    except Exception as exc:  # noqa: BLE001
        return error_json(
            ErrorCode.VALIDATION,
            f"indicators must be valid JSON/list: {exc}",
            hint='Example: [{"name":"rsi","window":14}]',
        )
    if not indicators_obj:
        return error_json(ErrorCode.VALIDATION, "indicators is required")
    gw = resolve_gateway(gateway)
    return await run_gateway_op(
        gw,
        "get_technical_indicators",
        tickers=parsed,
        indicators=indicators_obj,
        by=by,
        lasted=lasted,
        adjusted=adjusted,
        period=period,
    )


async def detect_pattern(
    pattern: str,
    params: str | dict[str, Any] | None = None,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    if not (pattern and str(pattern).strip()):
        return error_json(ErrorCode.VALIDATION, "pattern is required")
    try:
        params_obj = parse_jsonish(params) or {}
    except Exception as exc:  # noqa: BLE001
        return error_json(ErrorCode.VALIDATION, f"params must be valid JSON: {exc}")
    gw = resolve_gateway(gateway)
    return await run_gateway_op(
        gw,
        "detect_pattern",
        pattern=str(pattern).strip(),
        params=params_obj,
    )


async def get_rrg_analysis(
    tickers: str | list[str],
    benchmark: str = "VNINDEX",
    params: str | dict[str, Any] | None = None,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    parsed = parse_tickers(tickers)
    if not parsed:
        return error_json(ErrorCode.VALIDATION, "tickers is required")
    try:
        params_obj = parse_jsonish(params)
    except Exception as exc:  # noqa: BLE001
        return error_json(ErrorCode.VALIDATION, f"params must be valid JSON: {exc}")
    gw = resolve_gateway(gateway)
    return await run_gateway_op(
        gw,
        "get_rrg_analysis",
        tickers=parsed,
        benchmark=benchmark,
        params=params_obj,
    )


async def get_rebalance(
    index: str = "VN30",
    budget: float = 1_000_000_000,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    gw = resolve_gateway(gateway)
    return await run_gateway_op(gw, "get_rebalance", index=index, budget=budget)


async def run_custom_analysis(
    analysis_id: str | None = None,
    params: str | dict[str, Any] | None = None,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    try:
        params_obj = parse_jsonish(params)
    except Exception as exc:  # noqa: BLE001
        return error_json(ErrorCode.VALIDATION, f"params must be valid JSON: {exc}")
    gw = resolve_gateway(gateway)
    return await run_gateway_op(
        gw,
        "run_custom_analysis",
        analysis_id=analysis_id,
        params=params_obj,
    )


fq_screen_stocks = screen_stocks
fq_get_technical_indicators = get_technical_indicators
fq_detect_pattern = detect_pattern
fq_get_rrg_analysis = get_rrg_analysis
fq_get_rebalance = get_rebalance
fq_run_custom_analysis = run_custom_analysis
