"""Tests for structured error / success envelopes (phase 02 — expect RED until 04)."""

from __future__ import annotations

import json

import pytest

from fiinquant_mcp.errors import ErrorCode, error_envelope, error_json, success_json


def test_E1_error_envelope_timeout_has_stable_keys() -> None:
    raw = error_json(ErrorCode.TIMEOUT, "call exceeded budget", hint="retry with smaller range")
    payload = json.loads(raw)
    assert payload["ok"] is False
    assert payload["code"] == "TIMEOUT"
    assert payload["message"] == "call exceeded budget"
    assert payload["hint"] == "retry with smaller range"


def test_E2_success_json_shape() -> None:
    raw = success_json({"rows": [1]}, meta={"truncated": False, "row_count": 1})
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert payload["data"] == {"rows": [1]}
    assert payload["meta"]["row_count"] == 1
    assert payload["meta"]["truncated"] is False


def test_E3_unknown_code_still_serializable() -> None:
    raw = error_json("CUSTOM_CODE", "something odd")
    payload = json.loads(raw)
    assert payload["ok"] is False
    assert payload["code"] == "CUSTOM_CODE"
    assert "message" in payload


def test_E1b_error_envelope_dict_form() -> None:
    env = error_envelope(ErrorCode.AUTH, "missing credentials", hint="set FIINQUANT_USERNAME")
    assert env["ok"] is False
    assert env["code"] == "AUTH"
    assert env["hint"].startswith("set FIINQUANT")
