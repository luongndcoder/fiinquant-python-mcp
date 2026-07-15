# Phase 04 — Implement Gateway + core (GREEN)

**Status:** Done (2026-07-15) — 17/17 green  
**Type:** impl  
**Depends on:** phase-03 approved  
**blockedBy:** phase-03  
**Effort:** ~3–4h

## Goal

Làm xanh toàn bộ tests phase 02. Không register MCP tools ở phase này (trừ nếu cần import side-effect-free).

## Implement

### `errors.py`
- Codes enum/str: `AUTH`, `TIMEOUT`, `SDK_ERROR`, `VALIDATION`, `INTERNAL`
- `error_json(...)` / `success_json(data, meta=...)`

### `config.py`
- dataclass `Settings` from env
- `load_settings()` 
- never log password

### `response.py`
- `normalize_payload(obj, max_rows, max_chars) -> dict`
- Handle: dict, list[dict], pandas DataFrame **if available** (optional import), str
- Set `meta.truncated`, `meta.row_count`

### `gateway.py`
- `class FiinQuantGateway`
  - `__init__(settings, client_factory=None)`
  - `ensure_session()` — lazy login via SDK
  - `async def call(self, op: str, **kwargs) -> Any` **or** typed methods
  - Internals:
    - run sync SDK in `asyncio.to_thread`
    - `asyncio.wait_for(..., timeout=settings.timeout_s)`
    - map exceptions → structured error (raise domain `GatewayError` caught by tools later)
    - re-auth once on session-expired heuristic (message match / flag — tune after inventory)
  - **No** process `sys.exit` on failure

### SDK adapter
- Private module `_sdk.py` or methods inside gateway:
  - Import `fiinquant` behind try/except with clear AUTH/INTERNAL if missing install
  - Map `op` names loosely until inventory locked

## Non-goals

- FastMCP tools
- Real network tests

## Success criteria

- [ ] `pytest tests/test_errors.py tests/test_response.py tests/test_config.py tests/test_gateway.py` **all green**
- [ ] Coverage core modules ≥70%
- [ ] Password never appears in log strings (grep test optional)

## Evaluation Rubric

```yaml
rubric: general-code
rubric_version: 1
notes: reliability + secret hygiene critical
```
