# Phase 01 — Project scaffold

**Status:** Done (2026-07-15)  
**Type:** setup (no production business logic)  
**Depends on:** —  
**Effort:** ~1–2h

## Goal

Tạo skeleton package + tooling để phases TDD chạy được. Inventory SDK `fiinquant` trên máy user (private package).

## Steps

1. **Init project**
   - `pyproject.toml`: name `fiinquant-mcp`, python ≥3.11, deps `mcp`, `pydantic`, `python-dotenv` (optional)
   - dev: `pytest`, `pytest-asyncio`, `ruff` (optional)
   - entry: `[project.scripts] fiinquant-mcp = "fiinquant_mcp.server:main"` + `python -m fiinquant_mcp`
   - **Không** pin `fiinquant` trên PyPI public — document:
     - `dependencies` optional extra `[fiinquant]` nếu user có index
     - hoặc `pip install /path/to/fiinquant.whl`

2. **Package dirs**
   - Create empty modules: `src/fiinquant_mcp/{config,gateway,errors,response,server,__main__}.py`
   - `src/fiinquant_mcp/tools/` package
   - `tests/` + `conftest.py` minimal

3. **Config contract (stubs)**
   - Env names (document in `.env.example`):
     - `FIINQUANT_USERNAME` / `FIINQUANT_PASSWORD` (hoặc token nếu SDK dùng token — **verify khi inventory**)
     - `FIINQUANT_TIMEOUT_S` default `30`
     - `FIINQUANT_MAX_ROWS` default `500`
     - `FIINQUANT_MAX_CHARS` default `80000`
     - `FIINQUANT_LOG_LEVEL` default `INFO`

4. **SDK inventory (read-only script, dev)**
   - `scripts/inventory_fiinquant_sdk.py` (or one-off):
     - `import fiinquant` / inspect public classes/methods
     - print method names + signatures → save `plans/.../research/sdk-inventory.md`
   - **User runs** with their env where SDK already works
   - Output feeds phase 05/07 tool mapping

5. **Sanity**
   - `pip install -e ".[dev]"`
   - `pytest` collects 0 or placeholder pass
   - Ruff optional

## Out of scope

- Real Gateway logic (phase 04)
- Real tools (phase 07)
- Live FiinQuant calls in CI

## Success criteria

- [x] Editable install works
- [x] Package importable: `import fiinquant_mcp`
- [x] `.env.example` + stub modules exist
- [x] Inventory script ready (run by user when SDK available)
- [x] No secrets committed

## Evaluation Rubric

```yaml
rubric: general-code
rubric_version: 1
notes: scaffold only — no business logic review depth
```
