# Brainstorm: Personal FiinQuant MCP

**Date:** 2026-07-15  
**Slug:** `20260715-fiinquant-personal-mcp`  
**Status:** Approved (Option B — Resilient facade) — 2026-07-15  
**Lane:** Greenfield personal tool (không phải Mobio backend service)

---

## Vấn đề + yêu cầu

### Vấn đề
MCP official của FiinQuant **không tin cậy** (crash / hang / timeout / tool fail ngẫu nhiên), trong khi **Python SDK `fiinquant` dùng ngoài MCP vẫn ổn**. User muốn tự build MCP personal, bám tài liệu [FiinQuant Document](https://fiinquant.vn/Home/Document), tool surface **đa dạng ~ parity official**.

### Yêu cầu (đã chốt trong clarify)
| # | Yêu cầu | Nguồn |
|---|---------|--------|
| 1 | Reliability-first (không crash process, fail có envelope rõ) | user-confirmed |
| 2 | Tool surface đa dạng giống MCP official (không thin 1–2 tool) | user-confirmed |
| 3 | Data path qua SDK `fiinquant` (đã proven) | user-confirmed |
| 4 | Host: Claude Desktop / Cursor local, transport **stdio** | user-confirmed |
| 5 | Personal use — single user credentials | inferred |

### Ngoài scope v1 (YAGNI)
- Remote HTTP/SSE multi-user server
- Multi-tenant / merchant isolation (không áp dụng)
- UI dashboard, backtest engine, strategy execution
- Thay thế toàn bộ product FiinQuant — chỉ lớp MCP

---

## Stack context

| Layer | Choice (proposed) | Note |
|-------|-------------------|------|
| Language | Python 3.11+ | Match `fiinquant` SDK |
| MCP framework | FastMCP (hoặc official `mcp` SDK) | Rapid tool definition, stdio |
| Data | `fiinquant` Python package | Source of truth cho calls |
| Transport | stdio | Claude Desktop / Cursor |
| Config | env vars + optional `.env` | credentials, timeouts |
| Test | pytest + contract tests per tool | mock SDK boundary |
| Docs ref | https://fiinquant.vn/Home/Document | inventory tool groups ở phase plan |

**Repo hiện tại:** empty greenfield — chưa có code/docs/context.

---

## Existing code liên quan

- **Trong repo:** không có (workspace rỗng).
- **Ngoài repo (user):** SDK `fiinquant` đã login + call ổn → **reuse 100% data path**, chỉ thay lớp MCP.
- **Official MCP FiinQuant:** treat as *negative reference* (tool surface gợi ý parity; **không** copy reliability pattern).

---

## Findings

| # | Câu hỏi | Answer | Status | Source |
|---|---------|--------|--------|--------|
| 1 | Backend/Mobio signal? | Không — greenfield personal MCP | verified-by-source | empty workspace |
| 2 | Pain chính official MCP? | Unreliable / lỗi runtime | user-confirmed | clarify Q1 |
| 3 | Workflow v1 / tool surface? | Đa dạng tool ~ parity official MCP | user-confirmed | clarify Q2 (Other) |
| 4 | Data access ổn định? | Python package `fiinquant` SDK OK | user-confirmed | clarify Q3 |
| 5 | Host runtime? | Claude Desktop / Cursor local (stdio) | user-confirmed | clarify Q4 |
| 6 | Inventory tool exact từ Document? | Chưa — defer sang research/plan | deferred | — |
| 7 | Auth credential shape (user/pass vs token)? | Chưa chốt chi tiết — giả định env theo SDK | deferred | chốt ở `/be-plan` |

---

## Approaches

### Option A — Thin FastMCP wrap SDK (KISS max)

Map tool MCP 1:1 → hàm SDK. Login 1 lần lúc process start từ env. Mỗi tool = `try/except` + timeout thô.

- **Pros:** ship nhanh nhất (1–2 ngày cho vài tool core); dễ hiểu; ít abstraction.
- **Cons:** khi tool surface “đa dạng” → file phình, session/re-auth lỏng, response quá lớn làm LLM/client treo, khó test theo domain, dễ lặp lại lỗi official MCP (thiếu resilience layer).
- **Fit:** spike / PoC 3–5 tool. **Không đủ** nếu parity rộng là goal cứng.

### Option B — Resilient facade + domain tools (Recommended)

Kiến trúc 4 lớp, **vẫn dùng SDK** làm data plane:

1. **Config/Auth** — env credentials, timeout budgets, log level  
2. **Gateway** — singleton session SDK, lazy login, re-auth on session expire, hard timeout per call, never raise uncaught ra process  
3. **Domain tools** — group theo capability (market/OHLCV, fundamental, screening, metadata…) map từ Document + surface official  
4. **MCP presentation** — FastMCP stdio; response normalizer (JSON-serializable, size budget/truncate, error envelope chuẩn)

Reliability kit tối thiểu:
- `timeout_s` per tool (default + override)
- error envelope: `{ok:false, code, message, hint}` — tool fail ≠ process die
- response size budget (tránh hang client vì dump DataFrame khổng lồ)
- health tool: `fiinquant_ping` / `session_status`
- structured log local (stderr), không log password

Phased delivery **bên trong** skeleton B:
- P0: skeleton + auth + health + 3–5 tool “hottest”  
- P1: mở rộng domain theo Document / parity official  
- P2: cache optional, rate-limit soft, richer indicators  

- **Pros:** đúng pain (reliability); scale được tool đa dạng; testable (mock Gateway); tránh lặp lỗi official.
- **Cons:** upfront structure nhiều hơn A (~0.5–1 ngày skeleton); phải inventory tool có chủ đích (không gen mù).

### Option C — Clone/mirror official MCP surface rồi “vá reliability”

Inspect package/binary MCP official (nếu có trên PyPI/npm), copy schema tool 1:1, chỉ thay error handling / timeout.

- **Pros:** parity tool name nhanh nếu source mở.
- **Cons:** license/ToS risk; inherit bad tool design; nếu closed → dead end; vẫn không giải root cause nếu architecture gốc kém; effort reverse-engineer có thể > build B.
- **Fit:** chỉ khi official MCP **open source + license OK** và schema đã tốt — hiện **chưa verified**.

---

## Trade-off matrix

| Criterion | A Thin wrap | B Resilient facade | C Mirror official |
|-----------|-------------|--------------------|-------------------|
| Performance (latency) | Tốt (direct) | Tốt (+ overhead nhỏ) | Phụ thuộc code gốc |
| Reliability | Yếu khi scale tools | **Mạnh** (design goal) | Vá từng chỗ — không đều |
| Complexity | Thấp | Trung bình | Trung bình–cao (unknown) |
| Tool surface đa dạng | Khó maintain | **Có phase rõ** | Nhanh nếu source mở |
| Maintenance | Kém dài hạn | **Tốt** | Phụ thuộc upstream |
| Migration risk | Thấp | Thấp (greenfield) | License / reverse risk |
| Team skill fit | Python MCP cơ bản | Python + clean architecture | Reverse + MCP |
| Time to first useful | **Nhanh nhất** | Nhanh (P0) rồi mở rộng | Không chắc |
| SDK reuse | Có | **Có** | Có (thường) |

---

## Hướng đề xuất + lý do + caveats

### Preferred: **Option B — Resilient facade + domain tools**

**Lý do:**
1. Pain đã chốt = **runtime reliability**, không phải thiếu API → cần **Gateway + error/timeout/size policy**, không chỉ “thêm tool”.
2. SDK đã ổn → **không** viết lại HTTP client từ Document (YAGNI); Document dùng để **đặt tên/group tool + param semantics**.
3. User muốn surface **đa dạng** → cần domain modules + phase; A sẽ thối code khi tool count tăng.
4. stdio personal local → B đủ, không cần remote complexity.

**Caveats / điều kiện áp dụng:**
- Phải **inventory tool** (Document + surface MCP official) trước khi code P1 — không guess 50 tool.
- Mỗi tool trả về **LLM-friendly** (summary + optional raw sample), không dump full DF.
- Credentials **chỉ** env / local config; không commit secret.
- Tuân ToS/license FiinQuant + SDK — personal use; không redistribute data/API key.

**Khi nào chọn option khác:**
- **A** nếu chỉ cần spike 1 buổi chứng minh login+1 tool trước khi commit B (có thể làm A *bên trong* skeleton B P0).
- **C** chỉ sau khi verify official MCP open source + license cho phép + schema chất lượng — hiện không đủ evidence.

---

## Self-review inline

| Check | Result |
|-------|--------|
| Tenant isolation | N/A — personal single-user |
| Schema/migration | N/A — no DB v1 (optional local cache file later) |
| Event schema | N/A |
| Breaking change | N/A — greenfield; tool names có thể align official để drop-in config |
| PII / NĐ 13 | Credentials = secret; không log password; không gửi data lên third-party ngoài FiinQuant + local LLM client |
| Observability | stderr structured log + health tool; không cần Mobio-Trace-ID |
| YAGNI | Pass nếu không remote server / multi-tenant / full platform |
| KISS | Pass nếu P0 ≤ 5 tool + Gateway tối thiểu |
| DRY | Pass nếu mọi SDK call đi qua Gateway (1 chỗ timeout/auth/error) |

---

## Rủi ro + mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Session SDK expire giữa chừng | Tool fail hàng loạt | Re-auth trong Gateway; health tool |
| Response quá lớn (history dài) | Client hang / context overflow | Size budget, pagination params, head/tail sample |
| Official MCP tool list mơ hồ | Scope creep | Inventory có owner ở `/be-plan`; P0 fixed list |
| SDK API đổi version | Break tools | Pin version `fiinquant` trong deps; smoke test |
| Hang sync SDK trong event loop | MCP freeze | `asyncio.to_thread` + hard timeout |
| ToS / license SDK | Legal | Personal use; đọc license trước publish nếu public repo |
| Empty repo, chưa research Document | Sai tool params | `/be-research` inventory API groups trước plan chi tiết tool |

---

## Tiêu chí thành công + cách verify

| # | Success criteria | Verify |
|---|------------------|--------|
| 1 | Process MCP không chết khi 1 tool lỗi | Unit test: SDK raise → envelope, process còn sống |
| 2 | Không hang vô hạn | Call mock sleep > timeout → error `TIMEOUT` trong budget (vd 30s) |
| 3 | Login + 1 market tool e2e với credential thật | Manual: Cursor/Desktop list tools + invoke OK |
| 4 | Response parse được, size bounded | Contract test: max chars / max rows |
| 5 | P0 tool set documented + config sample `mcp.json` | README + example config |
| 6 | Mở rộng thêm domain tool không sửa Gateway core | Thêm 1 tool file + test, không đụng auth |

---

## Quyết định chưa chốt

1. **Danh sách tool P0/P1 exact** (cần inventory Document +/hoặc list tool MCP official).
2. **Credential shape** (username/password vs token) — follow SDK convention.
3. **FastMCP vs raw `mcp` SDK** — prefer FastMCP trừ khi constraint runtime.
4. **Publish private git vs local-only** — ảnh hưởng license/secret hygiene.
5. Có cần **cache** OHLCV local không (default: không ở v1).

---

## Bước tiếp theo

1. **User Review Gate** — approve / reject brainstorm này.
2. Nếu approve → **`/be-research`** (khuyến nghị): inventory FiinQuant Document + SDK public surface + (nếu được) tool list MCP official → `plans/.../research/`.
3. **`/be-plan`** — phase P0/P1, file map, test plan, mcp.json sample.
4. **`/be-ship`** hoặc implement theo plan (TDD: Gateway tests trước tools).
5. Optional: `/be-preview` xem architecture diagram.

---

## Recommendation ADR (short)

```
Status: Proposed
Decision: Build personal FiinQuant MCP as Resilient Facade (Option B)
          over working fiinquant Python SDK; stdio; Claude Desktop/Cursor.
Why: Official MCP unreliability is a presentation/process problem;
     data plane already works. Need timeout, error envelope, size budget,
     session re-auth, domain-phased tools for broad surface without chaos.
Reject: Thin-only long-term (A), blind mirror of official package (C)
         until open-source/license verified.
```
