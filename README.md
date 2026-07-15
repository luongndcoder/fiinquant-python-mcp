# fiinquant-mcp (personal)

Personal **resilient** MCP server wrapping the FiinQuant Python SDK for **Claude Desktop / Cursor** (stdio).

> Not an official FiinGroup/FiinQuant product. Built for local agent reliability: tool failures return JSON error envelopes instead of hanging or killing the process.

## Why

| Layer | Status |
|-------|--------|
| FiinQuant **Python SDK** (data) | Works for many users outside MCP |
| Official / remote FiinQuant MCP | Often unreliable for agent hosts |
| **This package** | Resilient facade: timeout, re-auth once, size budget, structured errors |

## Architecture

```
Cursor / Claude Desktop
        │ stdio
        ▼
  FastMCP tools (fq_*)
        │
        ▼
  FiinQuantGateway (session, timeout, error map)
        │
        ▼
  fiinquant SDK (private install)
```

## Install

```bash
cd fiinquant-python-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### FiinQuant SDK (required for live data)

The `fiinquant` package is **not on public PyPI**. Install your private wheel / internal index the same way you already use outside MCP:

```bash
pip install /path/to/fiinquant.whl
# optional inventory:
python scripts/inventory_fiinquant_sdk.py
```

If method names differ from defaults, map them in `src/fiinquant_mcp/sdk_client.py` (or inject a custom `client_factory`).

## Configuration

Copy `.env.example` or set env vars in MCP config:

| Variable | Default | Meaning |
|----------|---------|---------|
| `FIINQUANT_USERNAME` | — | SDK username |
| `FIINQUANT_PASSWORD` | — | SDK password |
| `FIINQUANT_TIMEOUT_S` | `30` | Hard timeout per SDK call |
| `FIINQUANT_MAX_ROWS` | `500` | Max table rows returned |
| `FIINQUANT_MAX_CHARS` | `80000` | Max JSON response chars |
| `FIINQUANT_LOG_LEVEL` | `INFO` | Logging (stderr only) |

**Never commit real credentials.**

## Cursor / Claude Desktop

See [`config/mcp.example.json`](config/mcp.example.json). Point `command` at this project's venv Python:

```json
{
  "mcpServers": {
    "fiinquant": {
      "command": "/ABS/PATH/fiinquant-python-mcp/.venv/bin/python",
      "args": ["-m", "fiinquant_mcp"],
      "env": {
        "FIINQUANT_USERNAME": "your_user",
        "FIINQUANT_PASSWORD": "your_pass"
      }
    }
  }
}
```

## P0 tools

| Tool | Description |
|------|-------------|
| `fq_ping` | Process health (no login) |
| `fq_session_status` | Credentials configured? logged in? |
| `fq_get_price_history` | OHLCV / price series (`tickers`, `start`, `end`) |
| `fq_list_tickers` | Universe list (optional `market`) |
| `fq_ticker_info` | Single ticker metadata |

All tools return JSON strings:

```json
{"ok": true, "data": ..., "meta": {"truncated": false, "row_count": 10}}
```

```json
{"ok": false, "code": "TIMEOUT|AUTH|SDK_ERROR|VALIDATION|INTERNAL", "message": "...", "hint": "..."}
```

## Develop / test

```bash
source .venv/bin/activate
pytest -v
pytest --cov=fiinquant_mcp --cov-report=term-missing
```

Unit tests mock the SDK boundary — no network required.

## Live smoke checklist

1. SDK login works outside MCP with same credentials  
2. MCP client lists the five `fq_*` tools  
3. `fq_ping` → `ok`  
4. `fq_get_price_history` for one ticker, short date range  
5. Wrong password → `AUTH` / `SDK_ERROR` envelope; process still up  

## Plan

Implementation plan: `plans/20260715-fiinquant-personal-mcp/`.

P1 (later): fundamental, screening, indicators — only after P0 live smoke is green.

## License

MIT for this wrapper only. FiinQuant SDK and market data remain under FiinQuant terms of use.
