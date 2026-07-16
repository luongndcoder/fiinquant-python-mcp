"""Discovery / escape-hatch tools (official + personal extras)."""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any

from fiinquant_mcp.errors import ErrorCode, error_json, success_json
from fiinquant_mcp.gateway import FiinQuantGateway
from fiinquant_mcp.ops import SUPPORTED_OPS
from fiinquant_mcp.tools._common import resolve_gateway, run_gateway_op
from fiinquant_mcp.tools.parsing import parse_jsonish

logger = logging.getLogger(__name__)


async def fq_list_ops(
    gateway: FiinQuantGateway | None = None,
) -> str:
    """Personal extra: list logical Gateway ops."""
    _ = gateway
    return success_json({"ops": list(SUPPORTED_OPS), "count": len(SUPPORTED_OPS)})


async def fiinquantx_search_methods(
    query: str,
    limit: int = 10,
    mode: str = "quick",
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    if not (query and str(query).strip()):
        return error_json(ErrorCode.VALIDATION, "query is required")
    gw = resolve_gateway(gateway)
    return await run_gateway_op(
        gw,
        "search_methods",
        query=str(query).strip(),
        limit=limit,
        mode=mode,
    )


async def fiinquantx_call_method(
    method_id: str,
    params: str | dict[str, Any] | None = None,
    dry_run: bool = False,
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    if not (method_id and str(method_id).strip()):
        return error_json(ErrorCode.VALIDATION, "method_id is required")
    try:
        params_obj = parse_jsonish(params) or {}
    except Exception as exc:  # noqa: BLE001
        return error_json(ErrorCode.VALIDATION, f"params must be valid JSON: {exc}")
    if dry_run:
        return success_json(
            {
                "dry_run": True,
                "method_id": str(method_id).strip(),
                "params": params_obj,
            }
        )
    gw = resolve_gateway(gateway)
    return await run_gateway_op(
        gw,
        "call_method",
        method_id=str(method_id).strip(),
        params=params_obj,
        dry_run=False,
    )


async def report_issue(
    user_question: str,
    claude_issue: str,
    tool_name: str = "",
    kind: str = "bug",
    severity: str = "medium",
    expected: str = "",
    actual: str = "",
    details: str = "",
    *,
    gateway: FiinQuantGateway | None = None,
) -> str:
    """Official tool name — local capture only (no FiinQuant admin upload)."""
    _ = gateway
    if not (user_question and str(user_question).strip()):
        return error_json(ErrorCode.VALIDATION, "user_question is required")
    if not (claude_issue and str(claude_issue).strip()):
        return error_json(ErrorCode.VALIDATION, "claude_issue is required")
    issue_id = f"local-{uuid.uuid4().hex[:12]}"
    payload = {
        "issue_id": issue_id,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "kind": kind,
        "severity": severity,
        "tool_name": tool_name,
        "user_question": user_question,
        "claude_issue": claude_issue,
        "expected": expected,
        "actual": actual,
        "details": details,
        "delivery": "local_log_only",
        "note": (
            "Personal MCP does not upload to FiinQuant admins. "
            "Issue logged on stderr for local debugging."
        ),
    }
    logger.warning("report_issue %s", payload)
    return success_json(payload)


# aliases
fq_search_methods = fiinquantx_search_methods
fq_call_method = fiinquantx_call_method
