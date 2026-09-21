# r01 Unica apply dryRun + docs smoke on stand simple — 2026-09-21

Binary: locally built `unica.exe` 0.12.0 debug from pinned commit
`56a67d4a460c97101b6b542b4fe940298ab0edd8` (not GitHub release v0.12.3).
Isolated `UNICA_PROVIDER_STATE_DIR`: `.v8/work/r01-apply/provider-state`.
Dump: `source-checkouts/simple1CAiConf` @ `1dbc395d`.
cwd of MCP = dump root. `dryRun:false` with a real `ifRev` was **not**
called. No `unica.run`, no Vanessa, no YaXUnit, no facade, no 1C client.

Stdio JSON-RPC (`initialize` 2025-06-18, `tools/call`). Client:
`r01-mcp-apply-simple.py`. SHA-256 fingerprint of 22 dump files (excluding
`.build` / `.code-index`) taken before and after.

| # | Call | Expected | Actual | Pass |
|---|---|---|---|---|
| 1 | `initialize` | `serverInfo.name=unica` | `unica` 0.12.0 | yes |
| 2 | `unica.apply` `dryRun:true` `props.set` Comment on `main:Document.ЗаказПокупателя` | preview **or** named refusal; no publish | structured `ok=false`; `invalid_source` / `fixSource`: Configuration.xml export format 1.0 is older than writable profile 2.20 for 8.3.27 | yes (tool callable; node not writable on this dump) |
| 3 | `unica.apply` without `ifRev` (publish omitted `dryRun`) | fence | `ok=false`; `bad_value` at `ifRev`: «apply requires ifRev from a prior dryRun preview» | yes |
| 4 | `unica.docs` `query=НаборЗаписей` | completed sections | first envelope is Task `working`; after 5× `unica.task.result` (waitMs≤7000): `ok=true`, 5 sections, 80 hits, `applicableVersion` 8.3.27.1936 on syntax-help | yes |
| 5 | `unica.docs` blank query | refusal | `ok=false`; `bad_value`: «docs query must be non-blank» | yes |
| 6 | dump fingerprint | unchanged | `changed=[]`; 22 files | yes |

Docs sections after poll:

- `platform-syntax-help` / `syntax-context` — ok (vendor, ru)
- `platform-syntax-help` / `platform-guides` — ok
- `kb-1ci` / `kb-developer-guide` — ok
- `kb-1ci` / `kb-administrator-guide` — unavailable (`version-missing`)
- `v8std` / `public-standards` — ok (community)

Raw JSON: `r01-mcp-apply-simple.json`, `r01-mcp-apply-initialize-simple.json`,
`r01-mcp-apply-dryrun-simple.json`, `r01-mcp-apply-fence-simple.json`,
`r01-mcp-docs-working-simple.json`, `r01-mcp-docs-simple.json`,
`r01-mcp-docs-blank-simple.json`.

`ConfigDumpInfo.xml` header is `version="2.20"`; Unica apply still classifies
the writable profile from `Configuration.xml` as format 1.0. This is the
hand-written simple1CAiConf dump, not a Designer re-export. Publication was
not attempted. Dual-workspace still NOT_RUN.
