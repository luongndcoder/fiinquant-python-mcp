"""Tests for response normalize / size budget (phase 02 — expect RED until 04)."""

from __future__ import annotations

import json

from fiinquant_mcp.response import normalize_payload


def test_R1_list_of_dicts_small() -> None:
    rows = [{"t": "A", "c": 1}, {"t": "B", "c": 2}]
    out = normalize_payload(rows, max_rows=10, max_chars=10_000)
    assert out["meta"]["truncated"] is False
    assert out["meta"]["row_count"] == 2
    assert out["data"] == rows
    # must be JSON-serializable
    json.dumps(out, default=str)


def test_R2_rows_exceed_max_rows_truncated() -> None:
    rows = [{"i": i} for i in range(20)]
    out = normalize_payload(rows, max_rows=5, max_chars=50_000)
    assert out["meta"]["truncated"] is True
    assert out["meta"]["row_count"] == 20
    assert len(out["data"]) == 5


def test_R3_string_longer_than_max_chars_truncated() -> None:
    text = "x" * 500
    out = normalize_payload(text, max_rows=10, max_chars=50)
    assert out["meta"]["truncated"] is True
    assert isinstance(out["data"], str)
    assert len(out["data"]) <= 50 + 20  # allow ellipsis marker slack


def test_R4_dict_passthrough_serializable() -> None:
    out = normalize_payload({"a": 1, "b": "ok"}, max_rows=10, max_chars=1000)
    assert out["data"] == {"a": 1, "b": "ok"}
    assert out["meta"]["truncated"] is False
    json.dumps(out, default=str)
