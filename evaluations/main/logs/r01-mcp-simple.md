# r01 Unica dump-only MCP smoke on stand simple — 2026-09-21

Binary: locally built `unica.exe` 0.12.0 debug from pinned commit
`56a67d4a460c97101b6b542b4fe940298ab0edd8` (not GitHub release v0.12.3,
SHA `f6d23068…` of 2026-08-19). Isolated worktree
`.v8/work/r01/unica-src`; `CARGO_TARGET_DIR` `.v8/work/r01/target`.
Rustc `1.98.1` (default 1.84.1 cannot parse `edition2024` crates).
No `cargo install`, no `~/.unica`.
Isolated `UNICA_PROVIDER_STATE_DIR`: `.v8/work/r01/provider-state`.
Dump: `source-checkouts/simple1CAiConf` @ `1dbc395d`.
cwd of MCP = dump root. No apply, no `unica.run`, no Vanessa, no
YaXUnit, no facade, no 1C client.

Stdio JSON-RPC (`initialize` 2025-06-18, `tools/list`, `tools/call`).
`UNICA_DAEMON_IDLE_GRACE_MS=8000`.

First attempt failed before handshake: debug binary 56 MiB, daemon
`CONNECT_TIMEOUT` 5 s, stderr
`protocol-v5 deadline expired during spawn lock`. Retry after warmup
passed.

| # | Call | Expected | Actual | Pass |
|---|---|---|---|---|
| 1 | `initialize` | `serverInfo.name=unica` | `unica` 0.12.0; protocol `2025-06-18` | yes |
| 2 | `tools/list` | exactly 11 compatibility names | 11; missing `[]`; unexpected `[]` | yes |
| 3 | `unica.view {}` | autodetect dump without yaml | `ok=true`; `config.state=autodetected`; source-set `main` path `.`; evidence `Configuration.xml`; yaml recipe only in `data.setup`, file not written | yes |
| 4 | `unica.view {at: main:Document.ЗаказПокупателя}` | readable document | `ok=true`; title «Заказ покупателя»; branches Attribute 2, TabularSection 1, Form 2, Module 2. Default view is a summary; attribute names are not expanded until a child `at` | yes |
| 5 | `unica.check {at: main:Document.ЗаказПокупателя}` | tool answers (admission/validation) | structured `ok=false`; `provider_unavailable` / `source_unreadable`: «outside the supported 2.20 export format». `ConfigDumpInfo.xml` header is `version="2.20"`; the reader still refused this hand-written dump | yes (tool callable; node not admitted) |
| 6 | `unica.view {at: main:Document.НесуществующийОбъектXYZ}` | refusal | `ok=false`; `not_found` | yes |

Live `tools/list` names: `r01-mcp-tools-list-simple.json`.
Raw JSON: `r01-mcp-simple.json`, `r01-mcp-initialize-simple.json`,
`r01-mcp-view-workspace-simple.json`, `r01-mcp-view-document-simple.json`,
`r01-mcp-check-document-simple.json`, `r01-mcp-view-missing-simple.json`.
Client: `r01-mcp-smoke.py`.

`unica.apply`, `unica.docs` and dual-workspace were not called.
`infobase.configured=false` in bootstrap (dump-only cwd; stand IB not
in this process).
