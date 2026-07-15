"""Shared helpers for tool handlers."""

from __future__ import annotations

from typing import Any

from fiinquant_mcp.config import Settings, load_settings
from fiinquant_mcp.errors import ErrorCode, GatewayError, error_json, success_json
from fiinquant_mcp.gateway import FiinQuantGateway
from fiinquant_mcp.response import normalize_payload
from fiinquant_mcp.sdk_client import default_client_factory

_gateway: FiinQuantGateway | None = None


def get_default_gateway() -> FiinQuantGateway:
    global _gateway
    if _gateway is None:
        settings = load_settings()
        _gateway = FiinQuantGateway(settings, client_factory=default_client_factory)
    return _gateway


def resolve_gateway(gateway: FiinQuantGateway | None) -> FiinQuantGateway:
    return gateway if gateway is not None else get_default_gateway()


def settings_of(gateway: FiinQuantGateway) -> Settings:
    return gateway.settings


async def run_gateway_op(
    gateway: FiinQuantGateway,
    op: str,
    **kwargs: Any,
) -> str:
    """Call gateway, normalize payload, return JSON string envelope."""
    try:
        raw = await gateway.call(op, **kwargs)
        s = settings_of(gateway)
        normalized = normalize_payload(
            raw,
            max_rows=s.max_rows,
            max_chars=s.max_chars,
        )
        return success_json(normalized["data"], meta=normalized["meta"])
    except GatewayError as exc:
        return error_json(exc.code, exc.message, hint=exc.hint)
    except Exception as exc:  # noqa: BLE001
        return error_json(
            ErrorCode.INTERNAL,
            str(exc),
            hint="Unexpected tool failure",
        )
