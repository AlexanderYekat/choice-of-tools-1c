# r01 Unica apply publish on Designer 2.20 dump — 2026-09-21

Binary: `unica.exe` 0.12.0 debug, pinned `56a67d4a…`.
cwd: `.v8/work/simple-cf-220` (Designer dump). Isolated
`UNICA_PROVIDER_STATE_DIR`: `.v8/work/r01-apply-publish/provider-state`.
`source-checkouts/simple1CAiConf` and IB `.v8/ib/simple` were not written.

| # | Call | Expected | Actual | Pass |
|---|---|---|---|---|
| 1 | `initialize` | unica | 0.12.0 | yes |
| 2 | `unica.apply` dryRun `props.set` Comment=`r01-publish-ifRev-20260921` on `main:Document.ЗаказПокупателя` | preview + `rev` | `ok=true`; `mode=preview`; `executable=true`; `rev` `unica-source-sha256-v1:1:f83d6c98…` | yes |
| 3 | dump fingerprint after dryRun | unchanged | `changed=[]` | yes |
| 4 | `unica.apply` `dryRun:false` + that `ifRev` | publication | `ok=true`; `mode=published`; summary «metadata apply published atomically»; new `rev` `…032c1542…` | yes |
| 5 | dump Comment | XML contains marker | only `Documents/ЗаказПокупателя.xml` changed; `<Comment>r01-publish-ifRev-20260921</Comment>` | yes |
| 6 | same `ifRev` after publish | stale fence | `ok=false`; `stale_revision`; expected `f83d6c98…`, admitted `032c1542…` | yes |

6/6 PASS (`run-r01-apply-publish`). Script:
`r01-mcp-apply-publish-simple.py`. The work dump now carries the smoke
Comment; handwritten fixture and IB were left intact.

Raw JSON: `r01-mcp-apply-publish-simple.json`,
`r01-mcp-apply-publish-initialize-simple.json`,
`r01-mcp-apply-publish-dryrun-simple.json`,
`r01-mcp-apply-publish-publish-simple.json`,
`r01-mcp-apply-publish-stale-simple.json`.
