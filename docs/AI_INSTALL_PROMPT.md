# AI Install Prompt — fiinquant-mcp

Copy **toàn bộ block** bên dưới (phần trong fence `text`) dán vào Codex CLI, Claude Code, Grok, Cursor Agent, v.v.  
AI sẽ tự cài / cấu hình; user chỉ cần cung cấp **username + password** FiinQuant khi được hỏi.

---

## Prompt (copy from here)

```text
Bạn là agent cài đặt MCP. Hãy cài PERSONAL FiinQuant MCP (SDK local) cho máy user — KHÔNG cài official remote proxy trừ khi user yêu cầu riêng.

## Mục tiêu
1) Cài package `fiinquant-mcp` + đảm bảo `FiinQuantX` import được trên CÙNG một Python.
2) Đăng ký MCP stdio vào (các) client có trên máy: Codex CLI, Claude Code, Grok CLI, Cursor — theo cái nào detect được.
3) Smoke test: list tools ≥ 20, gọi `fq_ping` ok=true; nếu có credential thì `get_stock_prices` FPT 7 ngày gần nhất ok.
4) Báo cáo path config đã sửa + lệnh verify. KHÔNG commit password lên git public.

## Repo
- GitHub: https://github.com/luongndcoder/fiinquant-python-mcp
- Clone (nếu chưa có): thư mục user chọn hoặc ~/Documents/AI/fiinquant-python-mcp
- Entry: `python -m fiinquant_mcp` (console script: `fiinquant-mcp`)
- Docs: README.md, config/mcp.*.example.*

## Quy tắc quan trọng
- FiinQuantX là SDK private: có thể đã cài sẵn (`import FiinQuantX`) hoặc user có file .whl. KHÔNG giả định pip public luôn có package.
- Dùng MỘT Python cố định (ưu tiên python3.11 hệ thống nếu đã có FiinQuantX): `which -a python3` + thử import.
- uvx isolate KHÔNG thấy site-packages hệ thống — nếu dùng uvx phải `--with /path/to/FiinQuantX.whl`.
- Server name gợi ý: `fiinquant-sdk` (tránh đụng `fiinquant-local` = proxy official npx nếu đã có).
- Secrets: hỏi user USERNAME + PASSWORD FiinQuant (AskUserQuestion / prompt ẩn nếu tool hỗ trợ). Lưu vào env MCP config local only. Không echo password trong log/report nếu có thể.
- Free plan: set FIINQUANT_PLAN=free, FIINQUANT_ENFORCE_PLAN_LIMITS=true (history ≤31 ngày, rate limit local).

## Bước thực hiện (tuần tự)

### A. Detect
- OS, shell
- Python candidates + `import FiinQuantX` / `import fiinquant_mcp`
- Có sẵn: `codex`, `claude`, `grok`, Cursor config paths
- Repo local đã clone chưa?

### B. Install packages
1. Clone repo nếu thiếu.
2. Trên Python đã có FiinQuantX (hoặc cài wheel user cung cấp):
   `python -m pip install -e "/abs/path/fiinquant-python-mcp"`
3. Verify:
   `python -c "import FiinQuantX, fiinquant_mcp; print(fiinquant_mcp.__version__)"`

### C. Credentials
- Hỏi / nhận FIINQUANT_USERNAME, FIINQUANT_PASSWORD.
- Nếu user chưa đưa: vẫn đăng ký MCP nhưng smoke chỉ test fq_ping; ghi chú live data cần creds.

### D. Register MCP theo client có trên máy

#### Codex CLI (nếu có `codex`)
```bash
codex mcp remove fiinquant-sdk 2>/dev/null || true
codex mcp add fiinquant-sdk \
  --env FIINQUANT_USERNAME='<user>' \
  --env FIINQUANT_PASSWORD='<pass>' \
  --env FIINQUANT_PLAN=free \
  --env FIINQUANT_ENFORCE_PLAN_LIMITS=true \
  -- <PYTHON_ABS> -m fiinquant_mcp
codex mcp list | grep fiinquant
```
Config file: ~/.codex/config.toml → [mcp_servers.fiinquant-sdk]

#### Grok CLI (nếu có `grok`)
Edit ~/.grok/config.toml:
```toml
[mcp_servers.fiinquant]
command = "<PYTHON_ABS>"
args = ["-m", "fiinquant_mcp"]
enabled = true
startup_timeout_sec = 60
tool_timeout_sec = 120

