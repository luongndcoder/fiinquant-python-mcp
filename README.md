# fiinquant-mcp (personal)

Personal **resilient** MCP server wrapping the FiinQuant Python SDK for **Claude Desktop / Cursor** (stdio).

> Not an official FiinGroup/FiinQuant product. Built for local agent reliability: tool failures return JSON error envelopes instead of hanging or killing the process.

## Quick start (uvx — recommended)

Requires [uv](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`).

### Cursor / Claude Desktop / Codex

```json
{
  "mcpServers": {
    "fiinquant": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/luongndcoder/fiinquant-python-mcp",
        "fiinquant-mcp"
      ],
      "env": {
        "FIINQUANT_USERNAME": "your_user",
        "FIINQUANT_PASSWORD": "your_pass"
      }
    }
  }
}
```

Copy from [`config/mcp.example.json`](config/mcp.example.json).

### CLI smoke

```bash
# print-help / start stdio (MCP clients talk on stdin — use client config above)
uvx --from git+https://github.com/luongndcoder/fiinquant-python-mcp fiinquant-mcp
```

Pin a ref if you want:

```bash
uvx --from git+https://github.com/luongndcoder/fiinquant-python-mcp@main fiinquant-mcp
```

### Live data = private FiinQuant SDK

`fiinquant` is **not on public PyPI**. Inject the wheel with `--with`:

```bash
uvx --from git+https://github.com/luongndcoder/fiinquant-python-mcp \
  --with /path/to/fiinquant.whl \
  fiinquant-mcp
```

MCP config with SDK: [`config/mcp.with-sdk.example.json`](config/mcp.with-sdk.example.json).

Without the SDK, health tools (`fq_ping`, `fq_session_status`) still work; market/universe tools return structured `AUTH` / `INTERNAL` errors instead of crashing.

## Why

| Layer | Status |
|-------|--------|
| FiinQuant **Python SDK** (data) | Works for many users outside MCP |
| Official / remote FiinQuant MCP | Often unreliable for agent hosts |
| **This package** | Resilient facade: timeout, re-auth, size budget, structured errors |

## Architecture

```
Cursor / Claude Desktop
        │ stdio
        ▼
  uvx → fiinquant-mcp (FastMCP)
        │
        ▼
  FiinQuantGateway (session, timeout, error map)
        │
        ▼
  fiinquant SDK (private wheel via --with)
```

## Environment

| Variable | Default | Meaning |
|----------|---------|---------|
| `FIINQUANT_USERNAME` | — | SDK username |
| `FIINQUANT_PASSWORD` | — | SDK password |
| `FIINQUANT_TIMEOUT_S` | `30` | Hard timeout per SDK call |
| `FIINQUANT_MAX_ROWS` | `500` | Max table rows returned |
| `FIINQUANT_MAX_CHARS` | `80000` | Max JSON response chars |
| `FIINQUANT_LOG_LEVEL` | `INFO` | Logging (stderr only) |

**Never commit real credentials.**

## P0 tools

| Tool | Description |
|------|-------------|
| `fq_ping` | Process health (no login) |
| `fq_session_status` | Credentials configured? logged in? |
| `fq_get_price_history` | OHLCV / price series (`tickers`, `start`, `end`) |
| `fq_list_tickers` | Universe list (optional `market`) |
| `fq_ticker_info` | Single ticker metadata |

Response shape:

```json
{"ok": true, "data": ..., "meta": {"truncated": false, "row_count": 10}}
```

```json
{"ok": false, "code": "TIMEOUT|AUTH|SDK_ERROR|VALIDATION|INTERNAL", "message": "...", "hint": "..."}
```

## Local develop

```bash
git clone https://github.com/luongndcoder/fiinquant-python-mcp.git
cd fiinquant-python-mcp
uv sync --extra dev
uv run pytest -v

# run like production
uvx --from . fiinquant-mcp
# or
uv run fiinquant-mcp
```

## Live smoke checklist

1. `uvx` installs and process starts (MCP client lists tools)
2. `fq_ping` → `ok`
3. With SDK + creds: `fq_get_price_history` for one ticker, short range
4. Tool error → JSON envelope; process still up

## License

MIT for this wrapper only. FiinQuant SDK and market data remain under FiinQuant terms of use.
