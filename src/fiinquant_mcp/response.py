"""Normalize and size-budget SDK payloads for LLM-friendly MCP responses."""

from __future__ import annotations

import json
from typing import Any


def normalize_payload(
    obj: Any,
    *,
    max_rows: int = 500,
    max_chars: int = 80_000,
) -> dict[str, Any]:
    """Convert *obj* into a JSON-serializable structure with size budgets.

    Returns::

        {"data": <payload>, "meta": {"truncated": bool, "row_count": int | None}}
    """
    truncated = False
    row_count: int | None = None

    # Optional pandas DataFrame support (duck-typed)
    if type(obj).__name__ == "DataFrame" and hasattr(obj, "to_dict"):
        try:
            n = len(obj)
            row_count = n
            frame = obj
            if n > max_rows:
                frame = obj.iloc[:max_rows]
                truncated = True
            records = frame.to_dict(orient="records")
            return _budget_chars(
                {
                    "data": records,
                    "meta": {"truncated": truncated, "row_count": row_count},
                },
                max_chars=max_chars,
            )
        except Exception:
            obj = str(obj)

    if isinstance(obj, list):
        row_count = len(obj)
        data: Any = obj
        if len(obj) > max_rows:
            data = obj[:max_rows]
            truncated = True
        result = {
            "data": data,
            "meta": {"truncated": truncated, "row_count": row_count},
        }
        return _budget_chars(result, max_chars=max_chars)

    if isinstance(obj, dict):
        result = {
            "data": obj,
            "meta": {"truncated": False, "row_count": None},
        }
        return _budget_chars(result, max_chars=max_chars)

    # Fallback: string / other
    text = obj if isinstance(obj, str) else str(obj)
    if len(text) > max_chars:
        # Keep total length within max_chars including marker
        marker = "…[truncated]"
        keep = max(0, max_chars - len(marker))
        text = text[:keep] + marker
        truncated = True
    return {
        "data": text,
        "meta": {"truncated": truncated, "row_count": None},
    }


def _budget_chars(result: dict[str, Any], *, max_chars: int) -> dict[str, Any]:
    """If serialized size exceeds max_chars, shrink list data or stringify."""
    raw = json.dumps(result, ensure_ascii=False, default=str)
    if len(raw) <= max_chars:
        return result

    data = result.get("data")
    meta = dict(result.get("meta") or {})
    meta["truncated"] = True

    if isinstance(data, list) and data:
        lo, hi = 1, len(data)
        best: list[Any] = data[:1]
        while lo <= hi:
            mid = (lo + hi) // 2
            candidate = data[:mid]
            trial = json.dumps(
                {"data": candidate, "meta": meta},
                ensure_ascii=False,
                default=str,
            )
            if len(trial) <= max_chars:
                best = candidate
                lo = mid + 1
            else:
                hi = mid - 1
        return {"data": best, "meta": meta}

    text = json.dumps(data, ensure_ascii=False, default=str)
    marker = "…[truncated]"
    if len(text) > max_chars:
        keep = max(0, max_chars - len(marker))
        text = text[:keep] + marker
    return {"data": text, "meta": meta}
