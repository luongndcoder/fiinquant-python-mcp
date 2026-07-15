"""P0 health tools (phase 05 — RED until 07)."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from fiinquant_mcp.tools.health import fq_ping, fq_session_status


@pytest.mark.asyncio
async def test_T1_fq_ping_ok() -> None:
    gw = MagicMock()
    gw.is_logged_in = False
    gw.settings = MagicMock(has_credentials=True, timeout_s=30)
    raw = await fq_ping(gateway=gw)
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert payload["data"]["status"] == "ok"


@pytest.mark.asyncio
async def test_T1b_fq_session_status_reflects_gateway() -> None:
    gw = MagicMock()
    gw.session_status.return_value = {
        "logged_in": True,
        "has_credentials": True,
        "timeout_s": 30,
    }
    raw = await fq_session_status(gateway=gw)
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert payload["data"]["logged_in"] is True
