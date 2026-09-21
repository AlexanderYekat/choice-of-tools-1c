# r01 Unica apply dryRun on Designer 2.20 dump — 2026-09-21

Binary: `unica.exe` 0.12.0 debug, pinned `56a67d4a…`.
cwd: `.v8/work/simple-cf-220` (Designer dump, not the handwritten fixture).
Isolated `UNICA_PROVIDER_STATE_DIR`: `.v8/work/r01-apply-cf220/provider-state`.
docs skipped (`UNICA_SMOKE_SKIP_DOCS=1`). Publication not called.

| # | Call | Expected | Actual | Pass |
|---|---|---|---|---|
| 1 | `initialize` | unica | 0.12.0 | yes |
| 2 | `unica.apply` dryRun `props.set` Comment on `main:Document.ЗаказПокупателя` | preview plan | `ok=true`; `mode=preview`; `executable=true`; `rev` returned; summary «metadata apply plan prepared without publication» | yes |
| 3 | `unica.apply` without `ifRev` | fence | `bad_value` at `ifRev` | yes |
| 4 | dump fingerprint | unchanged | 17 files; `changed=[]` (`.build/unica` excluded) | yes |

On the handwritten dump the same dryRun was `invalid_source` (format 1.0).
Publication (`dryRun:false` + this `ifRev`) was not called.

Raw JSON: `r01-mcp-apply-cf220-simple.json`,
`r01-mcp-apply-cf220-initialize-simple.json`,
`r01-mcp-apply-cf220-dryrun-simple.json`,
`r01-mcp-apply-cf220-fence-simple.json`.
