# r20 Answer42 dual live Test Client — 2026-09-21

Package: PyPI `answer42==0.5.3` (pinned SHA `0406669a…`, ветка `beta`).
Один stdio MCP: `answer42 --disable-rag --disable-credential-store --tool-profile ui`.
Изолированный `ONEC_MCP_DATA_DIR`: `.v8/work/r20-dual/data`.
`ONEC_PLATFORM_DIR`: `C:\Program Files\1cv8\8.3.27.1936\bin`.
ИБ A: `.v8/ib/simple`. ИБ B: файловая копия `.v8/work/r20-dual/ib-b` (синоним конфигурации тот же).
Фасад, Unica, Vanessa, `click_button` и публикация `apply` не вызывались.
Процесс скрипта: ~314 с, exit code 1. Повторный запуск 1С не делался.

| # | Call | Expected | Actual | Pass |
|---|---|---|---|---|
| 1 | `initialize` | Answer42 | `name=Answer42`; protocol `2025-11-25` | yes |
| 2 | `tools/list` | session tools, без RAG | **103**; `rag_query` нет | yes |
| 3 | `start_session` `dual-a` | Test Client на simple | `base_url` simple; `connection_value` `http://127.0.0.1:8424`; test port 3058 | yes |
| 4 | `start_session` `dual-b` при живой A | Test Client на копии | `base_url` `ib-b`; `http://127.0.0.1:10104`; test port 3098 | yes |
| 5 | разные URL ibsrv | два http | 8424 и 10104 | yes |
| 6 | `sessions_list` | две живые сессии | `count=2`; `base_url` каждой — своя ИБ; `testclient_alive` оба | yes |
| 7 | `session_status` | свой путь, ключ и порт | пути и порты 8424/10104 разошлись; ключи содержат свои пути. Скрипт пометил FAIL: сравнивал `as_posix()` (`/`) с ключом на `\` | yes, по JSON |
| 8 | `active_window` `dual-a` | окно при живой B | title «Простая конфигурация» | yes |
| 9 | `active_window` `dual-b` | окно при живой A | title «Простая конфигурация» | yes |
| 10 | `standalone.yaml` | оба пути в data dir | 4 yaml; оба пути ИБ есть | yes |
| 11 | `stop_session` `dual-a` | останов только A | `stopped=true`; shared-file-ibsrv A снят | yes |
| 12 | после stop A | B жива, A нет | `A.running=false`, `active_window` A — `isError`; B path = `ib-b`, title тот же | yes |

Заголовок окна не различает цели: копия несёт тот же синоним. Разведение — `base_url`, `shared_file_key`, порт file-ibsrv и то, что останов A не гасит B.

`shared_file_key` из сохранённого статуса: `file:C:\Program Files\1cv8\8.3.27.1936\bin:` плюс путь своей ИБ. После прогона процессов 1cv8c/ibsrv/ibcmd не осталось.

Raw JSON: `r20-mcp-dual.json`, `r20-mcp-dual-initialize.json`,
`r20-mcp-dual-start-dual-a.json`, `r20-mcp-dual-start-dual-b.json`,
`r20-mcp-dual-sessions-both.json`, `r20-mcp-dual-status-dual-a.json`,
`r20-mcp-dual-status-dual-b.json`, `r20-mcp-dual-window-dual-a.json`,
`r20-mcp-dual-window-dual-b.json`, `r20-mcp-dual-standalone.json`,
`r20-mcp-dual-stop-dual-a.json`, `r20-mcp-dual-status-after-stop-a.json`,
`r20-mcp-dual-window-after-stop-a.json`.
Скрипт: `r20-mcp-dual.py` (сравнение ключа поправлено на обратные слэши после прогона, без повтора).
