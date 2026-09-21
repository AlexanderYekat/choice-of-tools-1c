# Состояние main / 20260920T044856175227Z

Версия цели: **2**. Статус: COMPOSITION_R22_CHOSEN; STATIC_S1S5_FIVE_DONE;
FIXTURE_HARNESS_ATTACHED; R15_CLI_SMOKE_PASS; R15_MCP_SMOKE_PASS;
R22_IB_SMOKE_PASS; R01_MCP_SMOKE_PASS; R01_APPLY_DOCS_SMOKE_PASS;
R22_DUMP_CF220_PASS; R01_APPLY_CF220_PASS; R22_YAXUNIT_VA_EMPTY_FAIL; R22_VA_SMOKE_PASS;
R20_MCP_SMOKE_PASS; R01_APPLY_PUBLISH_PASS; R15_MCP_WHITELIST_PASS;
R01_DUAL_WORKSPACE_PASS.
Последнее обновление: 2026-09-21.

Состав контура выбран ([DECISION.md](DECISION.md)): Unica, code-index-mcp,
**v8-runner (r22 вместо r09)**, Answer42, Vanessa, тонкий фасад.
План: [INTEGRATION-PLAN.md](INTEGRATION-PLAN.md).
Стыковка: **r01 Unica, r15 code-index-mcp, r20 Answer42, r21 Vanessa
и r22 v8-runner достигли DEEP_STATIC по S1–S5**. r15 CLI, r15 daemon+MCP,
r22 init/build/syntax, r01 `view`/`check`, r01 `apply` dryRun + `docs`
на рукописном дампе, r22 `dump` 2.20 и r01 `apply` dryRun на этой
выгрузке — PASS. YaXUnit на simple — отказ (нет тестов/профиля).
Vanessa smoke-engine.feature 1/1 PASS. **r20 Answer42 smoke PASS**.
**r01 `apply` публикация на cf220 PASS**. **r15 `[tools].enabled`
PASS** (живой `tools/list` = 9). **r01 dual-workspace PASS**
(две выгрузки, один демон). Фасад не писался.

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
  `apply` dryRun на рукописном дампе — `invalid_source` (1.0 vs 2.20);
  на Designer dump `.v8/work/simple-cf-220` — план `preview` + `rev`;
  публикация `dryRun:false` + `ifRev` — `mode=published`; stale `ifRev`
  отказал; `docs` НаборЗаписей — 5 секций / 80 hits.
  Dual-workspace: два cwd, один `--daemon`, Comment не смешался.
- **r15 code-index-mcp: AVAILABLE / DEEP_STATIC**, commit
  `4bde72b60a09187c0667d451a02c7be5e0169835` (ветка `main`, v1.4.0).
  HEAD 2026-09-21 = `309cddb…` (v1.4.2); SHA не подменялся.
  CLI ядра + HTTP MCP dump-only PASS; живой `tools/list` = 33
  (13 1С-tools); alias `simple`. `[tools].enabled` из 9 имён explore
  плюс опечатка: `tools/list` = 9; `grep_code` и `get_object_structure`
  — `-32602`; `get_form_handlers` живой.
