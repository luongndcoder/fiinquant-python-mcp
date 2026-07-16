# fiinquant-mcp (personal)

Personal **resilient** MCP server wrapping the FiinQuant / **FiinQuantX** Python SDK for **Claude Desktop / Cursor / Grok CLI** (stdio).

> Not an official FiinGroup/FiinQuant product. Domain tool names match official FiinQuant MCP; personal extras keep the `fq_` prefix.

**Version:** 0.3.1 · **Tools:** 27 (21 official + 6 extras)

---

## How it works

```mermaid
flowchart TB
  subgraph Client["MCP Client"]
    A["Claude Desktop / Cursor / Grok CLI"]
  end

  subgraph MCP["fiinquant-mcp process (stdio)"]
    B["FastMCP tools<br/>27 tools · official names + fq_* extras"]
    C["Gateway<br/>timeout · re-auth · rate limit · free-tier guards"]
    D["Response envelope<br/>ok / code / data / meta · size budget"]
    E["SdkClientAdapter<br/>FiinSession mapping"]
  end

  subgraph SDK["Local Python"]
    F["FiinQuantX SDK<br/>private package"]
  end

  subgraph Cloud["FiinQuant cloud APIs"]
    G["Trading data / fundamental / screening / …"]
  end

  A <-->|"JSON-RPC over stdio"| B
  B --> C
  C --> E
  E --> F
  F <-->|"HTTPS + account token"| G
  C --> D
  D --> B
  B --> A
```

**Data path:** client → MCP tool → Gateway (reliability + free limits) → FiinQuantX → FiinQuant API → JSON envelope back to agent.

**Auth:** `FIINQUANT_USERNAME` / `FIINQUANT_PASSWORD` in MCP env (not browser OIDC like official remote MCP).

---

## Quick start

### 1. Install FiinQuantX SDK (required for live data)

```bash
# Same Python that will run the MCP, e.g. system 3.11:
pip install FiinQuantX   # or your private wheel from FiinQuant portal
python -c "import FiinQuantX; print('OK')"
```

SDK is **not** on public PyPI for everyone — install from your FiinQuant account package / wheel.

### 2. Grok CLI (recommended on this machine)

If SDK is on system Python 3.11:

```toml
# ~/.grok/config.toml
[mcp_servers.fiinquant]
command = "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3"
args = ["-m", "fiinquant_mcp"]
enabled = true
startup_timeout_sec = 60

[mcp_servers.fiinquant.env]
FIINQUANT_USERNAME = "your@email.com"
FIINQUANT_PASSWORD = "your_password"
FIINQUANT_PLAN = "free"
FIINQUANT_ENFORCE_PLAN_LIMITS = "true"
```

```bash
pip install -e /path/to/fiinquant-python-mcp   # same Python as FiinQuantX
grok mcp doctor fiinquant
```

### 3. uvx (isolated env)

Only works if FiinQuantX is injected into the uvx env:

```json
{
  "mcpServers": {
    "fiinquant": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/luongndcoder/fiinquant-python-mcp",
        "--with", "/path/to/FiinQuantX.whl",
        "fiinquant-mcp"
      ],
      "env": {
        "FIINQUANT_USERNAME": "your@email.com",
        "FIINQUANT_PASSWORD": "your_password",
        "FIINQUANT_PLAN": "free"
      }
    }
  }
}
```

---

## Free plan notes (Trải nghiệm / Miễn phí)

Local guards (MCP) + account API permissions (FiinQuant) both apply.

### Local guards (`FIINQUANT_PLAN=free`)

| Limit | Value |
|-------|--------|
| Connections | 1 session |
| Requests / min · / s | 90 · 80 |
| Realtime tickers / call | ≤ 33 |
| History window | ≤ **31 days** |
| Intraday TF | `1m`, `5m`, `15m`, `1h`, `4h` (+ Daily) |

Over limit → JSON `VALIDATION` or `RATE_LIMIT` (process does **not** crash).

### Live suite (account free) — tool status

Tested end-to-end with FiinQuantX + free account (see `plans/.../tool-test-report.json`).

| Status | Meaning | Count |
|--------|---------|-------|
| **Works** | Returns real data | 21 |
| **Blocked by free API** | Tool runs; FiinQuant returns 403 / no permission | 6 |
| **Crash** | — | 0 |

**Works on free (typical):**

- `get_stock_prices`, `fq_get_price_history`
- `get_financial_ratios`, `get_financial_statements`
- `get_valuation_timeseries`, `get_equity_snapshot`
- `get_rrg_analysis`, `get_rebalance`
- `get_technical_indicators`, `detect_pattern`
- `get_market_statistics`, health/meta tools

**Often 403 on free (need higher plan):**

