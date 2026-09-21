# r01 Unica dual-workspace smoke — 2026-09-21

Binary: locally built `unica.exe` 0.12.0 debug from pinned commit
`56a67d4a460c97101b6b542b4fe940298ab0edd8`. Isolated
`UNICA_PROVIDER_STATE_DIR`: `.v8/work/r01-dual/provider-state`.
`UNICA_DAEMON_IDLE_GRACE_MS=120000`. No `apply`, no `unica.run`,
no facade, no 1C client.

Two stdio MCP processes stayed connected together:

| Client | cwd | stdio pid |
|---|---|---|
| A | `source-checkouts/simple1CAiConf` | 32052 |
| B | `.v8/work/simple-cf-220` | 33900 |

Shared daemon: one `unica.exe --daemon` pid **23920** (parent is not
either stdio pid). Same pid before and after client B initialized.
`endpoint.json` is exclusively locked while that process lives, so the
pid was taken from `Win32_Process`, not from the file.

| # | Call | Expected | Actual | Pass |
|---|---|---|---|---|
| 1 | `initialize` A | `serverInfo.name=unica` | `unica` 0.12.0 | yes |
| 2 | daemon after A | one `--daemon` for this state root | pid 23920 | yes |
| 3 | `initialize` B while A is connected | `serverInfo.name=unica` | `unica` 0.12.0 | yes |
| 4 | daemon after B | same pid; both stdio pids differ | 23920; stdio 32052 and 33900 | yes |
| 5 | `unica.view {}` A | workspaceRoot = handwritten dump | `ok=true`; root `simple1CAiConf` | yes |
| 6 | `unica.view {}` B | workspaceRoot = cf220 | `ok=true`; root `.v8/work/simple-cf-220` | yes |
| 7 | `unica.view` document A | Comment empty | `Comment=""`; rev `6ae3445b…` | yes |
| 8 | `unica.view` document B | Comment is the publish marker | `Comment=r01-publish-ifRev-20260921`; rev `032c1542…` | yes |
| 9 | `unica.view` document A again | A unchanged after B | Comment still empty; same rev `6ae3445b…` | yes |
| 10 | receipt ledger | one core identity, two scopes | identity `884b7618…`; scopes `848996cf…` (A) and `fdf73748…` (B) | yes |
| 11 | document XML sha256 | both files unchanged | handwritten `00f4771e…`; cf220 `1275cfce…` | yes |

Address on both dumps: `main:Document.ЗаказПокупателя`.
Scope hashes are `sha256("unica.request-scope.v1\0" || u32be(len) || cwd utf-8)`
and match the receipt `requestScopeHash` values. Active receipt count
was 9 because an earlier probe in this same state directory left 5
receipts; the unique scopes were still exactly these two cwd hashes.

Client: `r01-mcp-dual-simple.py`. Summary: `r01-mcp-dual-simple.json`.
Raw views: `r01-mcp-dual-view-a.json`, `r01-mcp-dual-view-b.json`,
`r01-mcp-dual-doc-a.json`, `r01-mcp-dual-doc-b.json`,
`r01-mcp-dual-doc-a-again.json`.

Dual-IB and two `source-set` entries in one yaml were not executed.
The cf220 dump still carries the smoke Comment from `run-r01-apply-publish`.
