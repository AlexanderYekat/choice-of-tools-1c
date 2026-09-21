# r15 MCP dump-only smoke on stand simple — 2026-09-21

Binary: `C:\Users\Enduro\Documents\1c\Tools\bsl-indexer\bsl-indexer.exe`
Release: GitHub `Regsorm/code-index-mcp` v1.4.0 / commit `4bde72b60a09187c0667d451a02c7be5e0169835`
Dump: `source-checkouts/simple1CAiConf` @ `1dbc395d764773927684acd9ff75bf8f8e58cd56`
Isolated `CODE_INDEX_HOME`: `.v8/work/r15-mcp/home` (not the user profile).
HTTP MCP on an ephemeral `127.0.0.1` port (`serve --transport http --config daemon.toml`).
No infobase, no Unica, no Vanessa, no YaXUnit, no facade.

`daemon run` on Windows spawned a child and let the parent exit 0; health/IPC
was `http://127.0.0.1:60114`. Processes were stopped with `daemon stop` after
the checks. Reused the existing `<dump>/.code-index/index.db` from the CLI smoke
(21 files, 0 changed).

| # | Call | Expected | Actual | Pass |
|---|---|---|---|---|
| 1 | `health` | daemon online; alias `simple` ready | `daemon.status=online`; path ready | yes |
| 2 | `tools/list` | 13 1С-tools advertised | 33 names; 13 BSL present; missing `[]` | yes |
| 3 | `get_object_structure` `Document.ЗаказПокупателя` | attributes `СуммаДокумента`, TCH `Товары` | both; also `Контрагент` | yes |
| 4 | `get_form_handlers` `ФормаДокумента` | OnChange `ТоварыКоличествоПриИзменении` and `ТоварыЦенаПриИзменении` | 2 handlers; XML `OnChange` localized to `ПриИзменении`; owner `Documents.ЗаказПокупателя` | yes |
| 5 | `get_register_writers` `AccumulationRegister.ЗаказыПоКонтрагентам` | writer `Document.ЗаказПокупателя` | `writers_count=1` that document | yes |
| 6 | `get_event_subscriptions` | empty: dump has no `EventSubscriptions/` | `count=0`, `subscriptions=[]` | yes |
| 7 | `search_function` `РассчитатьСуммуДокумента` | MCP hit on same dump | hit | yes |

Live `tools/list` names: `r15-mcp-tools-list-simple.json` (20 core + 13 BSL = 33).
`[tools].enabled` whitelist was not exercised. `daemon_offline` without a daemon
was not re-tested.

Raw JSON: `r15-mcp-simple.json`, `r15-mcp-health-simple.json`,
`r15-mcp-tools-list-simple.json`, `r15-mcp-object-structure-simple.json`,
`r15-mcp-form-handlers-simple.json`, `r15-mcp-register-writers-simple.json`,
`r15-mcp-event-subscriptions-simple.json`, `r15-mcp-search-function-simple.json`.
