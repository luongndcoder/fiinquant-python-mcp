---
title: "Personal FiinQuant MCP — Resilient Facade"
description: "Build personal stdio MCP over working fiinquant SDK with Gateway reliability kit and phased domain tools"
status: shipped-p0
priority: P0
effort: 2-3d
branch: main
tags: [mcp, fiinquant, python, fastmcp, personal]
blockedBy: []
blocks: []
created: 2026-07-15
lane: normal
intake_warning: "intake.md missing — falling back to lane=normal"
---

# Personal FiinQuant MCP — Implementation Plan

## Chosen Approach

**Option B — Resilient facade + domain tools** (approved in brainstorm 2026-07-15)

- Data plane: official/private **`fiinquant` Python SDK** (đã proven ngoài MCP)
- Control plane: FastMCP **stdio** cho Claude Desktop / Cursor
- Reliability: session Gateway, hard timeout, error envelope, response size budget, health tools
- Tool surface: đa dạng ~ parity official MCP, **phased** (P0 core → P1 expand)

**Brainstorm:** [brainstorm.md](./brainstorm.md)

## Overview

Greenfield repo. Thay MCP official không tin cậy bằng server personal: wrap SDK ổn định, tool fail không kill process, response LLM-friendly, config `mcp.json` local.

**Không làm v1:** remote HTTP/SSE, multi-user auth, cache distributed, reverse-engineer HTTP thay SDK, publish data FiinQuant ra public.

## Constraints (đã chốt)

| Item | Value |
|------|--------|
| Host | Claude Desktop / Cursor, **stdio** |
| Pain | Runtime reliability (crash/hang/timeout) |
| Surface | Đa dạng tool ~ official |
| SDK | `fiinquant` works outside MCP; **không có trên PyPI public** → private wheel / vendor path |
| Docs ref | https://fiinquant.vn/Home/Document (inventory tool; client HTTP không rewrite) |

## Architecture

```
┌─────────────────────────────────────────────┐
│  Claude Desktop / Cursor (MCP client)       │
└──────────────────┬──────────────────────────┘
                   │ stdio JSON-RPC
┌──────────────────▼──────────────────────────┐
│  FastMCP server (fiinquant_mcp)             │
│  tools/*  →  presentation + Pydantic IO     │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│  Gateway (single session owner)             │
│  login / re-auth / timeout / to_thread      │
│  error map / never uncaught                 │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│  fiinquant SDK (private package)            │
└─────────────────────────────────────────────┘
```

### Package layout (target)

```
fiinquant-python-mcp/
├── pyproject.toml
├── README.md
├── .env.example
├── config/
│   └── mcp.example.json
├── src/fiinquant_mcp/
│   ├── __init__.py
│   ├── __main__.py          # python -m fiinquant_mcp
│   ├── server.py            # FastMCP app + tool registration
│   ├── config.py            # env: credentials, timeouts, size limits
│   ├── gateway.py           # FiinQuantGateway
│   ├── errors.py            # error codes + envelope helpers
│   ├── response.py          # serialize DF/dict, truncate, format
│   └── tools/
│       ├── __init__.py
│       ├── health.py        # ping, session_status
│       ├── market.py        # OHLCV / price (P0)
│       ├── universe.py      # tickers / metadata (P0)
│       ├── fundamental.py   # BCTC / ratios (P1)
│       └── screening.py     # filters (P1)
└── tests/
    ├── conftest.py
    ├── test_config.py
    ├── test_gateway.py
    ├── test_response.py
    ├── test_errors.py
    └── test_tools_*.py
```

### Error envelope (contract)

Mọi tool trả **string JSON** (FastMCP-friendly):

```json
{"ok": true, "data": {}, "meta": {"truncated": false, "row_count": 0}}
```

```json
{"ok": false, "code": "TIMEOUT|AUTH|SDK_ERROR|VALIDATION|INTERNAL", "message": "...", "hint": "..."}
```

Process **không** exit vì tool error.

## Scope challenge

| Keep in plan | Defer |
|--------------|--------|
| Scaffold + Gateway + response policy | Full parity 1:1 every official tool day-1 |
| P0: health + market + universe | Fundamental/screening full depth |
| Unit tests mock SDK | Live e2e (manual / optional) |
| mcp.example.json + README | Remote deploy, Docker, CI publish |
| SDK adapter interface | Rewrite HTTP client from Document |

**Blast radius:** greenfield — chỉ files trong repo; không đụng system khác.

## Phases (TDD ordering)

| Phase | Name | Type | Status |
|-------|------|------|--------|
| 01 | [Project scaffold](./phase-01-scaffold.md) | setup | ✅ Done (2026-07-15) |
| 02 | [Tests — Gateway + response + errors](./phase-02-test-gateway.md) | test (red) | ✅ Done RED (2026-07-15) |
| 03 | [Test review gate — Gateway](./phase-03-test-review-gateway.md) | **user gate** | ✅ Approved (2026-07-15) |
| 04 | [Implement Gateway + core](./phase-04-impl-gateway.md) | impl | ✅ Done (2026-07-15) |
| 05 | [Tests — P0 tools](./phase-05-test-tools-p0.md) | test (red) | ✅ Done RED (2026-07-15) |
| 06 | [Test review gate — P0 tools](./phase-06-test-review-tools-p0.md) | **user gate** | ✅ Approved (2026-07-15) |
| 07 | [Implement P0 tools + server entry](./phase-07-impl-tools-p0.md) | impl | ✅ Done (2026-07-15) |
| 08 | [Docs, mcp config, live smoke](./phase-08-docs-smoke.md) | docs/verify | ✅ Docs done; live smoke = user |
| 09 | [P1 domain expand](./phase-09-p1-expand.md) | later | ✅ Done v0.2.0 (2026-07-15) |

