# Общая картина: main

Версия цели: 2. r02–r14, r16–r19 остаются overview; **r01 Unica,
r15 code-index-mcp, r20 Answer42, r21 Vanessa и r22 v8-runner-rust
углублены до DEEP_STATIC по S1–S5**.
**r15 CLI ядра PASS**; **r15 daemon+MCP PASS**; **r22 init/build/syntax PASS**;
**r01 `view`/`check` PASS** на стенде `simple`.
Static стыковка пяти закрыта. Состав:
**r22 вместо r09** (решение пользователя 2026-09-21).

Самопроверка координатора, не независимый аудит.

## Ответ для пользователя

Готового монолита среди обзора 19 нет. Состав контура **выбран**
(цель v2): Unica, code-index-mcp, v8-runner, Answer42, Vanessa
и тонкий фасад. Подробности — [DECISION.md](DECISION.md).

r09 METR выведен: тот же слой, что r22. Vanessa остаётся движком
сценариев; запускает r22.

Обычные формы и хост Cursor **не обязательны**. rlm и skills Cursor/Claude
в контур не входят.

Это не разрешение внедрять. Static S1–S5 пяти закрыт
([FACADE.md](FACADE.md), [VALIDATION.md](VALIDATION.md)).
r15 CLI, r15 daemon+MCP, r22 init/build/syntax и r01 `view`/`check`
прогнаны на стенде `simple`. Следующий этап — `unica.apply` dryRun /
`unica.docs` / Answer42 по отдельной просьбе.

Вывод обзора при цели v1 сохранён в снимке `history/goal-v1/REPORT.md`.
Его не читать при обычном CONTINUE; как рекомендация v2 он не действует.

## Цель и охват

Критерии C1–C14 — [BRIEF.md](BRIEF.md), версия 2. Входов 22: r01–r22
AVAILABLE. Недоступных среди обзора 19: 0. r12 и r13 — содержательно
один toolkit в двух упаковках. Карточки обзора r01–r19: [reports/](reports/)
— не переписывались; меняется оценка роли, не SHA. r01/r20/r21/r22 —
DEEP_STATIC по S1–S5. **r15 — DEEP_STATIC по S1–S5** на том же pinned SHA
обзора. Реестр: [INVENTORY.json](INVENTORY.json).

Обзор, не deep-static: списки tools r09 (8 `@Tool`) и 1С-надстройка r15
(13 tools) закреплены по исходникам; r10 и универсальные 20 tools r15
остаются DOCUMENTATION. r17 явно отказывает ordinary forms (для v2 не блокер).

## Решения и архитектурные варианты

| Решение v2 | Кандидаты | Условие |
|---|---|---|
| Explore-ядро за фасадом | r15 | не сырой tools/list |
| Edit/docs/static/run | r01 | хост любой, где зовётся бинарь |
| Verify unit/build | **r22 выбран**; r09 не в контуре | AGPL-3.0; CLI `--json-message` |
| UI form / scenario | r20 Answer42, r21 Vanessa (запуск через r22) | r20: MCP stdio, `session_id`, `--tool-profile`; r21: движок `.feature` |
| Не в контуре | r09, r02, r12, r13, r10, r18 и прочие из DECISION | дубль или не та роль |
| Спецслучай | r04, r06, r07, r17 | по пробелу, не по умолчанию |

Варианты A/B/C обзора v1 (rlm+Unica; без Unica+r12; EDT-only) — исторические
и не нужны для S1–S5; полный текст в снимке `history/goal-v1/REPORT.md`.
Вариант C отклонён и в v2 (не основа контура).

Гипотеза explore/docs/edit/static/verify — внутренняя нарезка фасада.

## Риски и ревью

Наиболее существенные неизвестные цели v2:

1. Execution (индекс r15, smoke остальных). Static S1–S5 пяти есть.
2. Для Unica r01 остаются execution `view`/`apply`; для Answer42 r20 — dual live Test Client; для Vanessa r21 — execution; для r22 — smoke `test yaxunit` / `test va`.
3. Точность индекса r15 и компактность JSON-отчёта r22.
4. Лицензии Unica (LGPL) и r22 (AGPL-3.0) — не юридическое заключение.
5. Сборка r04, если `unica.docs` не хватит.

