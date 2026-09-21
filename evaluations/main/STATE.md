# Состояние main / 20260920T044856175227Z

Версия цели: **2**. Статус: COMPOSITION_R22_CHOSEN; STATIC_S1S5_FIVE_DONE;
FIXTURE_HARNESS_ATTACHED; R15_CLI_SMOKE_PASS; R15_MCP_SMOKE_PASS;
R22_IB_SMOKE_PASS; R01_MCP_SMOKE_PASS; R01_APPLY_DOCS_SMOKE_PASS.
Последнее обновление: 2026-09-21.

Состав контура выбран ([DECISION.md](DECISION.md)): Unica, code-index-mcp,
**v8-runner (r22 вместо r09)**, Answer42, Vanessa, тонкий фасад.
План: [INTEGRATION-PLAN.md](INTEGRATION-PLAN.md).
Стыковка: **r01 Unica, r15 code-index-mcp, r20 Answer42, r21 Vanessa
и r22 v8-runner достигли DEEP_STATIC по S1–S5**. r15 CLI, r15 daemon+MCP,
r22 init/build/syntax, r01 `view`/`check` и r01 `apply` dryRun + `docs`
на стенде `simple` — PASS. Фасад не писался.

## Восстановление без чата

1. Этот файл.
2. [request.json](request.json), [BRIEF.md](BRIEF.md).
3. [DECISION.md](DECISION.md), [FACADE.md](FACADE.md).
4. [INTEGRATION-PLAN.md](INTEGRATION-PLAN.md).
5. [INTEGRATION.md](INTEGRATION.md) — фактический static-результат.
6. [VALIDATION.md](VALIDATION.md).
7. Для r01 — [reports/r01.md](reports/r01.md); для r15 —
   [reports/r15.md](reports/r15.md); для r22 —
   [reports/r22.md](reports/r22.md); для r20 —
   [reports/r20.md](reports/r20.md); для r21 —
   [reports/r21.md](reports/r21.md); остальные карточки читать по необходимости.

## Прогресс

- **r01 Unica: AVAILABLE / DEEP_STATIC**, commit
  `56a67d4a460c97101b6b542b4fe940298ab0edd8` (ветка `main`, HEAD совпал).
  stdio MCP dump-only PASS; живой `tools/list` = 11; `view {}`
  autodetected `main`; `check` отказал фикстуре по формату 2.20;
  `apply` dryRun — `invalid_source` (format 1.0 vs writable 2.20);
  забор `ifRev` живой; `docs` НаборЗаписей — 5 секций / 80 hits.
- **r15 code-index-mcp: AVAILABLE / DEEP_STATIC**, commit
  `4bde72b60a09187c0667d451a02c7be5e0169835` (ветка `main`, v1.4.0).
  HEAD 2026-09-21 = `309cddb…` (v1.4.2); SHA не подменялся.
  CLI ядра + HTTP MCP dump-only PASS; живой `tools/list` = 33
  (13 1С-tools); alias `simple`.
- r09: OVERVIEW, **не в контуре** (C14, решение 2026-09-21).
- **r20 Answer42: AVAILABLE / DEEP_STATIC**, commit
  `0406669a88144834bfdf6086c7040a25cb76d24c` (ветка `beta`, v0.5.3).
- **r21 Vanessa: AVAILABLE / DEEP_STATIC**, commit
  `7db5c2bbbf91fd965613a6119121a098bf64cd9e`. Движок `.feature`; запуск
  через r22.
- **r22 v8-runner-rust: AVAILABLE / DEEP_STATIC**, commit
  `7ce1b062843d86644fe55741dbe0ee79f7ca767d` (ветка `master`, v0.5.1).
  **Выбран** как сборка / YaXUnit / синтаксис / запуск Vanessa.

Разрешения: `permissions.*` в request.json по-прежнему false. Пользователь
«хорошо, тогда вперёд» (2026-09-21) принят как разрешение создать
тестовую ИБ `.v8/ib/simple` из выгрузки и прогнать smoke r22.
«что там дальше по плану — выполняй» (2026-09-21) — dump-only MCP r15.
ИБ создана. Vanessa/YaXUnit (`tools.* = false`) не запускались.
Runtime r20/r21 остаются NOT_RUN. Публикация `apply` (`dryRun:false`
+ живой `ifRev`) NOT_RUN.

Фикстура: opt-in v8-harness @ `322398ae…`, стенд `simple`, `from: file`.
Выгрузка `source-checkouts/simple1CAiConf` @ `1dbc395d…`.
Платформа `8.3.27.1936` strict. В выгрузке нет пользователей ИБ —
поле `user: Админ` снято. Путь sources в маркере абсолютный: относительный
`source-checkouts/...` резолвится от `.v8/stands/simple/`, не от корня.

