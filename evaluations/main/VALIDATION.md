# Проверки и следующий эксперимент

Ограниченные dump-only прогоны r15 (CLI + daemon/MCP + `[tools].enabled`), r22
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
| S3 | Узкая surface | SOURCE+RUN: живой `tools/list` = 11; фасад зовёт subset docs/view/apply/check | SOURCE+RUN: без секции list = 33; с `[tools].enabled` list = 9 и `tools/call` вне списка = `-32602`; CLI без tools/list | SOURCE+RUN: статический `full` 122; живой `ui`+`--disable-rag` = 103 | SOURCE+INFERENCE: CLI без MCP tools; MCP 37 statically active, скрывать фасадом | SOURCE: CLI без tools/list; MCP ровно 8 `#[tool]` |
| S4 | Две цели | SOURCE+RUN: два cwd, один демон, два requestScopeHash; несколько source-set в одном yaml NOT_RUN; одна ИБ на yaml; dual-IB NOT_RUN | SOURCE: несколько alias, отдельный `.code-index/index.db`; dual live serve NOT_RUN | SOURCE+RUN: повтор того же `session_id` отказал; dual live Test Client на двух файловых ИБ PASS (заголовки окон совпали) | SOURCE+INFERENCE: несколько definitions/profiles; simultaneous two-target UNKNOWN | INFERENCE: два yaml / два процесса; dual-IB NOT_RUN |
| S5 | Project detection | SOURCE+RUN: `view {}` без yaml, source-set `main` из `Configuration.xml` на `.` | SOURCE: processor — `Configuration.xml` (≤2) и EDT `Configuration.mdo`; `daemon.toml` не обязателен для one-shot; детектор демона слабее | INFERENCE: явный `base_url`; RAG-scan EDT/XML не детектор фасада | INFERENCE: explicit WorkspaceRoot/projectpath; generic 1C detection facade-side | DOCUMENTATION: родной `v8project.yaml` + `config init` |

Шкала r01: S1 терпимо; S2 терпимо; S3 удобно; S4 терпимо; S5 удобно.

Шкала r15: S1 терпимо; S2 удобно; S3 удобно (CLI или MCP с
`[tools].enabled`); S4 удобно; S5 удобно на корне выгрузки.

Шкала r20: S1 терпимо; S2 удобно; S3 терпимо (живой `ui` = 103, фасад всё равно нужен);
S4 удобно (дубль id RUN; два живых Test Client RUN); S5 терпимо.

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
**r15 `[tools].enabled` PASS** ([logs/r15-mcp-whitelist-simple.md](logs/r15-mcp-whitelist-simple.md)):
`tools/list` = 9; опечатка в логе; `grep_code` и `get_object_structure` — `-32602`.
**r01 dual-workspace PASS** ([logs/r01-mcp-dual-simple.md](logs/r01-mcp-dual-simple.md)):
два stdio, один `--daemon`; `view` не смешал корни и Comment.
**r20 dual live Test Client PASS** ([logs/r20-mcp-dual-simple.md](logs/r20-mcp-dual-simple.md)):
один stdio, две файловые ИБ, file-ibsrv 8424 и 10104; останов A оставил B.
Скрипт exit 1 на сравнении слэшей; критерий подтверждён сохранённым JSON.

Следующее — по переписанному 2026-09-22
[INTEGRATION-PLAN.md](INTEGRATION-PLAN.md): **E1** YaXUnit на simple
(расширение с проходящим и падающим тестом) — закрывает единственный
FAIL; **E2** две цели для r01 (два source-set в одном yaml) и r22
(два yaml, вторая ИБ — копия `ib-b` от r20), r21 simultaneous остаётся
UNKNOWN осознанно; **E3** сквозной прогон цепочки с замером объёма
выдач по каждой операции поверхности (`success_criteria[0]`);
**E4** stdio-whitelist r15 и `--path` + `--config` — догоняющее.
Код фасада не писать.

**E1 статус на 2026-09-22: FAIL, не закрыт.** Движок YaXUnit 25.12 и
рукописное тестовое расширение `e1tests` установлены и активны в
`.v8/ib/simple` (build/load/merge/SafeMode — все шаги PASS), но
`test yaxunit` находит 0 сценариев. Инструментированная локальная копия
YaXUnit (диагностика, не upstream-патч) доказала: платформа не резолвит
модуль `ТестыE1` по имени из динамического `Выполнить()`, вызванного из
кода соседнего расширения YAXUNIT — воспроизведено и для настоящего
`ИсполняемыеСценарии`, и для отдельного тривиального пробного метода
того же модуля. Не изолировано: специфично ли это рукописному (без
EDT/Designer) scaffold'у расширения, или общее ограничение платформы для
независимых соседних расширений. Следующий эксперимент: проверить
load-order/priority/dependency между расширениями, и/или получить
тестовое расширение, собранное настоящим Дизайнером/EDT, для сравнения.
Подробности: [logs/r22-yaxunit-e1tests-simple.md](logs/r22-yaxunit-e1tests-simple.md).
До изоляции причины `verify.unit` через YaXUnit не считать готовым
к фасаду.

**E2 статус на 2026-09-22: PASS (оба подшага).** E2a (Unica, два
`source-set` в одном yaml, один процесс) — 8/8 PASS: `at="main:…"` и
`at="cf220:…"` резолвятся раздельно и различимо, `at="bogus:…"` даёт
именованный отказ (`provider_unavailable`), оба дампа не изменились;
Unica требует workspace-relative пути `source-set` без выхода за корень
workspace (абсолютные пути — невалидный yaml). E2b (r22, два `--config`/
два процесса на `.v8/ib/simple` и готовой копии `.v8/work/r20-dual/ib-b`)
— PASS: `syntax designer-modules` чисто на обеих целях, sha256 каждой ИБ
меняется только от своей операции, несуществующий `--config` — явный
отказ `invalid_argument`. Новых ИБ не создавалось. r21 simultaneous
остаётся UNKNOWN осознанно. Подробности:
[logs/r01-r22-e2-two-targets.md](logs/r01-r22-e2-two-targets.md).

**E3 статус на 2026-09-22: PASS.** Реальный проход по всем 8 операциям
внешней поверхности с замером байт/строк. Обязательная выгрузка в файл
только у `docs` (77 205 Б/800 строк, асинхронная задача) и у скриншота
Answer42 (180 КБ PNG, путь, не base64). Сумма цикла ≈290 КБ «как есть»,
≈30 КБ при выгрузке этих двух в файл — бюджет контекста не блокер при
условии, что фасад делает это с самого начала. Список из 7 стыков между
продуктами (формат 2.20/1.0, владелец ИБ, владелец рабочего дампа,
разрешение имени расширения у v8-runner, несовместимость EDT-исходников
YaXUnit с DESIGNER-проектом, асинхронность `docs`, ненадёжный
incremental build) записан. `verify.unit` в этом проходе — честный
`ok=false`, не PASS (см. открытый риск E1 выше). Подробности:
[logs/e3-chain-simple.md](logs/e3-chain-simple.md).
