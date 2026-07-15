"""Structured error / success JSON envelopes for MCP tool responses."""

from __future__ import annotations

import json
from enum import Enum
from typing import Any


class ErrorCode(str, Enum):
    AUTH = "AUTH"
    TIMEOUT = "TIMEOUT"
    SDK_ERROR = "SDK_ERROR"
    VALIDATION = "VALIDATION"
    INTERNAL = "INTERNAL"


class GatewayError(Exception):
    """Domain error raised by the Gateway; tools map it to JSON envelopes."""

    def __init__(
        self,
        code: ErrorCode | str,
        message: str,
        *,
        hint: str | None = None,
    ) -> None:
        if isinstance(code, ErrorCode):
            self.code = code
        else:
            try:
                self.code = ErrorCode(code)
            except ValueError:
                # Preserve unknown codes as string-like via INTERNAL with original in message
                # Tests allow CUSTOM_CODE via error_json directly; Gateway uses known codes.
                self.code = code  # type: ignore[assignment]
        self.message = message
        self.hint = hint
        super().__init__(message)


def _code_str(code: ErrorCode | str) -> str:
    if isinstance(code, ErrorCode):
        return code.value
    return str(code)


def error_json(
    code: ErrorCode | str,
    message: str,
    *,
    hint: str | None = None,
) -> str:
    """Serialize a failed tool response."""
    payload: dict[str, Any] = {
        "ok": False,
        "code": _code_str(code),
        "message": message,
    }
    if hint is not None:
        payload["hint"] = hint
    return json.dumps(payload, ensure_ascii=False, default=str)


def success_json(data: Any, *, meta: dict[str, Any] | None = None) -> str:
    """Serialize a successful tool response."""
    payload: dict[str, Any] = {"ok": True, "data": data}
    if meta is not None:
        payload["meta"] = meta
    return json.dumps(payload, ensure_ascii=False, default=str)


def error_envelope(
    code: ErrorCode | str,
    message: str,
    *,
    hint: str | None = None,
) -> dict[str, Any]:
    """Dict form of error envelope (tests / internal)."""
    out: dict[str, Any] = {
        "ok": False,
        "code": _code_str(code),
        "message": message,
    }
    if hint is not None:
        out["hint"] = hint
    return out
