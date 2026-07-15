"""Health / session tools."""

from __future__ import annotations

from fiinquant_mcp.errors import ErrorCode, error_json, success_json
from fiinquant_mcp.gateway import FiinQuantGateway
from fiinquant_mcp.tools._common import resolve_gateway


async def fq_ping(gateway: FiinQuantGateway | None = None) -> str:
    """Liveness check — does not require FiinQuant session."""
    try:
        resolve_gateway(gateway)
        return success_json({"status": "ok", "service": "fiinquant_mcp"})
    except Exception as exc:  # noqa: BLE001
        return error_json(ErrorCode.INTERNAL, str(exc))


async def fq_session_status(gateway: FiinQuantGateway | None = None) -> str:
    """Return Gateway session status (no secrets)."""
    try:
        gw = resolve_gateway(gateway)
        return success_json(gw.session_status())
    except Exception as exc:  # noqa: BLE001
        return error_json(ErrorCode.INTERNAL, str(exc))
