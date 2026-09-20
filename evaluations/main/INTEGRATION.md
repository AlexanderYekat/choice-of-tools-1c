# Стыковка выбранных компонентов — частичный результат

Дата: 2026-09-20. Статус: **CONTINUE-AUDIT начат; deep-static выполнен
только для r21 Vanessa Automation**. Остальные четыре кандидата этим
изменением не углублялись.

Шкала: [FACADE.md](FACADE.md). План:
[INTEGRATION-PLAN.md](INTEGRATION-PLAN.md).
Все связи — `PROPOSED_INTEGRATION`, execution отсутствует.

## S1–S5

| Кандидат | S1 вызов | S2 source / target | S3 surface | S4 две цели | S5 проект |
|---|---|---|---|---|---|
| r01 Unica | PENDING | PENDING | PENDING | PENDING | PENDING |
| r15 code-index-mcp | PENDING | PENDING | PENDING | PENDING | PENDING |
| r09 mcp-onec-test-runner | PENDING | PENDING | PENDING | PENDING | PENDING |
| r20 Answer42 | PENDING | PENDING | PENDING | PENDING | PENDING |
| **r21 Vanessa** | **удобно** — batch CLI через 1С; дополнительно HTTP MCP | **удобно** — один feature, scenario filter, Test Client data/profiles | **удобно CLI / терпимо MCP** — CLI без tools; MCP 37 active static | **терпимо / simultaneous UNKNOWN** | **терпимо** — explicit workspace/projectpath, generic detection facade-side |

Подробности: [reports/r21.md](reports/r21.md).

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

## Две ИБ

Vanessa принимает несколько Test Client definitions/profiles, но
одновременная работа двух активных целей через один процесс не доказана.
Контракт facade пока только `target -> profile/connection`.

## Что остаётся

r01/r15/r09/r20 требуют S1–S5. По r21 execution NOT_RUN.
DECISION/FACADE не менялись.
