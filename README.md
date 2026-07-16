# fiinquant-mcp (personal)

Personal **resilient** MCP server wrapping the FiinQuant / **FiinQuantX** Python SDK for **Claude Desktop / Cursor** (stdio).

> Not an official FiinGroup/FiinQuant product. **Domain tool names match official FiinQuant MCP**; personal extras keep the `fq_` prefix.

**Version:** 0.3.0

## Quick start (uvx)

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
        "FIINQUANT_PASSWORD": "your_pass",
        "FIINQUANT_PLAN": "free"
      }
    }
  }
}
```

Live data needs private SDK: add `"--with", "/path/to/FiinQuantX.whl"` before `fiinquant-mcp`.

## Tools

### Official names (21) — same as FiinQuant MCP

| Tool | Role |
|------|------|
| `get_stock_prices` | Primary OHLCV / latest price |
| `get_market_statistics` | market_cap, volume/value |
| `get_market_breadth` | Advance/decline breadth |
| `get_index_constituents` | e.g. VN30 members |
| `get_money_flow_contribution` | Index contribution / flow |
| `get_realtime_bid_ask` | Bid/ask snapshot |
| `get_basic_info` | Company / ICB basics |
| `get_icb_industries` | ICB industry list |
| `get_financial_ratios` | Ratios (ROE, PE, …) |
| `get_financial_statements` | BCTC income/balance/cashflow/full/note |
| `get_valuation_timeseries` | Valuation history |
| `get_equity_snapshot` | Point-in-time pe/pb/liquidity… |
| `screen_stocks` | Stock screening filters |
| `get_technical_indicators` | RSI, MACD, SMA… |
| `detect_pattern` | Candle / pattern |
| `get_rrg_analysis` | RRG vs benchmark |
| `get_rebalance` | Index rebalance budget |
| `run_custom_analysis` | Custom analyses |
| `fiinquantx_search_methods` | Discover SDK methods |
| `fiinquantx_call_method` | Call method by id |
| `report_issue` | Issue report (**local log only**) |

### Personal extras (6) — kept on purpose

| Tool | Role |
|------|------|
| `fq_ping` | Process health |
| `fq_session_status` | Session + free-tier plan status |
| `fq_list_ops` | Gateway op catalog |
| `fq_get_price_history` | Simple OHLCV `start`/`end` helper |
| `fq_list_tickers` | List tickers by market |
| `fq_ticker_info` | Single ticker metadata |

**Total: 27 tools** (21 official + 6 extras).

`tickers` accepts JSON array `["FPT","VNM"]` or CSV `"FPT,VNM"`.

## Free plan guards (default)

| Limit | Free |
|-------|------|
| Connections | 1 |
| Req/min · req/s | 90 · 80 |
| Realtime tickers | ≤33 |
| History depth | ≤31 days |
| Timeframes | 1m, 5m, 15m, 1h, 4h (+ Daily) |

See `FIINQUANT_PLAN`, `FIINQUANT_ENFORCE_PLAN_LIMITS` in `.env.example`.

## Still different from official (by design)

| | Official | This MCP |
|--|----------|----------|
| Auth | Browser / OIDC remote | Local SDK username/password |
| Transport | Remote Streamable HTTP | stdio via `uvx` |
| Reliability | Vendor | Timeout, envelope, size budget |
| `report_issue` | Uploads to admin | **Local stderr log only** |

## Develop

```bash
uv sync --extra dev
uv run pytest -v
uvx --from . fiinquant-mcp
```

## License

MIT for this wrapper only. FiinQuant SDK/data under FiinQuant terms.
