# Проверки и следующий эксперимент

Ограниченные dump-only прогоны r15 (CLI + daemon/MCP), r22
(init/build/syntax) и r01 Unica (`view`/`check`, `apply` dryRun,
`docs`, **публикация `ifRev`**) выполнены. **Answer42 smoke PASS**.
Vanessa engine smoke PASS. Основания: [EVIDENCE.json](EVIDENCE.json).
Версия цели: 2.

## Стыковка (цель v2)

План — [INTEGRATION-PLAN.md](INTEGRATION-PLAN.md), результат —
[INTEGRATION.md](INTEGRATION.md).

Сейчас **r01 Unica, r15 code-index-mcp, r20 Answer42, r21 Vanessa и
r22 v8-runner-rust достигли DEEP_STATIC**. r09 OUT OF CONTOUR,
static стыковка для него не требуется.

| ID | Вопрос | r01 Unica | r15 code-index-mcp | r20 Answer42 | r21 Vanessa | r22 v8-runner |
|---|---|---|---|---|---|---|
| S1 | Чем звать | SOURCE+RUN: бинарь `unica` = stdio MCP; one-shot CLI предметных операций нет; живой initialize 0.12.0 | SOURCE+RUN: CLI ядра + HTTP `serve`; 1С-tools только MCP; живой демон нужен | SOURCE+RUN: CLI `answer42` = stdio MCP; initialize name=Answer42; one-shot form CLI нет | DOCUMENTATION+SOURCE: batch CLI через 1С; дополнительно Streamable HTTP MCP | SOURCE: CLI `v8-runner` first-class; MCP `mcp serve stdio\|http` optional |
| S2 | Как передать feature/ИБ | SOURCE+RUN: cwd выгрузки; `view {}` autodetected `main`; yaml не обязателен; ИБ в yaml (здесь `infobase.configured=false`) | SOURCE: `--path alias=dir` / `--config` `[[paths]]` / `repo=`; ИБ не участвует | SOURCE+RUN: `start_session(base_url=путь файловой ИБ, session_id)`; креды не нужны на simple | DOCUMENTATION+SOURCE: один feature через featurepath, scenariofilter, Test Client definitions/profiles | DOCUMENTATION+SOURCE: `--config` / `V8TR_CONFIG` / cwd → один `infobase` в yaml |
| S3 | Узкая surface | SOURCE+RUN: живой `tools/list` = 11; фасад зовёт subset docs/view/apply/check | SOURCE+RUN: живой `tools/list` = 33 (20+13); CLI без tools/list; `[tools].enabled` режет MCP (whitelist NOT_RUN) | SOURCE+RUN: статический `full` 122; живой `ui`+`--disable-rag` = 103 | SOURCE+INFERENCE: CLI без MCP tools; MCP 37 statically active, скрывать фасадом | SOURCE: CLI без tools/list; MCP ровно 8 `#[tool]` |
| S4 | Две цели | SOURCE+INFERENCE: несколько source-set; одна ИБ на yaml; демон общий, scope по cwd; dual-IB NOT_RUN | SOURCE: несколько alias, отдельный `.code-index/index.db`; dual live serve NOT_RUN | SOURCE+RUN: повтор того же `session_id` отказал; dual live Test Client NOT_RUN | SOURCE+INFERENCE: несколько definitions/profiles; simultaneous two-target UNKNOWN | INFERENCE: два yaml / два процесса; dual-IB NOT_RUN |
| S5 | Project detection | SOURCE+RUN: `view {}` без yaml, source-set `main` из `Configuration.xml` на `.` | SOURCE: processor — `Configuration.xml` (≤2) и EDT `Configuration.mdo`; `daemon.toml` не обязателен для one-shot; детектор демона слабее | INFERENCE: явный `base_url`; RAG-scan EDT/XML не детектор фасада | INFERENCE: explicit WorkspaceRoot/projectpath; generic 1C detection facade-side | DOCUMENTATION: родной `v8project.yaml` + `config init` |

Шкала r01: S1 терпимо; S2 терпимо; S3 удобно; S4 терпимо; S5 удобно.

Шкала r15: S1 терпимо; S2 удобно; S3 удобно через CLI / терпимо через MCP;
S4 удобно; S5 удобно на корне выгрузки.

Шкала r20: S1 терпимо; S2 удобно; S3 терпимо (живой `ui` = 103, фасад всё равно нужен);
S4 удобно по контракту (дубль id RUN), simultaneous NOT_RUN; S5 терпимо.

Шкала r21: S1 удобно; S2 удобно; S3 удобно через CLI / терпимо через MCP;
S4 терпимо с неизвестной одновременностью; S5 терпимо.

Шкала r22: S1 удобно; S2 терпимо; S3 удобно; S4 терпимо; S5 удобно.

Execution: **r15 CLI ядра PASS**; **r15 daemon+MCP PASS**
([logs/r15-mcp-simple.md](logs/r15-mcp-simple.md)); **r22
init/build/syntax PASS** на ИБ стенда `simple`
([logs/r22-ib-simple.md](logs/r22-ib-simple.md)); **r01
`view`/`check` PASS** ([logs/r01-mcp-simple.md](logs/r01-mcp-simple.md));
**r01 `apply` dryRun + `docs` PASS**
([logs/r01-mcp-apply-simple.md](logs/r01-mcp-apply-simple.md));
**r22 dump 2.20 PASS**; **r01 apply dryRun на 2.20 PASS** (preview).
YaXUnit/Vanessa на simple **сначала отказали** без сценария; после
написанного `smoke-engine.feature` Vanessa **1/1 PASS**. `unica.check` на рукописном дампе — `source_unreadable`.
`unica.apply` dryRun там же — `invalid_source`; на cf220 — план, затем
публикация `dryRun:false` + `ifRev` — `mode=published`.
**r20 Answer42 smoke PASS** ([logs/r20-mcp-simple.md](logs/r20-mcp-simple.md)).
**r01 apply publish PASS** ([logs/r01-mcp-apply-publish-simple.md](logs/r01-mcp-apply-publish-simple.md)):
`mode=published`; XML Comment записан; stale `ifRev` — `stale_revision`.

Следующее — dump-only `[tools].enabled` r15, не код фасада.
