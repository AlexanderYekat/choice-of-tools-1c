# r22 IB smoke on stand simple — 2026-09-21

Runner: `v8-runner` 0.5.1 via v8-harness `--stand simple`
Platform: `C:\Program Files\1cv8\8.3.27.1936` (strict)
Dump: `source-checkouts/simple1CAiConf` @ `1dbc395d`
IB: `C:\MyPtojects\choice-of-tools-1c\.v8\ib\simple\1Cv8.1CD`

No Vanessa, no YaXUnit, no Unica, no MCP.

| # | Command | Expected | Actual | Pass |
|---|---|---|---|---|
| 1 | `init` | empty file IB created | `ok=true`; `1Cv8.1CD` created in 40826 ms | yes |
| 2 | `build` | Designer load of XML dump | `ok=true`; full load 10622 ms | yes |
| 3 | `syntax designer-modules --server --thin-client` | JSON `status=clean`, 0 errors | `ok=true`; issues `[]`; errors 0 | yes |

Earlier `build` attempts failed and were not the recorded PASS:
- user `Админ` in overlay → «Пользователь ИБ не идентифицирован» (dump has no users);
- relative `source-checkouts/...` resolved against `.v8/stands/simple/` → file not found.

Raw JSON: `r22-init-simple.json`, `r22-build-simple.json`, `r22-syntax-modules-simple.json`.