[mcp_servers.fiinquant.env]
FIINQUANT_USERNAME = "<user>"
FIINQUANT_PASSWORD = "<pass>"
FIINQUANT_PLAN = "free"
FIINQUANT_ENFORCE_PLAN_LIMITS = "true"
```
Verify: `grok mcp doctor fiinquant`

#### Claude Code (nếu có `claude`)
- Ưu tiên project `.mcp.json` hoặc user MCP config mà Claude Code hỗ trợ trên máy này.
- Pattern stdio JSON (Claude Desktop / nhiều host):
```json
{
  "mcpServers": {
    "fiinquant-sdk": {
      "command": "<PYTHON_ABS>",
      "args": ["-m", "fiinquant_mcp"],
      "env": {
        "FIINQUANT_USERNAME": "<user>",
        "FIINQUANT_PASSWORD": "<pass>",
        "FIINQUANT_PLAN": "free",
        "FIINQUANT_ENFORCE_PLAN_LIMITS": "true"
      }
    }
  }
}
```
- Nếu CLI có `claude mcp add`: dùng tương đương command/args/env trên (đọc `claude mcp add --help` trước, đừng đoán flag sai).
- Paths thường gặp:
  - Project: `<repo>/.mcp.json` hoặc `.claude/settings.json` (theo version)
  - User: `~/.claude.json` / Claude Desktop config macOS
    `~/Library/Application Support/Claude/claude_desktop_config.json`

#### Cursor
- Merge vào Cursor MCP settings JSON (user hoặc project `.cursor/mcp.json` nếu dùng):
  cùng schema JSON như trên với `command`/`args`/`env`.
- Tham chiếu mẫu: repo `config/mcp.cursor.example.json`

### E. Smoke test (bắt buộc)
Chạy bằng MCP Python client hoặc subprocess:

```python
# pseudocode / script
# start: <PYTHON_ABS> -m fiinquant_mcp  with env
# initialize session
# list_tools -> expect >= 20 tools including get_stock_prices, fq_ping
# call fq_ping -> ok true
# if creds: call get_stock_prices tickers=["FPT"], from_date=today-7d, to_date=today
#   expect ok true OR clear AUTH/SDK error (not crash)
```

Hoặc one-liner style với mcp package nếu đã cài `mcp`.

### F. Báo cáo cho user (template)
```
## Install result
- Python: <path> (FiinQuantX: yes/no, fiinquant_mcp: version)
- Clients configured: Codex / Grok / Claude / Cursor (list)
- Config paths edited: ...
- Smoke: fq_ping=..., get_stock_prices=...
- Free plan: history ≤31d; some tools 403 on free (screen, breadth, moneyflow, basic_info)
- Next: mở session MỚI của client để load MCP; thử prompt:
  "Dùng get_stock_prices lấy OHLCV FPT 2 tuần gần nhất"
```

## Không làm
- Không force-push / không publish secret.
- Không xóa MCP server khác của user (đặc biệt `fiinquant-local` proxy) trừ khi user bảo.
- Không rewrite toàn bộ config.toml — chỉ thêm/cập nhật block fiinquant-sdk / fiinquant.
- Không cài global bừa nếu user đang dùng venv project có chủ đích — ưu tiên Python đã có FiinQuantX.

## Troubleshooting
| Lỗi | Xử lý |
|-----|--------|
| No module named FiinQuantX | Cài wheel / pip đúng Python; hoặc uvx --with wheel |
| No module named fiinquant_mcp | pip install -e repo trên Python đó |
| AUTH missing credentials | set env USERNAME/PASSWORD |
| History window exceeds 31d | rút ngắn from/to (free) |
| 403 / no permission | free API; tool path OK, cần gói cao hơn |
| uvx không thấy SDK | đừng dùng bare uvx; dùng python -m hoặc --with |

Bắt đầu: detect môi trường → cài package → hỏi credential nếu thiếu → register MCP → smoke → report.
```

---

## Short variant (1 đoạn, khi user đã có SDK + clone)

```text
Cài personal FiinQuant MCP từ https://github.com/luongndcoder/fiinquant-python-mcp vào máy này.
Dùng Python đã có `import FiinQuantX`. pip install -e repo. Đăng ký stdio MCP:
- Codex: codex mcp add fiinquant-sdk --env FIINQUANT_USERNAME=… --env FIINQUANT_PASSWORD=… --env FIINQUANT_PLAN=free -- <python> -m fiinquant_mcp
- Grok: block [mcp_servers.fiinquant] trong ~/.grok/config.toml (xem repo config/mcp.grok.example.toml)
- Claude/Cursor: JSON mcpServers.fiinquant-sdk command/args/env (config/mcp.cursor.example.json)
Hỏi tôi username/password FiinQuant nếu chưa có. Smoke: fq_ping + get_stock_prices FPT 7 ngày. Không đụng fiinquant-local. Report path config + kết quả test.
```

---

## Ghi chú maintainer

- Giữ file này sync với README multi-client + `config/mcp.*.example.*`.
- Khi đổi entrypoint/env vars: cập nhật prompt block ở trên.
```