- r09: OVERVIEW, **не в контуре** (C14, решение 2026-09-21).
- **r20 Answer42: AVAILABLE / DEEP_STATIC**, commit
  `0406669a88144834bfdf6086c7040a25cb76d24c` (ветка `beta`, v0.5.3).
  Runtime smoke PASS (`run-r20-mcp-simple`): живой `tools/list` = 103
  (`ui` + `--disable-rag`); `start_session` → `active_window` →
  `screenshot` → дубль id отказал → `stop_session`.
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
ИБ создана. Designer dump 2.20 снят в `.v8/work/simple-cf-220` (исходный
`source-checkouts/simple1CAiConf` не затирался). YaXUnit на simple:
клиент стартовал, JUnit не появился (нет движка/сценариев в ИБ).
Vanessa: сначала `tests.va.profile is not configured`; после feature +
EPF — **1/1 PASS** (`run-r22-va-smoke-simple`). **Runtime r20 PASS**
(`run-r20-mcp-simple`). Публикация `apply` (`dryRun:false` + `ifRev`
с cf220) **PASS**. Dual live Test Client r20 NOT_RUN.

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
**r22 Designer dump 2.20 PASS** (`run-r22-dump-cf220`): `dump --mode full`
в `.v8/work/simple-cf-220`; корни `version="2.20"`.
Лог: [logs/r22-dump-cf220-simple.md](logs/r22-dump-cf220-simple.md).
**r01 apply dryRun на 2.20 PASS** (`run-r01-apply-cf220`): план preview,
файлы не изменились. Лог:
[logs/r01-mcp-apply-cf220-simple.md](logs/r01-mcp-apply-cf220-simple.md).
**r22 YaXUnit на simple FAIL** (`run-r22-yaxunit-simple`): нет движка в ИБ.
**r22 Vanessa smoke PASS** (`run-r22-va-smoke-simple`): написан
`tests/features/smoke-engine.feature`, EPF 1.2.043.1, 1/1 за 122 с.
Лог: [logs/r22-va-smoke-simple.md](logs/r22-va-smoke-simple.md).
**r20 Answer42 smoke PASS** (`run-r20-mcp-simple`): venv `answer42==0.5.3`,
stdio `--tool-profile ui --disable-rag`; `tools/list` = 103; сессия к
`.v8/ib/simple`; окно «Простая конфигурация»; PNG path 296716 bytes;
дубль `session_id` отказал; `stop_session`. Лог:
[logs/r20-mcp-simple.md](logs/r20-mcp-simple.md).
**r01 apply publish PASS** (`run-r01-apply-publish`): dryRun preview
`rev` `f83d6c98…`; `dryRun:false` + `ifRev` — `mode=published`;
`Documents/ЗаказПокупателя.xml` получил
`<Comment>r01-publish-ifRev-20260921</Comment>`; повтор того же `ifRev`
— `stale_revision`. Рукописный дамп и ИБ не трогались. Лог:
[logs/r01-mcp-apply-publish-simple.md](logs/r01-mcp-apply-publish-simple.md).
**r15 `[tools].enabled` PASS** (`run-r15-mcp-whitelist`): HTTP `serve
--config` без `--path`; `tools/list` = 9; опечатка в логе; отказ
`-32602` на `grep_code` и `get_object_structure`. Лог:
[logs/r15-mcp-whitelist-simple.md](logs/r15-mcp-whitelist-simple.md).
**r01 dual-workspace PASS** (`run-r01-dual-simple`): два stdio с cwd
`simple1CAiConf` и `.v8/work/simple-cf-220`, один `--daemon` pid 23920.
`view {}` вернул свой корень каждому; Comment пустой на рукописном
дампе и `r01-publish-ifRev-20260921` на cf220, повторный view A не
смешался. Квитанции: один `coreIdentityDigest`, два `requestScopeHash`.
XML документов не изменились. Лог:
[logs/r01-mcp-dual-simple.md](logs/r01-mcp-dual-simple.md).

## Следующий шаг

Не писать код фасада. Dual live Test Client Answer42 — следующий
эксперимент. stdio-whitelist r15 и связка `--path`+`--config` NOT_RUN
(`serve --help`: `--path` игнорирует конфиг). YaXUnit на simple
по-прежнему без расширения/модулей. Две ИБ Unica и два source-set
в одном yaml NOT_RUN. Рабочий дамп `.v8/work/simple-cf-220` несёт
smoke-Comment; повторный Designer dump затрёт его.

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
2026-09-21 → по просьбе: Designer `dump --mode full` из ИБ simple в
`.v8/work/simple-cf-220` (`version="2.20"`). `unica.apply` dryRun на
этой выгрузке — preview PASS. YaXUnit all — клиент без движка, JUnit
нет (клиент убит после ожидания). Vanessa — нет `tests.va.profile`.
2026-09-21 → пользователь указал ошибку: тесты надо написать, а не ждать
их в дампе. Добавлен `tests/features/smoke-engine.feature`, Vanessa EPF
1.2.043.1, `test --no-build va` — 1/1 PASS (`run-r22-va-smoke-simple`).
2026-09-21 → «продолжи что там по плану? answer42»: изолированный venv
`answer42==0.5.3`, stdio MCP `--tool-profile ui`, smoke на ИБ simple —
7/7 PASS (`run-r20-mcp-simple`). Публикация `apply` не вызывалась.
Фасад не писался.
2026-09-21 → «давай дальше, что по плану»: публикация `unica.apply`
(`dryRun:false` + `ifRev`) на `.v8/work/simple-cf-220` — 6/6 PASS
(`run-r01-apply-publish`). Фасад не писался.
2026-09-21 → «давай дальше по плану»: dump-only `[tools].enabled` r15.
Изолированный `CODE_INDEX_HOME` `.v8/work/r15-whitelist/home`; HTTP
`serve --config` без `--path`. 7/7 PASS (`run-r15-mcp-whitelist`).
`tools/list` = 9; опечатка предупреждена; вне списка `-32602`.
Фасад не писался.
2026-09-21 → «продолжай дальше по плану»: dual-workspace Unica.
Два stdio MCP, один `--daemon` (pid 23920) на изолированном
`UNICA_PROVIDER_STATE_DIR`. 11/11 PASS (`run-r01-dual-simple`).
`view` не смешал корни и Comment; sha256 XML не изменился.
`apply` не вызывался. Фасад не писался.
