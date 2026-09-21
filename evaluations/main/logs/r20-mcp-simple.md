# r20 Answer42 stdio MCP smoke on stand simple — 2026-09-21

Package: PyPI `answer42==0.5.3` (pinned SHA `0406669a…`, ветка `beta`).
Venv: `.v8/work/r20-mcp/venv` (не pipx, не профиль пользователя).
CLI: `answer42 --disable-rag --disable-credential-store --tool-profile ui`.
Изолированный `ONEC_MCP_DATA_DIR`: `.v8/work/r20-mcp/data`.
`ONEC_PLATFORM_DIR`: `C:\Program Files\1cv8\8.3.27.1936\bin`.
ИБ: `.v8/ib/simple` (без пользователей). Фасад, Unica, Vanessa, публикация `apply` не вызывались.

Первый `start_session` собрал менеджерскую ИБ из packaged `MCPTestManager.cf` через `ibcmd`, поднял `ibsrv` и тонкий `/TESTMANAGER` + `/TESTCLIENT`. Живое окно: «Простая конфигурация». Сессия остановлена `stop_session`; leftover 1С-процессов не осталось.

| # | Call | Expected | Actual | Pass |
|---|---|---|---|---|
| 1 | `initialize` | Answer42 | `name=Answer42`; protocol `2025-11-25`; version пустой | yes |
| 2 | `tools/list` (`ui` + `--disable-rag`) | subset, RAG нет, `< 122` | **103** имён; `start_session`/`active_window`/`stop_session`/`screenshot` есть; `rag_query` нет | yes |
| 3 | `start_session` `simple-smoke` + путь файловой ИБ | сессия к simple | `session_id=simple-smoke`; client connected; `rag_enabled=false`; ~104 с (IB менеджера 46 с) | yes |
| 4 | `active_window` | непустое окно | title «Простая конфигурация»; type тестируемое окно | yes |
| 5 | `screenshot` | путь PNG, не base64 | path `.v8/work/r20-mcp/screenshots/simple-smoke.png`; 296716 bytes; fallback `full_display` (геометрия окна 1С не найдена) | yes |
| 6 | повторный `start_session` тот же id | отказ | `isError=true` (`UnexpectedToolError`; исходный `Session already exists` FastMCP скрыл) | yes |
| 7 | `stop_session` `clean_data=true` | останов | `stopped=true`; test-client, ibsrv, bridge | yes |

Статический count 122 — профиль `full`, не этот прогон. Живой `full` `tools/list` не снимался. Dual live Test Client NOT_RUN. `click_button` / открытие формы документа не вызывались.

Raw JSON: `r20-mcp-simple.json`, `r20-mcp-initialize-simple.json`,
`r20-mcp-tools-list-simple.json`, `r20-mcp-start-session-simple.json`,
`r20-mcp-active-window-simple.json`, `r20-mcp-screenshot-simple.json`,
`r20-mcp-start-session-duplicate-simple.json`, `r20-mcp-stop-session-simple.json`.
Скрипт: `r20-mcp-smoke.py`.