Контрпример «обычные формы доминируют» в v2 не опрокидывает контур.
Контрпример «пять MCP торчат агенту» опрокидывает внедрение без фасада
(у r20 дефолт 122 tools — самый сильный пример). Контрпример
«singleton затирает обмен» для r20 слабее: есть именованный `session_id`,
но фасад обязан его всегда передавать. Для r01 слабее тем же смыслом:
одна yaml = одна ИБ, две цели = два корня/cwd; общий user-daemon скоупится
по `workspace_hint`.
Контрпример «вернуть r09 рядом с r22» опрокидывается C14.
Вывод «не подключать все 19» контрпримером не опрокинут.

Механический `kit.py check-run` проверяет структуру, не истинность.

## Следующий эксперимент и состояние

Не V1 (Unica в Cursor) и не внедрение. Static S1–S5 пяти закрыт —
[INTEGRATION.md](INTEGRATION.md); статусы — [VALIDATION.md](VALIDATION.md).
Этот отчёт не запускает остальные продукты. **r15 CLI** и **r22
init/build/syntax** PASS на стенде `simple` (ИБ создана). Точка
продолжения — [STATE.md](STATE.md).


## Частичный CONTINUE-AUDIT r20

[Answer42](reports/r20.md) — MCP-драйвер Test Client, не пакетный CLI
формы. CLI `answer42` поднимает stdio (или HTTP) MCP. Цель задаётся
`start_session(base_url, session_id)`; screenshot пишет путь, не base64.
На SHA 122 `@mcp.tool()` при профиле `full`, но продукт уже режет
поверхность через `--tool-profile ui|core` и `--disable-rag`. RAG не
брать как explore. Состав не менялся. Execution NOT_RUN.

## Частичный CONTINUE-AUDIT r21

[Vanessa Automation](reports/r21.md) оказалась лучше приспособлена к
узкому фасаду, чем предполагалось по одному MCP: у проекта давно есть
пакетный command-line режим через платформу 1С. Он позволяет запускать
один feature-файл, фильтровать сценарий и получать машинный status 0–4.
Поэтому для обычного `verify.scenario` предпочтителен batch CLI adapter;
MCP разумно оставить для интерактивной отладки. Это не меняет выбранный
состав, а уменьшает постоянную tool surface.

## Частичный CONTINUE-AUDIT r01

[Unica](reports/r01.md) — stdio MCP, не one-shot CLI правок. Бинарь
`unica` поднимает MCP и пользовательский демон; корень задаётся cwd /
`v8project.yaml`, аргумента `config` нет. Поверхность ровно 11 tools;
фасад зовёт subset `docs`/`view`/`apply`/`check`. `apply` без `ifRev`
на публикацию отвергается. Автодетект выгрузки без yaml есть
(`Configuration.xml` / EDT `.mdo`) и **подтверждён** `unica.view {}` на
simple1CAiConf (`config.state=autodetected`, source-set `main`). Живой
`tools/list` = 11. `unica.check` на этом дампе ответил
`source_unreadable` (формат 2.20). Две ИБ обмена — два корня, как у
r22. Патч не нужен. Состав не менялся. `apply` NOT_RUN.

## Частичный CONTINUE-AUDIT r15

[code-index-mcp](reports/r15.md) — explore-ядро. Бинарь `bsl-indexer`:
one-shot CLI ядра (`index`, `search_function`, `get_callers`) и stdio/HTTP
MCP `serve` (только чтение). Именованные 1С-tools (13) только в MCP и
требуют `daemon run` (`daemon_offline` без него). Выгрузка задаётся
`--path alias=dir` или `[[paths]]`; две выгрузки — два alias и два
`index.db`. Автодетект: `Configuration.xml` и EDT `Configuration.mdo`.
Широкий `tools/list` режется `[tools].enabled`. Патч не нужен. HEAD
`309cddb…` не подменял pinned `4bde72b…`. Состав не менялся.
Dump-only MCP на simple1CAiConf: живой `tools/list` = 33; handlers,
structure и register writers PASS.