## Dependencies

| Dep | Role | Note |
|-----|------|------|
| `mcp[cli]` / FastMCP | MCP server | pin version in pyproject |
| `pydantic` v2 | input models | via mcp often |
| `fiinquant` | data | **private** — document install path in README |
| `pytest`, `pytest-asyncio` | tests | dev deps |
| `python-dotenv` | optional local env | optional |

**Pre-ship user action:** cung cấp cách cài `fiinquant` (wheel path / private index / `pip install` internal). Plan không assume PyPI public (đã verify: package không có trên pypi.org).

## Test Plan

### Test Strategy

- **Type:** Unit (primary) + 1 optional live smoke script
- **Coverage target:** ≥70% on `gateway`, `response`, `errors`, P0 tools
- **Runner:** pytest + pytest-asyncio
- **Boundary:** mock toàn bộ SDK tại Gateway boundary — **không** call network trong unit tests

### Test Cases (outline)

| # | Unit | Scenario | Expected | Priority |
|---|------|----------|----------|----------|
| G1 | `Gateway.ensure_session` | credentials missing | `AUTH` envelope / raises mapped error | P0 |
| G2 | `Gateway.call` | SDK success | returns data | P0 |
| G3 | `Gateway.call` | SDK raises | `SDK_ERROR`, process continues | P0 |
| G4 | `Gateway.call` | slow SDK > timeout | `TIMEOUT` | P0 |
| G5 | `Gateway.call` | session expired then success | re-auth once, success | P0 |
| R1 | `response.serialize` | DataFrame-like list | JSON ok, row_count set | P0 |
| R2 | `response.serialize` | rows > max_rows | truncated=true, data capped | P0 |
| R3 | `response.serialize` | non-JSON type | coerced or INTERNAL | P0 |
| E1 | `errors.envelope` | known code | stable JSON schema | P0 |
| T1 | `fiinquant_ping` | gateway ok | ok=true | P0 |
| T2 | `get_ohlcv` (name TBD) | valid tickers | ok + data | P0 |
| T3 | `get_ohlcv` | gateway TIMEOUT | ok=false TIMEOUT | P0 |
| T4 | tool validation | bad ticker empty | VALIDATION | P0 |

### Mock Dependencies

- Fake `FiinQuantClient` / module with methods user maps in Gateway
- `AsyncMock` / thread-side sync mock for timeout tests (`time.sleep`)
- Env fixture: set/clear `FIINQUANT_*` vars

### Test Data

- Sample OHLCV rows (3–5 bars)
- Oversized table fixture (max_rows+10) for truncate

### Prerequisites

- `tests/conftest.py`: gateway factory, env monkeypatch
- No real credentials in repo

## Evaluation Rubric

```yaml
rubric: general-code
rubric_version: 1
notes: |
  Emphasis: reliability (timeout/error envelope), no secrets in logs,
  tool isolation, response size budget, TDD gate compliance.
```

## Risks

| Risk | Mitigation |
|------|------------|
| SDK API surface unknown in-repo | Phase 01 includes **SDK inventory script** on user's installed package; map methods → tools |
| `fiinquant` not on PyPI | README + optional `FIINQUANT_SDK_PATH`; pyproject dependency optional/extra |
| Sync SDK blocks event loop | `asyncio.to_thread` + timeout |
| Tool name drift vs official | P1 align names after inventory; P0 stable own names with prefix `fq_` |
| Document site fetch blocked | Inventory from local SDK + user-provided doc screenshots/PDF if needed |

## Success criteria (plan-level)

1. `pytest` green offline (no network)
2. `python -m fiinquant_mcp` starts stdio without crash when env set
3. Cursor/Desktop lists tools; ping + 1 market tool work live
4. Forced SDK exception → JSON error, process still up
5. README: install SDK, env, mcp.json sample

## File mapping (estimate)

| Area | Files | Count |
|------|-------|-------|
| Package core | config, gateway, errors, response, server, __main__ | ~6 |
| Tools P0 | health, market, universe | ~3 |
| Tools P1 | fundamental, screening | ~2 |
| Tests | conftest + 5–7 test modules | ~7 |
| Project meta | pyproject, README, .env.example, mcp.example.json | ~4 |
| **Total** | | **~20–22** (at plan limit — keep modules small) |

## Next after plan approve

```
/be-ship plans/20260715-fiinquant-personal-mcp
```

Optional: `/be-plan --review=devex` (API/SDK surface — MCP tools).

---

_Shipped P0: 2026-07-15 — phases 01–08 complete (unit tests green). Phase 09 deferred. Live smoke requires private SDK install on user machine._
