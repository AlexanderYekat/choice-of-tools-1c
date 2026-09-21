# r15 CLI smoke on stand simple — 2026-09-21

Binary: `C:\Users\Enduro\Documents\1c\Tools\bsl-indexer\bsl-indexer.exe`
Release: GitHub `Regsorm/code-index-mcp` v1.4.0 / commit `4bde72b60a09187c0667d451a02c7be5e0169835`
Dump: `source-checkouts/simple1CAiConf` @ `1dbc395d764773927684acd9ff75bf8f8e58cd56`
No infobase, no daemon, no MCP.

| # | Command | Expected | Actual | Pass |
|---|---|---|---|---|
| 1 | `index --path <dump>` | exit 0; `index.db`; 21 files; 7 procedures | exit 0; db 598016 bytes; stdout «Найдено файлов: 21», «этап 18 … 7 процедур»; stderr processor `bsl` | yes |
| 2 | `search-function --path <dump> РассчитатьСумму` | JSON includes `РассчитатьСуммуСтроки` and `РассчитатьСуммуДокумента` | 4 hits; both names present; also FTS body hits `ТоварыКоличествоПриИзменении` / `ТоварыЦенаПриИзменении` | yes |
| 3 | `get-function --path <dump> РассчитатьСуммуДокумента` | one procedure, body with `Объект.СуммаДокумента` | array length 1; name and body match | yes |
| 4 | `get-callers --path <dump> РассчитатьСуммуСтроки` | callers `ТоварыКоличествоПриИзменении` and `ТоварыЦенаПриИзменении` | two edges, those callers, callee match | yes |
| 5 | `search-function --path <dump> НесуществующаяФункцияXYZ123` | empty list | stdout `[]` | yes |
| 6 | `stats --path <dump>` | files 21, functions 7 | stdout «Файлов: 21», «Функций: 7» | yes |

CLI subcommands are hyphenated (`search-function`), not MCP underscores.

Raw JSON: `r15-index-simple.json`, `r15-search-function-simple.json`, `r15-get-function-simple.json`, `r15-get-callers-simple.json`, `r15-search-function-negative.json`, `r15-stats-simple.json`.
Expected procedure names: `../sources/simple1c-bsl-procs.txt`.
