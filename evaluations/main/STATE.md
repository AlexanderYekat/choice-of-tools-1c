# Состояние main / 20260920T044856175227Z

Версия цели: **2**. Статус: COMPOSITION_R22_CHOSEN; STATIC_S1S5_FIVE_DONE;
FIXTURE_HARNESS_ATTACHED; R15_CLI_SMOKE_PASS; R15_MCP_SMOKE_PASS;
R22_IB_SMOKE_PASS; R01_MCP_SMOKE_PASS; R01_APPLY_DOCS_SMOKE_PASS;
R22_DUMP_CF220_PASS; R01_APPLY_CF220_PASS; R22_YAXUNIT_VA_EMPTY_FAIL; R22_VA_SMOKE_PASS;
R20_MCP_SMOKE_PASS; R01_APPLY_PUBLISH_PASS; R15_MCP_WHITELIST_PASS;
R01_DUAL_WORKSPACE_PASS; R20_DUAL_LIVE_PASS; R22_YAXUNIT_CROSSEXT_DISCOVERY_UNRESOLVED;
R01_E2A_MULTI_SOURCESET_PASS; R22_E2B_TWO_IBS_PASS; E3_CHAIN_CONTEXT_BUDGET_PASS.
Последнее обновление: 2026-09-22.

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
(две выгрузки, один демон). **r20 dual live Test Client PASS**
(два `base_url`, один stdio MCP). **E1 YaXUnit — движок и тестовое
расширение реально установлены и запускаются, но обнаружение тестового
модуля соседним расширением не работает** (`Метод объекта не обнаружен`
для любого метода модуля из динамического `Выполнить()`); причина не
изолирована (рукописный scaffold vs общее ограничение платформы),
критерий E1 не закрыт. Фасад не писался.

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
  2026-09-22: найден и локально исправлен (не опубликован) баг
  `load --mode merge` на Windows (двойной префикс пути `\\?\` ломает
  `/MergeCfg`); патч только в локальной копии тула, не в этом репозитории.

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
с cf220) **PASS**. Dual live Test Client r20 PASS
(`run-r20-mcp-dual`).

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
**r22 YaXUnit E1 повторно FAIL, причина не в отсутствии движка**
(`run-r22-yaxunit-crossext-discovery-simple`, 2026-09-22): движок 25.12 и
тестовое расширение `e1tests` установлены и активны, SafeMode отключён,
свойства модуля сверены с эталонным тестовым модулем самого YaXUnit —
`test yaxunit` всё равно находит 0 сценариев. Инструментированная локальная
копия YaXUnit доказала: `Выполнить()` не резолвит модуль `ТестыE1` по имени
из кода соседнего расширения ни для одного метода (проверено и на
`ИсполняемыеСценарии`, и на отдельном тривиальном пробном методе). Причина —
рукописный scaffold расширения (нет EDT/Designer в среде) или общее
ограничение платформы — не изолирована. Лог:
[logs/r22-yaxunit-e1tests-simple.md](logs/r22-yaxunit-e1tests-simple.md).
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
**r20 dual live Test Client PASS** (`run-r20-mcp-dual`): один stdio,
`dual-a` на `.v8/ib/simple` и `dual-b` на копии
`.v8/work/r20-dual/ib-b`. File-ibsrv `8424` и `10104`;
`sessions_list` count=2; `stop` A оставил B. Заголовки окон совпали
(копия той же конфигурации). Скрипт exit 1 из-за сравнения
`as_posix()` с ключом на `\`; разбор JSON — критерий выполнен,
повтор 1С не запускался. Лог:
[logs/r20-mcp-dual-simple.md](logs/r20-mcp-dual-simple.md).

## Следующий шаг

План переписан 2026-09-22 под этап исполнения:
[INTEGRATION-PLAN.md](INTEGRATION-PLAN.md). Очередь по близости к цели,
не по дешевизне прогона.

1. **E1 YaXUnit на simple — ПРИОСТАНОВЛЕН как открытый риск, не PASS.**
   Движок и тестовое расширение установлены и запускаются
   (build/load/merge/SafeMode — всё PASS), но `test yaxunit` находит
   0 сценариев. Проверены и исключены все гипотезы уровня конфигурации:
   порядок/приоритет расширений, `filter.extensions` в config.json,
   алфавитное имя расширения, пересборка после переименования; ключевая
   новая находка — обычный **статический** (не только динамический
   `Выполнить()`) вызов чужого модуля расширения тоже падает в рантайме
   с той же ошибкой, хотя компилируется без замечаний. Причина не
   изолирована (см. [logs/r22-yaxunit-e1tests-simple.md](logs/r22-yaxunit-e1tests-simple.md),
   раздел «Round 2»). По прямому указанию пользователя работа по E1
   остановлена 2026-09-22, очередь продолжена без него. До изоляции
   причины `verify.unit` через YaXUnit не считать готовым к фасаду.
   **Долг:** инструментация внутри `YAXUNIT` в `.v8/ib/simple` не
   откачена — учитывать при следующей работе с этим стендом.
2. **E2 две цели — ЗАКРЫТ, PASS.** E2a (Unica, два source-set в одном
   yaml, один процесс) — 8/8 PASS: `at="main:…"`/`at="cf220:…"` резолвятся
   раздельно, `at="bogus:…"` — именованный отказ
   (`provider_unavailable`), оба дампа не изменились. Путь `source-set`
   должен быть workspace-relative и не выходить за корень workspace
   (абсолютные пути Unica отклоняет как невалидный yaml) — временный
   конфиг пришлось класть в корень репозитория и сразу удалить после
   прогона. E2b (r22, два yaml/два процесса на `.v8/ib/simple` и готовой
   копии `.v8/work/r20-dual/ib-b`) — PASS: операция на одной цели не
   меняет sha256 файла ИБ другой; несуществующий `--config` — явный отказ
   `invalid_argument`, без молчаливого дефолта. r21 simultaneous остаётся
   UNKNOWN осознанно (не проверялось в этом раунде). Подробности:
   [logs/r01-r22-e2-two-targets.md](logs/r01-r22-e2-two-targets.md).
3. **E3 сквозной прогон и цена контекста — ЗАКРЫТ, PASS.** Один реальный
   проход explore → docs → edit.view/apply dryRun → static → build →
   verify.unit → verify.form → verify.scenario, с замером байт/строк на
   каждом из 8 шагов внешней поверхности. Только два шага обязаны уходить
   в файл: `docs` (77 205 байт/800 строк, асинхронная задача, финальный
   payload — полный список хитов, не выжимка) и скриншот Answer42
   (180 КБ PNG, путь в JSON, не инлайн). Остальные шаги — единицы КБ.
   Сумма «как есть» за цикл ≈ 290 КБ; при обязательной выгрузке docs и
   PNG в файл — ≈ 30 КБ в чат. Бюджет контекста не блокер, если фасад
   с самого начала делает пост-обрезку для этих двух шагов. Составлен
   список из 7 стыков между продуктами (формат 2.20/1.0, владение ИБ,
   владение рабочим дампом, разрешение имени расширения по source-set,
   несовместимость `--sources` YaXUnit с DESIGNER-проектом,
   асинхронность `docs`, ненадёжность incremental build после насыщенной
   работы с расширениями). `verify.unit` в этом проходе — честный
   `ok=false` (E1 не закрыт), это ожидаемо и записано как есть, не как
   PASS. smoke-`Comment` в `.v8/work/simple-cf-220` не тронут в этом
   прогоне (только read-only вызовы). Подробности:
   [logs/e3-chain-simple.md](logs/e3-chain-simple.md).
4. **E4 r15 stdio-whitelist и `--path` + `--config` — ТЕКУЩИЙ ШАГ.**
   Догоняющее, ничего не блокирует.

Код фасада по-прежнему не писать: запрет снимается отдельным решением
пользователя после критериев завершения этапа.

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
2026-09-21 → «давай дальше по плану»: dual live Test Client Answer42.
Один stdio MCP, две файловые ИБ (`simple` и копия `ib-b`). 12/12 по
разбору JSON (`run-r20-mcp-dual`); скрипт exit 1 на сравнении слэшей
в `shared_file_key`. `click_button` не вызывался. Фасад не писался.
2026-09-22 → «перепиши план»: план этапа static S1–S5 выполнен и
заморожен в [history/plan-static-s1s5/](history/plan-static-s1s5/);
[INTEGRATION-PLAN.md](INTEGRATION-PLAN.md) переписан под этап
исполнения (E1 YaXUnit → E2 две цели → E3 сквозной прогон и цена
контекста → E4 stdio-whitelist r15). Очередь пересортирована: прежний
следующий шаг (stdio-whitelist) отодвинут как не блокирующий. Добавлен
второй порог существенной проблемы — непомещающийся бюджет контекста
по `success_criteria[0]`. Прогонов не выполнялось, факты и статусы
не менялись, фасад не писался.
2026-09-22 → «продолжи дальше по плану»: начат E1 (разрешение на установку
расширения получено отдельным вопросом). Установлен движок YaXUnit 25.12
и рукописное тестовое расширение `e1tests` (нет EDT/Designer в среде —
Designer XML собирался вручную методом проб против реальных ошибок
платформы). Найден и локально исправлен баг `v8-runner load --mode merge`
на Windows (не опубликован). `test yaxunit` находит 0 сценариев несмотря
на то, что оба расширения активны и SafeMode отключён. По запросу
пользователя (не переходить сразу к гипотезе load-order/priority)
инструментирована локальная копия YaXUnit: доказано, что модуль `ТестыE1`
целиком не резолвится по имени из динамического кода соседнего
расширения — не проблема сигнатуры `ИсполняемыеСценарии` и не проблема
свойств модуля (сверены с эталонным тестовым модулем самого YaXUnit).
Причина не изолирована: рукописный scaffold vs общее ограничение
платформы. E1 остаётся открытым. Записано честно как FAIL с диагностикой,
не как PASS. Диагностическая инструментация оставлена в `YAXUNIT`
внутри `.v8/ib/simple` — требует отката перед повторным использованием
стенда. Подробности:
[logs/r22-yaxunit-e1tests-simple.md](logs/r22-yaxunit-e1tests-simple.md),
[reports/r22.md](reports/r22.md), claim
`c22-yaxunit-crossext-discovery-unresolved-simple` в EVIDENCE.json.
2026-09-22 → продолжение той же сессии: по инструкции пользователя проверены
и исключены все оставшиеся гипотезы уровня конфигурации — порядок/приоритет
расширений (по документации это только очередь `&Перед/&После/&Вместо`, не
видимость), `filter.extensions` в config.json YaXUnit (нашёлся в их issue
#526, добавлен в локальный патч v8-runner), алфавитный порядок имени
расширения (`e1tests` → `AE1TESTS`), пересборка `YAXUNIT` после
переименования. Новая находка: **обычный статический вызов**
`ТестыE1.Пинг();` внутри `YAXUNIT` компилируется без ошибки, но падает в
рантайме с той же ошибкой — то есть дело не в `Выполнить()`, а в чём-то на
уровне рантайма; при этом факт успешной компиляции через
`LoadConfigFromFiles` оказался ненадёжным индикатором резолвинга ссылки.
Причина всё ещё не изолирована. По прямому указанию пользователя
(«дальше переходить») E1 зафиксирован как открытый риск, диагностика
остановлена, работа продолжена по E2. Диагностика v8-runner
(`filter.extensions`, `debug`-уровень лога) откачена и пересобрана — влияла
бы на все будущие прогоны `test yaxunit`; патч `/MergeCfg` (реальный баг)
оставлен. Инструментация внутри `YAXUNIT` в `.v8/ib/simple` — всё ещё не
откачена, долг сохраняется. Подробности:
[logs/r22-yaxunit-e1tests-simple.md](logs/r22-yaxunit-e1tests-simple.md)
(раздел «Round 2»), claim
`c22-yaxunit-crossext-hypotheses-ruled-out-simple` в EVIDENCE.json.
2026-09-22 → «дальше переходить»: E2 выполнен и закрыт. E2a Unica — один
stdio-процесс, один yaml с двумя `source-set` (`main`, `cf220`), адресация
`at="имя:путь"`; выяснилось, что Unica требует workspace-relative пути без
выхода за корень (абсолютные пути отклоняет как невалидный yaml) —
временный `v8project.yaml` в корне репозитория, удалён сразу после
прогона. 8/8 PASS (`run-r01-e2a-multi-sourceset-simple`). E2b r22 — два
отдельных процесса `v8-runner` с разными `--config` на `.v8/ib/simple` и
готовой копии `.v8/work/r20-dual/ib-b`; `syntax designer-modules` на обеих
целях чисто, sha256 каждой ИБ меняется только от своей операции,
несуществующий `--config` — явный отказ. PASS
(`run-r22-e2b-two-ibs-simple`). Новых ИБ не создавалось. Диагностический
долг по E1 (инструментация в `YAXUNIT`) не устранялся в этом шаге.
Подробности: [logs/r01-r22-e2-two-targets.md](logs/r01-r22-e2-two-targets.md).
2026-09-22 → «закомить всё и приступай к следующему этапу»: коммит
`092bb0a` (E1 + E2). Дальше выполнен E3 — один реальный проход по всей
цепочке восьми операций внешней поверхности с замером байт/строк на
каждом шаге. `docs` (77 205 Б) и скриншот Answer42 (180 КБ PNG) —
единственные обязательные файловые артефакты; остальное укладывается в
чат. Бюджет цикла: ≈290 КБ «как есть», ≈30 КБ при обязательной выгрузке
двух этих шагов. Список из 7 стыков между продуктами составлен. `build`
на `main` один раз отказал в partial-режиме («Ошибка чтения
файла-списка загружаемых файлов») после насыщенной серии пересборок
расширений в E1 — вылечено `--full-rebuild`, зафиксировано как отдельный
стык. `verify.unit` честно FAIL (E1 не закрыт). Подробности:
[logs/e3-chain-simple.md](logs/e3-chain-simple.md).
