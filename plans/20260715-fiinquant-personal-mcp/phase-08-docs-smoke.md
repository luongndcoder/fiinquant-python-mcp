# Phase 08 — Docs, mcp config, live smoke

**Status:** Docs done (2026-07-15); live smoke awaiting user SDK  
**Type:** docs + manual verify  
**Depends on:** phase-07  
**blockedBy:** phase-07  
**Effort:** ~1–2h

## Deliverables

1. **README.md**
   - What / why (personal MCP, not official)
   - Install: Python, this package, **how to install private fiinquant SDK**
   - Env vars table
   - Cursor + Claude Desktop `mcp.json` samples
   - Tool list P0
   - Troubleshooting: AUTH, TIMEOUT, SDK not installed

2. **`config/mcp.example.json`**
```json
{
  "mcpServers": {
    "fiinquant": {
      "command": "python",
      "args": ["-m", "fiinquant_mcp"],
      "env": {
        "FIINQUANT_USERNAME": "your_user",
        "FIINQUANT_PASSWORD": "your_pass",
        "FIINQUANT_TIMEOUT_S": "30"
      }
    }
  }
}
```

3. **`.env.example`** — no real secrets

4. **Live smoke (manual, user machine)**
   - [ ] Login works via SDK outside MCP (control)
   - [ ] MCP client lists tools
   - [ ] `fq_ping` ok
   - [ ] `fq_get_price_history` for 1 ticker short range
   - [ ] Kill SDK (wrong password) → error envelope, process still listed

## Success criteria

- [ ] README đủ self-serve
- [ ] User confirms live smoke checklist

## Evaluation Rubric

```yaml
rubric: general-code
rubric_version: 1
notes: docs clarity TTHW < 15 min
```
