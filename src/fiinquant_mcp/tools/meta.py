"""Discovery / escape-hatch tools for FiinQuantX methods."""

from __future__ import annotations

from fiinquant_mcp.errors import ErrorCode, error_json, success_json
from fiinquant_mcp.gateway import FiinQuantGateway
from fiinquant_mcp.ops import SUPPORTED_OPS
from fiinquant_mcp.tools._common import resolve_gateway, run_gateway_op
from fiinquant_mcp.tools.parsing import parse_jsonish


async def fq_list_ops(
    gateway: FiinQuantGateway | None = None,
) -> str:
    """List logical ops this MCP Gateway supports (no network)."""
    _ = gateway  # unused; kept for signature consistency
    return success_json(
        {
            "ops": list(SUPPORTED_OPS),
            "count": len(SUPPORTED_OPS),
        }
    )


async def fq_search_methods(
    query: str,
    limit: int = 10,
    mode: str = "quick",
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    """Discover FiinQuantX methods / screening indicators (if SDK exposes)."""
    if not (query and query.strip()):
        return error_json(ErrorCode.VALIDATION, "query is required")
    gw = resolve_gateway(gateway)
    return await run_gateway_op(
        gw,
        "search_methods",
        query=query.strip(),
        limit=limit,
        mode=mode,
    )


async def fq_call_method(
    method_id: str,
    params: str | None = None,
    dry_run: bool = False,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    """Call a registered FiinQuantX method by id (escape hatch)."""
    if not (method_id and method_id.strip()):
        return error_json(ErrorCode.VALIDATION, "method_id is required")
    try:
        params_obj = parse_jsonish(params) or {}
    except Exception as exc:  # noqa: BLE001
        return error_json(ErrorCode.VALIDATION, f"params must be valid JSON: {exc}")
    if dry_run:
        return success_json(
            {
                "dry_run": True,
                "method_id": method_id.strip(),
                "params": params_obj,
            }
        )
    gw = resolve_gateway(gateway)
    return await run_gateway_op(
        gw,
        "call_method",
        method_id=method_id.strip(),
        params=params_obj,
        dry_run=False,
    )
