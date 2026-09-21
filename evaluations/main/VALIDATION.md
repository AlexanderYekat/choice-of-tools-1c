# Проверки и следующий эксперимент

Запуски продуктов не выполнялись. Основания: [EVIDENCE.json](EVIDENCE.json).
Версия цели: 2.

## Стыковка (цель v2)

План — [INTEGRATION-PLAN.md](INTEGRATION-PLAN.md), частичный результат —
[INTEGRATION.md](INTEGRATION.md).

Сейчас **r01 Unica, r20 Answer42, r21 Vanessa и r22 v8-runner-rust
достигли DEEP_STATIC**; r15 остаётся OVERVIEW. r09 OUT OF CONTOUR,
static стыковка для него не требуется.

| ID | Вопрос | r01 Unica | r20 Answer42 | r21 Vanessa | r22 v8-runner |
|---|---|---|---|---|---|
| S1 | Чем звать | SOURCE: бинарь `unica` = stdio MCP; one-shot CLI предметных операций нет | SOURCE: CLI `answer42` = stdio MCP (опционально `--http`); one-shot form CLI нет | DOCUMENTATION+SOURCE: batch CLI через 1С; дополнительно Streamable HTTP MCP | SOURCE: CLI `v8-runner` first-class; MCP `mcp serve stdio\|http` optional |
| S2 | Как передать feature/ИБ | SOURCE+DOCUMENTATION: cwd / предок `v8project.yaml`; ИБ в yaml; `at`/`sourceSet`; аргумента config нет | SOURCE: `start_session(base_url, session_id)`; креды из файла/title | DOCUMENTATION+SOURCE: один feature через featurepath, scenariofilter, Test Client definitions/profiles | DOCUMENTATION+SOURCE: `--config` / `V8TR_CONFIG` / cwd → один `infobase` в yaml |
| S3 | Узкая surface | SOURCE: ровно 11 tools; фасад зовёт subset docs/view/apply/check | SOURCE: 122 `@mcp.tool()` при `full`; `--tool-profile` / `--disable-rag` режут список | SOURCE+INFERENCE: CLI без MCP tools; MCP 37 statically active, скрывать фасадом | SOURCE: CLI без tools/list; MCP ровно 8 `#[tool]` |
| S4 | Две цели | SOURCE+INFERENCE: несколько source-set; одна ИБ на yaml; демон общий, scope по cwd; dual-IB NOT_RUN | SOURCE+INFERENCE: `_SESSIONS` + `session_id`; dual live Test Client NOT_RUN | SOURCE+INFERENCE: несколько definitions/profiles; simultaneous two-target UNKNOWN | INFERENCE: два yaml / два процесса; dual-IB NOT_RUN |
| S5 | Project detection | SOURCE: автодетект XML/EDT без yaml; yaml не обязателен | INFERENCE: явный `base_url`; RAG-scan EDT/XML не детектор фасада | INFERENCE: explicit WorkspaceRoot/projectpath; generic 1C detection facade-side | DOCUMENTATION: родной `v8project.yaml` + `config init` |

Шкала r01: S1 терпимо; S2 терпимо; S3 удобно; S4 терпимо; S5 удобно.

Шкала r20: S1 терпимо; S2 удобно; S3 терпимо (с `--tool-profile ui`);
S4 удобно по контракту, simultaneous NOT_RUN; S5 терпимо.

Шкала r21: S1 удобно; S2 удобно; S3 удобно через CLI / терпимо через MCP;
S4 терпимо с неизвестной одновременностью; S5 терпимо.

Шкала r22: S1 удобно; S2 терпимо; S3 удобно; S4 терпимо; S5 удобно.

Execution запрещён текущими permissions и остаётся NOT_RUN.
Следующий static CONTINUE-AUDIT — r15.
