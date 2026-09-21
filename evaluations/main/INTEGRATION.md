# Стыковка выбранных компонентов — частичный результат

Дата: 2026-09-21. Статус: **CONTINUE-AUDIT; deep-static выполнен для
r21 Vanessa, r20 Answer42 и r22 v8-runner**. Остальные три кандидата
плана (r01/r15/r09) этим изменением не углублялись. r22 — вне исходной
пятёрки, конкурент слота r09.

Шкала: [FACADE.md](FACADE.md). План:
[INTEGRATION-PLAN.md](INTEGRATION-PLAN.md).
Все связи — `PROPOSED_INTEGRATION`, execution отсутствует.

## S1–S5

| Кандидат | S1 вызов | S2 source / target | S3 surface | S4 две цели | S5 проект |
|---|---|---|---|---|---|
| r01 Unica | PENDING | PENDING | PENDING | PENDING | PENDING |
| r15 code-index-mcp | PENDING | PENDING | PENDING | PENDING | PENDING |
| r09 mcp-onec-test-runner | PENDING | PENDING | PENDING | PENDING | PENDING |
| **r22 v8-runner** (конкурент r09) | **удобно** — CLI `v8-runner`; MCP optional stdio/HTTP | **терпимо** — `--config` / один `infobase` на yaml | **удобно** — CLI без tools; MCP ровно 8 | **терпимо** — два yaml / два процесса; dual-IB NOT_RUN | **удобно** — родной `v8project.yaml` |
| **r20 Answer42** | **терпимо** — CLI поднимает stdio/HTTP MCP, не one-shot form CLI | **удобно** — `base_url` + `session_id`; креды из файла | **терпимо** — 122 tools default `full`; есть `--tool-profile` / `--disable-rag` | **удобно по контракту / simultaneous NOT_RUN** | **терпимо** — явный `base_url`; RAG-scan не детектор фасада |
| **r21 Vanessa** | **удобно** — batch CLI через 1С; дополнительно HTTP MCP | **удобно** — один feature, scenario filter, Test Client data/profiles | **удобно CLI / терпимо MCP** — CLI без tools; MCP 37 active static | **терпимо / simultaneous UNKNOWN** | **терпимо** — explicit workspace/projectpath, generic detection facade-side |

Подробности: [reports/r20.md](reports/r20.md), [reports/r21.md](reports/r21.md),
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

## Что остаётся

r01/r15 требуют S1–S5. По r20, r21 и r22 execution NOT_RUN.