**r15 CLI smoke PASS** — [logs/r15-cli-simple.md](logs/r15-cli-simple.md).
**r15 MCP smoke PASS** (`run-r15-mcp-simple`): изолированный
`CODE_INDEX_HOME`, `daemon run` + HTTP `serve`, `tools/list` = 33
(13 1С-tools), handlers/structure/register writers. Лог:
[logs/r15-mcp-simple.md](logs/r15-mcp-simple.md).
**r22 IB smoke PASS** (`run-r22-ib-simple`): `init` + `build` +
`syntax designer-modules --server --thin-client` (`status=clean`).
Лог: [logs/r22-ib-simple.md](logs/r22-ib-simple.md).
**r01 MCP smoke PASS** (`run-r01-mcp-simple`): изолированный
`UNICA_PROVIDER_STATE_DIR`, stdio `unica` с cwd выгрузки. 6/6.
Лог: [logs/r01-mcp-simple.md](logs/r01-mcp-simple.md).
**r01 apply+docs PASS** (`run-r01-apply-simple`): dryRun `props.set`
отказал `invalid_source`; забор без `ifRev` — `bad_value`; `docs`
через Task (5 poll) — 80 hits; дамп не изменился. 6/6.
Лог: [logs/r01-mcp-apply-simple.md](logs/r01-mcp-apply-simple.md).

## Следующий шаг

Answer42 (живой Test Client) — по отдельной просьбе. Не писать код
фасада. Vanessa/YaXUnit не гонять: в выгрузке нет тестов,
`tools.* = false`. `[tools].enabled` r15 не гоняли. Dual-workspace
Unica NOT_RUN. Публикация `apply` на этой фикстуре не делать: Unica
требует перевыгрузку 2.20.

## Журнал

2026-09-20 → план стыковки подготовлен.
2026-09-20 → по просьбе пользователя выполнен partial CONTINUE-AUDIT r21:
инвентаризация + deep-static S1–S5. Обнаружен существующий batch CLI;
создан INTEGRATION.md. Execution не выполнялся.
2026-09-21 → по просьбе пользователя («следующий репозиторий на свой
выбор») выполнен CONTINUE-AUDIT r20 Answer42: инвентаризация GitLab
`beta`/`0406669a…` + deep-static S1–S5. MCP stdio, `base_url`+`session_id`,
122 tools, `--tool-profile`. Execution не выполнялся.
2026-09-21 → по просьбе пользователя добавлен и разобран r22
`alkoleft/v8-runner-rust` @ `7ce1b062…`: deep-static S1–S5.
2026-09-21 → уточнение по Vanessa: r22 — runner (`test va` / `launch mcp
va` / download single EPF), не замена движка шагов r21; адаптер фасада
при выборе r22 может идти через runner, а не через сырой 1cv8.
2026-09-21 → пользователь подтвердил замену r09 на r22. Состав в
DECISION/FACADE/BRIEF обновлён. Внедрение не начиналось.
2026-09-21 → CONTINUE-AUDIT r01 Unica: SHA `56a67d4a…` совпал с HEAD
`main`; deep-static S1–S5. Патч не нужен. Остаётся r15.
2026-09-21 → CONTINUE-AUDIT r15 code-index-mcp: pinned `4bde72b…` (v1.4.0);
HEAD `309cddb…` не подменялся. CLI ядра + MCP; 1С-tools за демоном;
alias и EDT-detect есть; патч не нужен. Static пяти закрыт.
2026-09-21 → по просьбе пользователя подключена opt-in обвязка
v8-harness и выгрузка simple1CAiConf как стенд `simple`. ИБ не
создавалась; execution по-прежнему запрещён.
2026-09-21 → «давай дальше»: dump-only CLI r15 на стенде `simple`.
`bsl-indexer` 1.4.0: index + search/get/callers PASS. Daemon/MCP и
остальные продукты не запускались; ИБ не создавалась.
2026-09-21 → пользователь разрешил создать ИБ из выгрузки. `init` +
`build` + `syntax designer-modules` PASS (`run-r22-ib-simple`).
Пользователь `Админ` в пустой ИБ отвергнут платформой; относительный
path sources поправлен на абсолютный.
2026-09-21 → «что там дальше по плану — выполняй»: dump-only MCP r15.
Изолированный `CODE_INDEX_HOME` `.v8/work/r15-mcp/home`; HTTP serve
на свободном порту. 7/7 PASS (`run-r15-mcp-simple`). Живой
`tools/list` = 33. Фасад и Unica не запускались.
2026-09-21 → «давай дальше по плану»: smoke Unica `view`/`check`.
Бинарь собран из pinned SHA (релиз v0.12.3 не подменялся). Первый
запуск — timeout 5 с spawn lock debug-бинаря; повтор — 6/6 PASS
(`run-r01-mcp-simple`). `check` на `Document.ЗаказПокупателя`
ответил `source_unreadable` (формат 2.20). `apply` не вызывался.
2026-09-21 → рабочая копия перенесена `C:\MyPtojects\choice-of-tools-1c` →
`C:\MyProjects\choice-of-tools-1c`. Утренний снимок сохранён как
`C:\MyProjects\choice-of-tools-1c.old-20260921`. Абсолютные пути стенда
и smoke поправлены. Журналы прошлых прогонов оставлены как снято.
2026-09-21 → «закомить, если закончено и продолжи по плану»: зафиксирован
r01 `view`/`check`; выполнен `unica.apply` dryRun + `unica.docs`
(`run-r01-apply-simple`, 6/6 PASS). Публикация не вызывалась. Answer42
не запускался.
