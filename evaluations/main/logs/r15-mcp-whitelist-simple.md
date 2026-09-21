# r15 MCP `[tools].enabled` whitelist on stand simple — 2026-09-21

Binary: `C:\Users\Enduro\Documents\1c\Tools\bsl-indexer\bsl-indexer.exe`
Release: GitHub `Regsorm/code-index-mcp` v1.4.0 / commit `4bde72b60a09187c0667d451a02c7be5e0169835`
Dump: `source-checkouts/simple1CAiConf` @ `1dbc395d764773927684acd9ff75bf8f8e58cd56`
Isolated `CODE_INDEX_HOME`: `.v8/work/r15-whitelist/home` (not the user profile, not the earlier r15-mcp home).
HTTP MCP `serve --transport http --config daemon.toml` on ephemeral `127.0.0.1:54852/mcp`.
No `--path`: `serve --help` of this binary says a simultaneous `--path` ignores the config file.
No infobase, no Unica, no Vanessa, no facade. Dump XML was not edited.

Whitelist in `daemon.toml` `[tools].enabled`: the explore subset
`search_function`, `get_function`, `get_callers`, `read_file`,
`get_object_profile`, `get_form_handlers`, `get_event_subscriptions`,
`get_register_writers`, `find_references`, plus the unknown name
`not_a_real_tool`.

`daemon run` spawned a child (parent exit 0); status `running`, path
`ready`. Processes stopped with `daemon stop` after the checks.

| # | Call | Expected | Actual | Pass |
|---|---|---|---|---|
| 1 | `daemon status` | path ready | `running`, alias path ready | yes |
| 2 | HTTP listen | port accepts | `127.0.0.1:54852` | yes |
| 3 | `tools/list` | exactly the 9 known names | count=9, missing=[], extra=[] | yes |
| 4 | startup log | warning for the typo | `неизвестные имена tools (опечатка?): ["not_a_real_tool"]`; `9 известных tools разрешены (10 в списке)` | yes |
| 5 | `get_form_handlers` | both OnChange handlers | `ТоварыКоличествоПриИзменении`, `ТоварыЦенаПриИзменении` | yes |
| 6 | `tools/call grep_code` | JSON-RPC -32602 | `tool 'grep_code' is disabled by [tools].enabled whitelist in daemon.toml` | yes |
| 7 | `tools/call get_object_structure` | same refusal for a registered tool outside the list | `tool 'get_object_structure' is disabled by [tools].enabled whitelist` | yes |

`not_a_real_tool` was not advertised. `health`, `grep_code` and
`get_object_structure` were absent from `tools/list`. Empty `enabled`
was not re-tested; the earlier run without the section listed 33 names.
stdio transport was not re-tested. `--path` overriding `--config` was
not re-tested.

Raw JSON: `r15-mcp-whitelist-simple.json`,
`r15-mcp-whitelist-tools-list.json`,
`r15-mcp-whitelist-form-handlers.json`,
`r15-mcp-whitelist-denied.json`.
Serve log: `.v8/work/r15-whitelist/serve.log`.