| Tool | Typical error |
|------|----------------|
| `get_basic_info` / `fq_ticker_info` | ApiAccessFailed 403 |
| `screen_stocks` | Screening API 403 |
| `get_market_breadth` | No permission MarketBreadth |
| `get_money_flow_contribution` | No permission MoneyFlow |
| `get_index_constituents` | 403 |

Envelope example when blocked:

```json
{"ok": false, "code": "SDK_ERROR", "message": "…permission…", "hint": "…"}
```

---

## Response format

Success:

```json
{"ok": true, "data": …, "meta": {"truncated": false, "row_count": 10}}
```

Error (tool failure ≠ process die):

```json
{"ok": false, "code": "TIMEOUT|AUTH|SDK_ERROR|VALIDATION|RATE_LIMIT|INTERNAL", "message": "…", "hint": "…"}
```

`tickers` accepts `["FPT","VNM"]` or `"FPT,VNM"`.

---

## Prompt guide (per tool)

Copy/adapt prompts for your agent. Prefer **official tool names** first.

### Health & meta

| Tool | When to use | Example prompt |
|------|-------------|----------------|
| `fq_ping` | Check MCP alive | “Ping FiinQuant MCP xem process còn sống không.” |
| `fq_session_status` | Creds / plan / rate | “Kiểm tra session FiinQuant: đã login chưa, plan free limits thế nào.” |
| `fq_list_ops` | List gateway ops | “Liệt kê các op Gateway hỗ trợ.” |
| `report_issue` | Local debug note | “Ghi issue local: tool X lỗi Y khi hỏi Z.” *(chỉ log local, không gửi admin FiinQuant)* |
| `fiinquantx_search_methods` | Discover SDK methods | “Search method FiinQuantX chứa Fetch.” |
| `fiinquantx_call_method` | Escape hatch | “Dry-run call method_id=login với params {}.” |

### Market / prices

| Tool | When to use | Example prompt |
|------|-------------|----------------|
| **`get_stock_prices`** | Giá / OHLCV chính | “Lấy giá **FPT** 2 tuần gần nhất (Daily, adjusted).” · “OHLCV FPT và VNM từ 2026-07-01 đến 2026-07-15.” · “Giá **VNINDEX** tuần qua.” |
| `fq_get_price_history` | OHLCV đơn giản start/end | “Price history VNM start=2026-07-01 end=2026-07-15.” |
| `get_market_statistics` | Stats (cap, foreign…) | “Market statistics FPT từ 2026-07-01 đến 2026-07-15, time_filter=Daily.” |
| `get_market_breadth` | Breadth index | “Market breadth VNINDEX.” *(free: often no permission)* |
| `get_index_constituents` | Thành phần chỉ số | “Lấy danh sách mã **VN30**.” *(free: often 403)* |
| `get_money_flow_contribution` | Dòng tiền / đóng góp | “Top gainers đóng góp VNINDEX 1Day, limit 10.” *(free: often no permission)* |
| `get_realtime_bid_ask` | Bid/ask | “Bid/ask realtime FPT.” *(SDK streaming; may return guidance note)* |

**Tips `get_stock_prices`:**

- Always pass **`from_date` + `to_date`** (YYYY-MM-DD); free max span **31 days**.
- `frequency`: `Daily` or `1m`/`5m`/`15m`/`1h`/`4h`.
- Multiple tickers: `["FPT","VNM"]`.

### Universe

| Tool | When to use | Example prompt |
|------|-------------|----------------|
| `get_basic_info` | Tên, sàn, ngành | “Basic info FPT, VNM.” *(free: often 403)* |
| `get_icb_industries` | ICB levels | “List ICB industries level=2.” |
| `fq_list_tickers` | List theo sàn | “List tickers market=HOSE.” |
| `fq_ticker_info` | 1 mã metadata | “Ticker info FPT.” *(free: often 403)* |

### Fundamental

| Tool | When to use | Example prompt |
|------|-------------|----------------|
| **`get_financial_ratios`** | Chỉ số tài chính | “Financial ratios FPT years 2024 và 2025.” |
| **`get_financial_statements`** | BCTC | “Income statement FPT năm 2024 (consolidated).” · “Balance sheet FPT statement=balance_sheet years=[2024].” |
| `get_valuation_timeseries` | Lịch sử định giá | “Valuation timeseries FPT scope=stock from 2026-06-15 to 2026-07-15.” |
| `get_equity_snapshot` | Snapshot gần đây | “Equity snapshot FPT metrics pe,pb.” |

**`statement` values:** `income_statement` · `balance_sheet` · `cashflow` · `full` · `note`

### Screening & technical

