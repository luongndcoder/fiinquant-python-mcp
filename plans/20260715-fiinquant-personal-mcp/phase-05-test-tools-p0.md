# Phase 05 — Tests: P0 tools (RED)

**Status:** Done RED (2026-07-15) — 8 fail  
**Type:** test-only  
**Depends on:** phase-04  
**blockedBy:** phase-04  
**Effort:** ~2h

## Goal

Tests cho P0 tool handlers (callable functions), mock Gateway. Expected red until phase 07.

## P0 tool set (stable names — prefix `fq_`)

| Tool name | Purpose | Inputs (draft) |
|-----------|---------|----------------|
| `fq_ping` | health | — |
| `fq_session_status` | logged in? | — |
| `fq_get_price_history` | OHLCV / price series | tickers, start, end, timeframe? |
| `fq_list_tickers` / `fq_ticker_info` | universe/metadata | market/exchange or ticker |

**Final SDK method mapping** = output of phase-01 inventory. If inventory says different method names, update tests + this table before phase 07 — **do not invent fake SDK APIs**.

## Test modules

### `tests/test_tools_health.py`
- ping → ok when gateway healthy
- session_status → reflects gateway state

### `tests/test_tools_market.py`
- valid request → success envelope with data
- gateway TIMEOUT → ok=false code TIMEOUT
- empty ticker → VALIDATION

### `tests/test_tools_universe.py`
- list/info happy path
- SDK_ERROR mapped

## Patterns

- Tools are pure-ish async functions taking gateway as dep **or** module-level gateway injectable in tests
- Prefer: `async def fq_ping(gateway: Gateway | None = None)` with default singleton for server, inject in tests
- Assert JSON string parseable + schema

## Success criteria

- [ ] Tests collected, red on missing tools
- [ ] All P0 tools have ≥1 happy + ≥1 failure case

## Evaluation Rubric

```yaml
rubric: general-code
rubric_version: 1
```
