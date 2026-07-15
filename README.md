# fiinquant-mcp (personal)

Personal **resilient** MCP server wrapping the FiinQuant / **FiinQuantX** Python SDK for **Claude Desktop / Cursor** (stdio).

> Not an official FiinGroup/FiinQuant product. Tool surface aligned with official FiinQuant MCP domain tools, with timeout / error envelope / size budget so agent hosts do not hang.

**Version:** 0.2.0 (P0 + P1)

## Quick start (uvx)

Requires [uv](https://docs.astral.sh/uv/).

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

Live data needs the **private SDK wheel**:

```json
"args": [
  "--from", "git+https://github.com/luongndcoder/fiinquant-python-mcp",
  "--with", "/ABS/PATH/to/FiinQuantX.whl",
  "fiinquant-mcp"
]
```

See `config/mcp.example.json` and `config/mcp.with-sdk.example.json`.

## Tools (P0 + P1)

| Domain | Tools |
|--------|--------|
| **Health** | `fq_ping`, `fq_session_status`, `fq_list_ops` |
| **Market** | `fq_get_price_history`, `fq_get_stock_prices`, `fq_get_market_statistics`, `fq_get_market_breadth`, `fq_get_index_constituents`, `fq_get_money_flow_contribution`, `fq_get_realtime_bid_ask` |
| **Universe** | `fq_list_tickers`, `fq_ticker_info`, `fq_get_basic_info`, `fq_get_icb_industries` |
| **Fundamental** | `fq_get_financial_ratios`, `fq_get_financial_statements`, `fq_get_valuation_timeseries`, `fq_get_equity_snapshot` |
| **Screen / TA** | `fq_screen_stocks`, `fq_get_technical_indicators`, `fq_detect_pattern`, `fq_get_rrg_analysis`, `fq_get_rebalance`, `fq_run_custom_analysis` |
| **Meta** | `fq_search_methods`, `fq_call_method` |

**~26 tools** total. Names use `fq_` prefix; semantics match official FiinQuant MCP domain tools.

### Examples

```text
fq_get_stock_prices tickers=FPT,VNM latest=true
fq_get_financial_ratios tickers=FPT years=2023,2024
fq_get_financial_statements tickers=FPT statement=income_statement
fq_screen_stocks filters=[{"indicator":"roe","operator":"gt","value":20}] limit=30
fq_get_technical_indicators tickers=VNM indicators=[{"name":"rsi","window":14}]
fq_get_index_constituents index=VN30
```

Responses:

```json
{"ok": true, "data": ..., "meta": {"truncated": false, "row_count": 10}}
```

```json
{"ok": false, "code": "TIMEOUT|AUTH|SDK_ERROR|VALIDATION|INTERNAL", "message": "...", "hint": "..."}
```

## Architecture

```
Cursor / Claude Desktop
        │ stdio
        ▼
  uvx → fiinquant-mcp (FastMCP tools)
        │
        ▼
  FiinQuantGateway (session, timeout, re-auth, size budget)
        │
        ▼
  ops.py aliases → FiinQuantX / fiinquant SDK methods
```

If your SDK method names differ, edit `src/fiinquant_mcp/ops.py` or run:

```bash
python scripts/inventory_fiinquant_sdk.py
```

## Environment

| Variable | Default | Meaning |
|----------|---------|---------|
| `FIINQUANT_USERNAME` | — | SDK username |
| `FIINQUANT_PASSWORD` | — | SDK password |
| `FIINQUANT_TIMEOUT_S` | `30` | Hard timeout per call |
| `FIINQUANT_MAX_ROWS` | `500` | Max table rows |
| `FIINQUANT_MAX_CHARS` | `80000` | Max response chars |
| `FIINQUANT_LOG_LEVEL` | `INFO` | stderr logs |

## Develop

```bash
git clone https://github.com/luongndcoder/fiinquant-python-mcp.git
cd fiinquant-python-mcp
uv sync --extra dev
uv run pytest -v
uvx --from . fiinquant-mcp
```

## License

MIT for this wrapper only. FiinQuant SDK and market data remain under FiinQuant terms.
