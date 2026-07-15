# Phase 09 — P1 domain expand (after P0 stable)

**Status:** Done (2026-07-15) — v0.2.0 ~26 tools  
**Type:** feature expansion  
**Depends on:** phase-08 live smoke OK  
**blockedBy:** phase-08  
**Effort:** variable (1–2d)

## Goal

Mở tool surface đa dạng ~ official MCP **sau khi** reliability P0 proven.

## Candidate domains (từ Document + SDK inventory)

| Domain | Example tools | Priority |
|--------|---------------|----------|
| Fundamental | BCTC, ratios, financials | P1 |
| Screening | filter universe by criteria | P1 |
| Indicators | TA indicators if SDK exposes | P1 |
| Corporate events | dividends, events if available | P2 |
| Realtime | if SDK supports streaming — careful with MCP request model | P2 / maybe skip |

## Process per domain (repeat TDD mini-cycle)

1. Map SDK methods → tool specs  
2. Write tests (red)  
3. User review if surface large  
4. Implement + normalize large tables  
5. Update README tool catalog  

## Rules

- Mọi call qua Gateway — không bypass
- Default `max_rows` / timeframe limits cho screening
- Không dump full market into one response
- Prefer workflow tools over 1:1 raw API spam (mcp-builder principle)

## Success criteria

- [x] ≥2 domains beyond market/universe (fundamental + screening/TA + market expand)
- [x] Unit tests green; no regression P0
- [x] README catalog updated

## Evaluation Rubric

```yaml
rubric: general-code
rubric_version: 1
```
