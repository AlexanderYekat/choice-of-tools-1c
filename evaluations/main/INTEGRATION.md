# Стыковка выбранных компонентов — результат static S1–S5

Дата: 2026-09-21. Статус: **CONTINUE-AUDIT; deep-static выполнен для
r01 Unica, r15 code-index-mcp, r20 Answer42, r21 Vanessa и r22
v8-runner**. r09 из контура выведен, S1–S5 для него не делаем.

Шкала: [FACADE.md](FACADE.md). План:
[INTEGRATION-PLAN.md](INTEGRATION-PLAN.md).
Все связи — `PROPOSED_INTEGRATION`, execution отсутствует.

## S1–S5

| Кандидат | S1 вызов | S2 source / target | S3 surface | S4 две цели | S5 проект |
|---|---|---|---|---|---|
| **r01 Unica** | **терпимо** — stdio MCP `unica`, не one-shot CLI | **терпимо** — cwd / `v8project.yaml`, аргумента config нет | **удобно** — ровно 11 tools; фасад зовёт subset | **терпимо** — несколько source-set; одна ИБ на yaml; два процесса | **удобно** — автодетект XML/EDT, yaml не обязателен |
| **r15 code-index-mcp** | **терпимо** — CLI ядра + stdio/HTTP MCP `serve`; 1С-tools только MCP+демон | **удобно** — `--path alias=dir` / `[[paths]]` / `repo=`; ИБ нет | **удобно CLI / терпимо MCP** — ~20+13; `[tools].enabled` режет list | **удобно** — несколько alias, отдельный `index.db` | **удобно** на корне выгрузки; `daemon.toml` не обязателен для one-shot |
| r09 mcp-onec-test-runner | OUT OF CONTOUR | — | — | — | — |
| **r22 v8-runner** (конкурент r09) | **удобно** — CLI `v8-runner`; MCP optional stdio/HTTP | **терпимо** — `--config` / один `infobase` на yaml | **удобно** — CLI без tools; MCP ровно 8 | **терпимо** — два yaml / два процесса; dual-IB NOT_RUN | **удобно** — родной `v8project.yaml` |
| **r20 Answer42** | **терпимо** — CLI поднимает stdio/HTTP MCP, не one-shot form CLI | **удобно** — `base_url` + `session_id`; креды из файла | **терпимо** — 122 tools default `full`; есть `--tool-profile` / `--disable-rag` | **удобно по контракту / simultaneous NOT_RUN** | **терпимо** — явный `base_url`; RAG-scan не детектор фасада |
| **r21 Vanessa** | **удобно** — batch CLI через 1С; дополнительно HTTP MCP | **удобно** — один feature, scenario filter, Test Client data/profiles | **удобно CLI / терпимо MCP** — CLI без tools; MCP 37 active static | **терпимо / simultaneous UNKNOWN** | **терпимо** — explicit workspace/projectpath, generic detection facade-side |

Подробности: [reports/r01.md](reports/r01.md), [reports/r15.md](reports/r15.md),
[reports/r20.md](reports/r20.md), [reports/r21.md](reports/r21.md),
[reports/r22.md](reports/r22.md).

## Предпочтительный адаптер r21

Для обычного автономного `verify.scenario` **не обязательно использовать
MCP**. Vanessa уже имеет batch-контур:

```text
verify.scenario(target, feature, scenario?)
  -> temporary VAParams.json
     - КаталогФич = <one .feature>
     - optional СписокСценариевДляВыполнения
     - status file
     - Test Client settings
  -> 1cv8c /TestManager /Execute vanessa-automation.epf
            /C"StartFeaturePlayer;VAParams=..."
  -> wait
  -> read status 0..4
  -> keep detailed logs/reports as artifacts
  -> return compact summary
```

Это лучше всего отвечает C10: coding-agent не видит ни одного Vanessa
MCP tool.

MCP — дополнительный long-lived backend для интерактивной отладки:
`manage_test_client -> run_scenario -> get_test_results`.

## Предпочтительный адаптер r20

Для `verify.form` пакетного CLI нет: `answer42` — это MCP-сервер.
Фасад держит процесс и **не** проксирует сырой `tools/list`:

```text
verify.form(target, steps...)
  -> stdio MCP: answer42 --disable-rag --tool-profile ui
       env ONEC_MCP_CREDENTIALS_FILE=<facade secrets>
  -> start_session(session_id=<target>, base_url=<url or saved title>)
  -> ui_tree / click_button / set_field_value / screenshot
       (каждый вызов с тем же session_id)
  -> PNG/PDF как artifacts (в tool result только path)
  -> compact summary агенту
```

Дефолт `full` (122 tools) агенту не показывать. Продуктовый
`--tool-profile` закрывает C10 без патча Answer42. RAG не использовать
как explore.

## Две ИБ

**Vanessa:** несколько Test Client definitions/profiles; одновременная
работа двух активных целей через один процесс не доказана. Контракт
facade пока `target -> profile/connection`.

**Answer42:** именованные сессии в `_SESSIONS`; UI-tools принимают
`session_id`; повтор того же id отклоняется. Фасад обязан всегда
передавать `session_id` (иначе `default-{pid}` смешает цели).
Одновременность двух живых Test Client на разных `base_url` кодом
допускается, runtime NOT_RUN.

## Предпочтительный адаптер r22 (конкурент r09)

Для `verify.unit` / сборки MCP не обязателен:

```text
verify.unit(target, module?)
  -> v8-runner --json-message --config <target.yaml>
       test [--no-build] yaxunit module <NAME> | yaxunit all
  -> envelope ok / data.report / data.retained_paths
```

`--no-build` есть только в CLI. Две ИБ обмена = два `--config`.
r09 в контур не входит (решение 2026-09-21).

## Предпочтительный адаптер r01

Для `docs` / `edit` / `static.check` пакетного CLI нет: `unica` — stdio MCP.
Фасад держит процесс с `cwd` = корень 1С-проекта и **не** проксирует
сырой `tools/list`:

```text
docs / edit.view / edit.apply / static.check
  -> cwd=<корень с v8project.yaml или выгрузкой>
  -> stdio MCP: unica
  -> subset: unica.docs / unica.view / unica.apply / unica.check
  -> apply: сначала dryRun true, публикация только с ifRev
  -> compact summary агенту; search/run/task.* не светить
```

Официальный хост Codex/Claude не нужен, если есть бинарь. `unica.search`
не explore-слой (это r15). `unica.run` не основной build (это r22).
Патч Unica не нужен.

Две выгрузки в одном корне — два `source-set` и префикс `at`. Две ИБ
обмена — два yaml / два cwd, как у r22.

## Предпочтительный адаптер r15

Для `explore` ядро можно звать one-shot CLI без MCP. Именованные 1С-tools
(структура объекта, handlers формы, подписки, регистраторы) — только MCP
и требуют живой `daemon run`:

```text
explore(source, op, args)
  -> bsl-indexer index --path <source>          # или daemon watch
  -> CODE_INDEX_HOME=<facade>
       daemon.toml [[paths]] + [tools].enabled
  -> stdio MCP: bsl-indexer serve --config <toml>
  -> tools/call repo=<alias> subset explore
  -> compact summary; raw tools/list не показывать
```

Без демона: `bsl-indexer search_function|get_function|get_callers --path`.
Патч r15 не нужен.

## Что остаётся

Static S1–S5 пяти закрыты. **r15 CLI ядра PASS** на выгрузке
`simple1CAiConf` (без ИБ). Daemon/MCP r15 и runtime остальных NOT_RUN.
Внедрение и код фасада не начинались.