| Tool | When to use | Example prompt |
|------|-------------|----------------|
| `screen_stocks` | Lọc cổ phiếu | “Screen HOSE: ROE > 15, limit 20.” *(free: often 403)* |
| `get_technical_indicators` | RSI/MACD/… | “RSI 14 và MACD cho FPT, by=1d.” |
| `detect_pattern` | Mẫu nến / pattern | “Detect doji trên FPT từ 2026-06-15 đến 2026-07-15.” |
| `get_rrg_analysis` | RRG vs benchmark | “RRG FPT,VNM vs VNINDEX 1 tháng gần nhất.” |
| `get_rebalance` | Phân bổ theo rổ | “Rebalance VN30 với budget 1 tỷ VND.” |
| `run_custom_analysis` | Custom / list | “List custom analyses available.” |

**Screen filters example (JSON):**

```json
[{"indicator": "roe", "operator": "gt", "value": 15}]
```

**Pattern `params` example:**

```json
{"tickers": ["FPT"], "from_date": "2026-06-15", "to_date": "2026-07-15", "by": "1d"}
```

---

## Example agent workflows

### A. Xem giá nhanh

```text
Dùng get_stock_prices lấy OHLCV FPT 2 tuần gần nhất (Daily, adjusted).
Tóm tắt close đầu/cuối kỳ, % thay đổi, volume bất thường.
```

### B. Phân tích fundamental

```text
1) get_financial_ratios FPT years 2024,2025
2) get_financial_statements FPT income_statement 2024
So sánh revenue / net profit / EPS.
```

### C. So sánh 2 mã + index

```text
get_stock_prices tickers=[FPT,VNM,VNINDEX] from_date=… to_date=… (≤31 ngày free).
Bảng close theo ngày + nhận xét tương quan ngắn hạn.
```

### D. Khi tool 403

```text
Nếu SDK_ERROR permission/403: báo user đây là hạn mức gói free FiinQuant,
không phải MCP die; gợi ý tool thay thế (vd giá thay vì screen).
```

---

## Environment

| Variable | Default | Meaning |
|----------|---------|---------|
| `FIINQUANT_USERNAME` | — | SDK username |
| `FIINQUANT_PASSWORD` | — | SDK password |
| `FIINQUANT_PLAN` | `free` | `free` \| `paid` |
| `FIINQUANT_ENFORCE_PLAN_LIMITS` | `true` | Local rate/history/ticker guards |
| `FIINQUANT_MAX_HISTORY_DAYS` | `31` (free) | Max date span |
| `FIINQUANT_MAX_REALTIME_TICKERS` | `33` | Cap per realtime-ish call |
| `FIINQUANT_REQUESTS_PER_MINUTE` | `90` | Local RPM |
| `FIINQUANT_REQUESTS_PER_SECOND` | `80` | Local RPS |
| `FIINQUANT_TIMEOUT_S` | `30` | Per-call timeout |
| `FIINQUANT_MAX_ROWS` | `500` | Response row budget |
| `FIINQUANT_MAX_CHARS` | `80000` | Response char budget |

---

## Architecture vs official MCP

| | Official FiinQuant MCP | This MCP |
|--|------------------------|----------|
| Tool names | `get_stock_prices`, … | **Same** + `fq_*` extras |
| Auth | Browser / OIDC remote | Local SDK user/pass |
| Transport | Streamable HTTP | **stdio** |
| Reliability | Vendor | Timeout, envelope, size budget, free guards |
| `report_issue` | Admin upload | Local log only |

```mermaid
sequenceDiagram
  participant U as User / Agent
  participant C as MCP Client
  participant M as fiinquant-mcp
  participant G as Gateway
  participant S as FiinQuantX
  participant A as FiinQuant API

  U->>C: "Giá FPT 2 tuần gần nhất"
  C->>M: tools/call get_stock_prices
  M->>G: call(op, tickers, from, to)
  G->>G: free-tier check (≤31d, rate…)
  G->>S: Fetch_Trading_Data(...)
  S->>A: HTTPS
  A-->>S: OHLCV
  S-->>G: DataFrame
  G-->>M: normalize + envelope
  M-->>C: {"ok":true,"data":[...]}
  C-->>U: Table / summary
```

---

## Develop

```bash
git clone https://github.com/luongndcoder/fiinquant-python-mcp.git
cd fiinquant-python-mcp
# Use a Python that already has FiinQuantX
pip install -e ".[dev]"
pytest -v
python -m fiinquant_mcp   # stdio server
```

Unit tests mock the SDK boundary (no network). Live suite: `plans/20260715-fiinquant-personal-mcp/tool-test-report.json`.

---

## License

MIT for this wrapper only. FiinQuant SDK and market data remain under FiinQuant terms of use. Do not commit credentials.
