# Phase 07 — Implement P0 tools + FastMCP server

**Status:** Done (2026-07-15) — 25/25 green  
**Type:** impl  
**Depends on:** phase-06 approved  
**blockedBy:** phase-06  
**Effort:** ~3–4h

## Goal

Green tests phase 05 + runnable stdio MCP server.

## Implement

### Tools
- `tools/health.py` — `fq_ping`, `fq_session_status`
- `tools/market.py` — `fq_get_price_history` (map SDK)
- `tools/universe.py` — ticker list/info (map SDK)

Each tool:
1. Validate input (Pydantic)
2. `await gateway.call(...)` or typed method
3. `normalize_payload` + `success_json` / catch `GatewayError` → `error_json`
4. annotations: `readOnlyHint=True`, `openWorldHint=True` (external data)

### `server.py`
```python
mcp = FastMCP("fiinquant_mcp")
# register tools
def main():
    mcp.run(transport="stdio")
```

### `__main__.py`
- `main()` entry

### Wiring
- Lazy global gateway from `load_settings()`
- Fail soft at tool-call time if no credentials (error envelope), prefer not crash at import

## Success criteria

- [ ] All unit tests green
- [ ] `timeout 3s python -m fiinquant_mcp` starts then idle/timeout without traceback (stdio wait OK)
- [ ] Tools listed via MCP inspector or client if available

## Evaluation Rubric

```yaml
rubric: general-code
rubric_version: 1
notes: tool descriptions must be agent-friendly; no secret leak
```
