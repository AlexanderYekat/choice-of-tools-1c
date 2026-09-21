# Проверки и следующий эксперимент

Ограниченные dump-only прогоны r15 (CLI + daemon/MCP) и r22
(init/build/syntax) выполнены. Остальные продукты не запускались.
Основания: [EVIDENCE.json](EVIDENCE.json).
Версия цели: 2.

## Стыковка (цель v2)

План — [INTEGRATION-PLAN.md](INTEGRATION-PLAN.md), результат —
[INTEGRATION.md](INTEGRATION.md).

Сейчас **r01 Unica, r15 code-index-mcp, r20 Answer42, r21 Vanessa и
r22 v8-runner-rust достигли DEEP_STATIC**. r09 OUT OF CONTOUR,
static стыковка для него не требуется.

| ID | Вопрос | r01 Unica | r15 code-index-mcp | r20 Answer42 | r21 Vanessa | r22 v8-runner |
|---|---|---|---|---|---|---|
| S1 | Чем звать | SOURCE: бинарь `unica` = stdio MCP; one-shot CLI предметных операций нет | SOURCE+RUN: CLI ядра + HTTP `serve`; 1С-tools только MCP; живой демон нужен | SOURCE: CLI `answer42` = stdio MCP (опционально `--http`); one-shot form CLI нет | DOCUMENTATION+SOURCE: batch CLI через 1С; дополнительно Streamable HTTP MCP | SOURCE: CLI `v8-runner` first-class; MCP `mcp serve stdio\|http` optional |
| S2 | Как передать feature/ИБ | SOURCE+DOCUMENTATION: cwd / предок `v8project.yaml`; ИБ в yaml; `at`/`sourceSet`; аргумента config нет | SOURCE: `--path alias=dir` / `--config` `[[paths]]` / `repo=`; ИБ не участвует | SOURCE: `start_session(base_url, session_id)`; креды из файла/title | DOCUMENTATION+SOURCE: один feature через featurepath, scenariofilter, Test Client definitions/profiles | DOCUMENTATION+SOURCE: `--config` / `V8TR_CONFIG` / cwd → один `infobase` в yaml |
| S3 | Узкая surface | SOURCE: ровно 11 tools; фасад зовёт subset docs/view/apply/check | SOURCE+RUN: живой `tools/list` = 33 (20+13); CLI без tools/list; `[tools].enabled` режет MCP (whitelist NOT_RUN) | SOURCE: 122 `@mcp.tool()` при `full`; `--tool-profile` / `--disable-rag` режут список | SOURCE+INFERENCE: CLI без MCP tools; MCP 37 statically active, скрывать фасадом | SOURCE: CLI без tools/list; MCP ровно 8 `#[tool]` |
| S4 | Две цели | SOURCE+INFERENCE: несколько source-set; одна ИБ на yaml; демон общий, scope по cwd; dual-IB NOT_RUN | SOURCE: несколько alias, отдельный `.code-index/index.db`; dual live serve NOT_RUN | SOURCE+INFERENCE: `_SESSIONS` + `session_id`; dual live Test Client NOT_RUN | SOURCE+INFERENCE: несколько definitions/profiles; simultaneous two-target UNKNOWN | INFERENCE: два yaml / два процесса; dual-IB NOT_RUN |
| S5 | Project detection | SOURCE: автодетект XML/EDT без yaml; yaml не обязателен | SOURCE: processor — `Configuration.xml` (≤2) и EDT `Configuration.mdo`; `daemon.toml` не обязателен для one-shot; детектор демона слабее | INFERENCE: явный `base_url`; RAG-scan EDT/XML не детектор фасада | INFERENCE: explicit WorkspaceRoot/projectpath; generic 1C detection facade-side | DOCUMENTATION: родной `v8project.yaml` + `config init` |

Шкала r01: S1 терпимо; S2 терпимо; S3 удобно; S4 терпимо; S5 удобно.

Шкала r15: S1 терпимо; S2 удобно; S3 удобно через CLI / терпимо через MCP;
S4 удобно; S5 удобно на корне выгрузки.

Шкала r20: S1 терпимо; S2 удобно; S3 терпимо (с `--tool-profile ui`);
S4 удобно по контракту, simultaneous NOT_RUN; S5 терпимо.

Шкала r21: S1 удобно; S2 удобно; S3 удобно через CLI / терпимо через MCP;
S4 терпимо с неизвестной одновременностью; S5 терпимо.

Шкала r22: S1 удобно; S2 терпимо; S3 удобно; S4 терпимо; S5 удобно.

Execution: **r15 CLI ядра PASS**; **r15 daemon+MCP PASS**
([logs/r15-mcp-simple.md](logs/r15-mcp-simple.md)); **r22
init/build/syntax PASS** на ИБ стенда `simple`
([logs/r22-ib-simple.md](logs/r22-ib-simple.md)). r01, r20, r21
остаются NOT_RUN. YaXUnit/Vanessa не запускались (в выгрузке нет тестов).

Следующее — Unica `view`/`check`, не код фасада.
