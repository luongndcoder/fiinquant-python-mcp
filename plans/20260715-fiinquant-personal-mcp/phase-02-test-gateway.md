# Phase 02 — Tests: Gateway + response + errors (RED)

**Status:** Done RED (2026-07-15) — 14 fail / 3 pass (config)  
**Type:** test-only  
**Depends on:** phase-01  
**blockedBy:** phase-01  
**Effort:** ~2–3h

## Goal

Viết unit tests cho reliability core **trước** implementation. Tests **expected FAIL** (red) cho đến phase 04.

## Test modules to create

### `tests/test_errors.py`

| ID | Case | Assert |
|----|------|--------|
| E1 | `error_envelope("TIMEOUT", "msg", hint="...")` | JSON keys: ok=false, code, message, hint |
| E2 | success helper optional | ok=true shape stable if exists |
| E3 | unknown code still serializable | no throw |

### `tests/test_response.py`

| ID | Case | Assert |
|----|------|--------|
| R1 | list[dict] small | ok serialize, row_count |
| R2 | rows > max_rows | truncated True, len(data) ≤ max_rows |
| R3 | string longer than max_chars | truncated / char budget |
| R4 | nested datetime/numpy-like via simple mocks | JSON-serializable output (str cast ok) |

### `tests/test_config.py`

| ID | Case | Assert |
|----|------|--------|
| C1 | load defaults | timeout=30, max_rows=500 |
| C2 | env override | monkeypatch FIINQUANT_TIMEOUT_S |
| C3 | missing credentials detection | `has_credentials` False |

### `tests/test_gateway.py`

| ID | Case | Assert |
|----|------|--------|
| G1 | no credentials → AUTH error mapping | call fails with code AUTH |
| G2 | mock client success | returns payload |
| G3 | mock client raises Exception | SDK_ERROR, not raw traceback to caller as uncaught |
| G4 | mock slow call > timeout | TIMEOUT within ~timeout+slack |
| G5 | session invalid once then ok | re-auth path invoked ≤1 retry |
| G6 | concurrent-ish sequential calls | same gateway instance safe (no crash) |

## Mock strategy

```python
# Pseudo — inject client factory into Gateway
class FakeClient:
    def login(self): ...
    def get_market_data(self, **kw): ...  # name adjusted after inventory
```

- Gateway **must** accept injectable client/factory for tests (DI) — không hard-import-only.
- Timeout test: fake fn `time.sleep(2)` with `timeout_s=0.2`.

## Implementation note for later (phase 04)

Do **not** implement production code in this phase except minimal stubs if import fails hard (prefer tests import real module paths that will exist).

If imports break collection: add skeleton classes with `NotImplementedError` in phase 01 already.

## Success criteria

- [ ] `pytest` collects all G/R/E/C tests
- [ ] Majority **fail** (red) for unimplemented behavior
- [ ] No network, no real credentials
- [ ] Test IDs match plan.md Test Plan table

## Evaluation Rubric

```yaml
rubric: general-code
rubric_version: 1
notes: test quality — isolation, no flaky sleep without bound
```
