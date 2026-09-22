# Техническое ТЗ фасада

Дата: 2026-09-22. Версия цели: 2. Источник — методологическое ТЗ
[FACADE-TZ.md](FACADE-TZ.md), дефолты его раздела 14.

**Статус документа:** техническая спецификация для будущей реализации —
интерфейсы, схемы, алгоритмы, раскладка конфигов. **Не код.** Запрет
писать код фасада не снят: он снимается отдельным решением пользователя
([INTEGRATION-PLAN.md](INTEGRATION-PLAN.md), [STATE.md](STATE.md)). Этот
документ можно читать и оспаривать до того решения; ничего из него не
исполняется автоматически.

**Что здесь новое, а что унаследовано.** Контракты по операциям, семь
стыков, бюджет контекста, принципы — из [FACADE-TZ.md](FACADE-TZ.md),
не повторяются подробно, только даются технической формой (схемы,
пороги, алгоритмы). Разбивка на компоненты, конкретные JSON-схемы,
конвенции именования файлов, таксономия ошибок — новые технические
решения этого документа, предложены поверх проверенных фактов, не сами
проверены прогоном.

## 0. Нерешённое до начала кода (явно, не по умолчанию скрыто)

Технический стек и место размещения кода — решения, которые методология
не покрывала. Дефолт ниже — рабочее предположение для этого документа,
не финальное решение; подтвердить или сменить перед первой строкой кода:

- **Рантайм:** Python 3.11+, изолированный venv (тот же приём, что уже
  применялся для Answer42 в этом исследовании — `answer42==0.5.3` в
  своём venv, не глобально).
- **Форма поставки:** CLI-бинарь/entrypoint, поднимающий **stdio MCP
  сервер** (`facade serve --transport stdio --config .v8/facade.yaml`),
  по аналогии с уже проверенным паттерном `r15`/`r01`/`r20`. HTTP —
  опционально, не первично.
- **Место кода:** отдельно от `evaluations/main` (это исследовательское
  дерево, не продукт) — отдельный каталог/репозиторий верхнего уровня
  или вне `choice-of-tools-1c` вовсе. Не определено окончательно.

## 1. Словарь

| Термин | Значение |
|---|---|
| `source` | именованная запись выгрузки в `sources` (путь, формат `cf-xml`/`edt`) |
| `target` | именованная цель в `targets` (ИБ или сторона обмена: путь/строка соединения, роль, привязанный `source` для записи) |
| `at` | адрес узла внутри source-set, формат `"<source-set>:<путь>"` (контракт Unica, раздел 4 [FACADE-TZ.md](FACADE-TZ.md)) |
| adapter | модуль фасада, оборачивающий один продукт (r01/r15/r20/r21/r22) |
| envelope | единый формат ответа фасада агенту (раздел 5) |
| artifact | файл на диске, на который envelope даёт путь вместо инлайна |

## 2. Компоненты

```
facade
 ├ Router               — принимает 7 внешних операций, единственная
 │                         точка входа для агента (MCP tools/list = 7,
 │                         не 33–122 продуктовых)
 ├ ProjectDetector       — 3 маркера по умолчанию (FACADE-TZ.md §14.1),
 │                         решает enabled/disabled на корне
 ├ ConfigLoader          — .v8/facade.yaml, .v8/credentials.local
 ├ TargetRegistry        — резолвит source/target по имени, требует
 │                         default_target только если target не указан
 │                         и в конфиге ровно один
 ├ Adapters
 │   ├ IndexAdapter      → r15 (explore)
 │   ├ UnicaAdapter      → r01 (docs, edit.view, edit.apply, static.unica)
 │   ├ RunnerAdapter     → r22 (static.syntax, build, verify.unit,
 │   │                         verify.scenario transport)
 │   ├ FormAdapter       → r20 (verify.form)
 │   └ ScenarioAdapter   → r21 через RunnerAdapter (verify.scenario)
 ├ ProcessManager        — держит долгоживущие процессы (r01 daemon,
 │                         r15 daemon, r20 stdio-сессия); r22 — one-shot
 ├ ArtifactStore         — .v8/artifacts/**, порог раздела 6
 └ EnvelopeNormalizer    — сводит разные конверты продуктов к единому
                           envelope и единой таксономии ошибок (раздел 7)
```

Правило: Router не содержит 1С-логики, только маршрутизацию и envelope.
Вся продуктовая специфика — в Adapters. Это прямое следствие C12
([FACADE-TZ.md](FACADE-TZ.md) §13) — 1С-логика не завязана на MCP/CLI/
хост.

## 3. Конфигурация

### 3.1 `.v8/facade.yaml`

Дефолт по [FACADE-TZ.md](FACADE-TZ.md) §14.2 — 4 поля на старте.

```yaml
enabled: true

sources:
  main:
    path: source-checkouts/simple1CAiConf
    format: cf-xml          # cf-xml | edt
  cf220:
    path: .v8/work/simple-cf-220
    format: cf-xml

targets:
  simple:
    kind: file-ib            # file-ib | server-ib
    path: .v8/ib/simple
    role: test                # test | dev | never-prod — verify по умолчанию только на test/dev
    write_source: cf220       # куда идут edit.apply/static; см. §7.1
    read_source: main         # откуда explore/docs/edit.view; по умолчанию = write_source
    runner_config: .v8/stands/simple/v8project.yaml   # v8project.yaml самого r22, не путать с этим файлом

default_target: simple
```

`sources`/`targets` — map по имени, не список: адресация всегда по
имени, никогда по индексу (совпадает с принципом «нет молчаливого
дефолта на текущую 1С», раздел 4 [FACADE-TZ.md](FACADE-TZ.md)).

### 3.2 `.v8/credentials.local`

Дефолт [FACADE-TZ.md](FACADE-TZ.md) §14.3, `.env`-подобный, в
`.gitignore`:

```
SIMPLE_TEST_USER_PASSWORD=...
EXCHANGE_A_TOKEN=...
```

Ключ — `<TARGET_UPPER>_<ROLE>`. Никогда не логируется целиком; при
ошибке подстановки — сообщение называет имя переменной, не значение.

## 4. Единый envelope

Все 7 операций отвечают одной формой, независимо от того, что внутри
Unica отдаёт `diagnostics[].code`, r22 — `ok`/`data.report`/
`data.retained_paths`, а Answer42/Vanessa — свои поля (факт из
[VALIDATION.md](VALIDATION.md) S1–S5). `EnvelopeNormalizer` сводит их
сюда:

```json
{
  "ok": true,
  "operation": "edit.apply",
  "target": "simple",
  "data": { "...": "операция-специфичные поля, инлайн если < порога §6" },
  "artifacts": [
    { "kind": "report|screenshot|raw", "path": ".v8/artifacts/...",
      "bytes": 77205, "summary": "80 hits, 5 секций" }
  ],
  "diagnostics": [
    { "code": "stale_revision", "message": "...", "severity": "error" }
  ],
  "duration_ms": 1240
}
```

`ok=false` не означает «фасад сломан» — это честный отказ продукта
(например YaXUnit, раздел 8). Router никогда не превращает `ok=false`
в исключение/молчание — агент обязан увидеть его как обычный ответ.

## 5. Таксономия ошибок фасада

`EnvelopeNormalizer` сводит наблюдённые продуктовые коды к фасадным.
Источник наблюдений — [VALIDATION.md](VALIDATION.md), логи E1–E4.

| Код фасада | Откуда (наблюдённый факт) | Когда |
|---|---|---|
| `target_not_found` | новое (нет прямого аналога у продуктов) | имя `target`/`source` не в `TargetRegistry` |
| `target_ambiguous` | новое | `target` не указан, `default_target` не задан, целей > 1 |
| `provider_unavailable` | Unica `at="bogus:…"` → `provider_unavailable` (E2a) | несуществующий source-set |
| `source_format_unwritable` | Unica `invalid_source`/`source_unreadable` — «export format 1.0 is older than the writable profile 2.20» | `edit.apply`/`static` на нерукописном/старом дампе без `write_source` |
| `missing_ifrev` | Unica отказ `apply` без `ifRev` на публикации | `dryRun:false` без предшествующего `dryRun:true` в этой же сессии |
| `stale_revision` | Unica `stale_revision` на повторном `ifRev` | публикация с устаревшим `ifRev` |
| `config_invalid` | r22 `invalid_argument` на несуществующий `--config` (E2b) | битый/отсутствующий `runner_config` |
| `extension_name_mismatch` | E1: `source-set` в yaml ≠ реальный `Name` расширения в ИБ | перед `verify.unit`, best-effort проверка (§7.4) |
| `verify_unavailable` | E1: YaXUnit находит 0 сценариев при активном расширении | `verify.unit` не может дать честный pass/fail — см. раздел 8 |
| `docs_task_transport_failed` | Unica: разный `UNICA_PROVIDER_STATE_DIR` на старт/опрос `docs` | нарушение инварианта §7.6 |
| `process_start_timeout` | r01 живой прогон: первый запуск — timeout 5с на spawn lock debug-бинаря (журнал STATE.md 2026-09-21) | старт демона/сессии не уложился в таймаут — повтор, не сразу отказ агенту |
| `artifact_write_failed` | новое | `ArtifactStore` не смог записать файл |

## 6. Порог инлайна и `ArtifactStore`

Источник чисел — [logs/e3-chain-simple.md](logs/e3-chain-simple.md)
(раздел 8 [FACADE-TZ.md](FACADE-TZ.md)).

**Порог: 8192 байт.** Ответ ≤ порога — инлайн в `data`. Ответ > порога —
`ArtifactStore` пишет файл, `data` содержит только summary (счётчики,
первые N совпадений), `artifacts[]` — путь и точный размер.

Проверка по уже измеренным операциям: `explore` 3202, `edit.view` 3260,
`edit.apply` dryRun 1616, `static` 568/484, `verify.unit` 5304,
`verify.scenario` 3964, `verify.form.active_window` 2752 — все инлайн.
`verify.form.start_session` 9960 — **пересекает порог**, уходит в файл
автоматически (это совпадает с пометкой E3 «на грани — лучше выдержка»,
не требует отдельного правила). `docs` (77 205) и `verify.form.
screenshot` PNG (180 197) — безусловно в файл независимо от порога,
это два зафиксированных методологией обязательных случая, не
подчиняются общему правилу «по размеру».

Имя файла: `.v8/artifacts/<operation>-<target>-<unix_ms>.<ext>`
(`.json` для отчётов, `.png` для скриншотов). Каталог — не в git
(добавить в `.gitignore`, как рабочие дампы `.v8/work/**`).

## 7. Обработка семи стыков (техническая форма)

Каждый пункт — из раздела 9 [FACADE-TZ.md](FACADE-TZ.md), здесь —
конкретный алгоритм adapter'а.

### 7.1 Формат 2.20 vs 1.0

`UnicaAdapter.edit_view/docs/explore` используют `target.read_source`.
`UnicaAdapter.edit_apply/static` используют `target.write_source`. Если
`write_source` не задан в конфиге — используется `read_source`, и при
первом же `invalid_source`/`source_unreadable` от Unica adapter
возвращает `source_format_unwritable` с сообщением, что нужно завести
отдельный `write_source` в `.v8/facade.yaml` — **не** пытается сам
подобрать или сконвертировать дамп.

### 7.2 Владелец ИБ

`edit.apply` **не** триггерит билд автоматически. После успешного
`dryRun:false` adapter добавляет в `diagnostics` информационную запись
(`severity: "info"`, код `build_required`): «правка в дампе, для
попадания в ИБ нужен отдельный `static`/build через `target`». Явный
самостоятельный build — вне 7 операций раздела 3 методологического ТЗ,
вызывается той же verify.unit-цепочкой (`RunnerAdapter` сам гоняет
build перед syntax/YaXUnit, это его внутренний шаг, не отдельная внешняя
операция).

### 7.3 Владелец рабочего дампа

`RunnerAdapter.dump()` (внутренний вызов, не внешняя операция) пишет в
`.v8/work/<target>-<unix_ms>/`, никогда не переиспользует существующий
каталог молча. Если конфиг явно указывает фиксированный путь дампа —
adapter логирует в `diagnostics` (`severity: "warning"`, код
`work_dump_overwrite`) факт перезаписи перед вызовом, не после.

### 7.4 Имя расширения у `r22`

Перед `verify.unit` `RunnerAdapter` делает best-effort сверку: если
`runner_config` описывает `source-set` типа extension, adapter (если
есть дешёвый способ узнать реальное имя объекта в ИБ — например через
уже полученный `static`/`syntax` вывод в этом же цикле) сверяет имя.
Несовпадение → `extension_name_mismatch` **до** вызова YaXUnit, не после
непонятного «0 сценариев». Если дешёвого способа сверки нет — adapter
пропускает проверку и передаёт отказ `r22` как есть; ложноотрицательных
не создаёт.

### 7.5 `--sources` YaXUnit vs `DESIGNER`-проект

`RunnerAdapter` не вызывает `tools download yaxunit --sources` для целей
с `format: DESIGNER` в `runner_config` — использует путь `load`/`merge`
скомпилированного `.cfe`. Это статическое правило по `format` цели, не
попытка запустить оба пути и посмотреть, какой сработает.

### 7.6 Асинхронность `docs`

`UnicaAdapter` держит **один** `UNICA_PROVIDER_STATE_DIR` на весь
процесс фасада (не per-call). `docs()` вызывает `unica.docs`, затем сам
поллит `unica.task.result` (интервал — экспоненциальный бэкофф от
200 мс, таймаут по умолчанию 60 с, настраиваемый), агенту возвращается
уже готовый envelope — polling полностью скрыт внутри adapter'а, агент
не видит промежуточных `status: queued/working`.

### 7.7 Ненадёжность incremental build

`RunnerAdapter.build()` — внутренний шаг. Первая попытка — partial;
при отказе с сообщением про «файл-список загружаемых файлов» —
одна автоматическая повторная попытка с `--full-rebuild`, и только
её результат уходит в envelope (с `diagnostics` пометкой, что
понадобился fallback). Не более одной автоматической повторной попытки
— второй отказ уходит агенту как есть.

## 8. `verify.unit` — честная реализация открытого риска (E1)

Прямое исполнение дефолта [FACADE-TZ.md](FACADE-TZ.md) §14.5.
`RunnerAdapter.verify_unit()`:

1. Гоняет build (с fallback §7.7) и `test yaxunit` как есть.
2. Если результат — `0` найденных сценариев при активном движке и
   активном расширении (сигнатура, зафиксированная в
   [logs/r22-yaxunit-e1tests-simple.md](logs/r22-yaxunit-e1tests-simple.md)) —
   envelope `ok=false`, `diagnostics=[{code:"verify_unavailable",
   severity:"error", message:"YaXUnit не резолвит модуль стороннего
   расширения — открытый риск, см. FACADE-TZ.md §10"}]`.
3. **Не подменяется** `verify.form`/`verify.scenario` автоматически —
   это решение агента/пользователя, не фасада.
4. Если сценарии найдены (после изоляции причины E1 или на другом
   стенде, где расширение резолвится) — обычный envelope с
   pass/fail-отчётом, без специальной обработки.

## 9. Жизненный цикл процессов

| Продукт | Модель | Решение фасада |
|---|---|---|
| r01 Unica | долгоживущий stdio-демон | один демон на процесс фасада; несколько целей — через `at="<source-set>:…"` в одном `v8project.yaml`, если пути под общим корнем workspace (§4 [FACADE-TZ.md](FACADE-TZ.md) ограничение по workspace-relative путям); иначе — второй cwd/процесс (доказано `run-r01-dual-simple`) |
| r15 code-index-mcp | демон + `serve` | `daemon run` при старте фасада; `serve --config` с `[tools].enabled`; несколько выгрузок — несколько alias в одном `[[paths]]`, не несколько демонов |
| r22 v8-runner | one-shot CLI | новый процесс на каждый вызов, `--config <target.runner_config>`; без общего состояния между вызовами |
| r20 Answer42 | долгоживущая stdio-сессия | один MCP-процесс, `session_id = target`; повторный `verify.form` на той же цели переиспользует сессию (идемпотентность, принцип 8 [FACADE-TZ.md](FACADE-TZ.md) §11 расширенный дефолтами методологии), новый процесс — только на новую цель |
| r21 Vanessa | нет отдельного процесса | транспорт — `RunnerAdapter` (`r22 test va`) |

`ProcessManager` отвечает за то, чтобы при остановке фасада не оставались
осиротевшие демоны/сессии — явный shutdown-хук на каждый долгоживущий
процесс.

## 10. Приёмочный тестовый контур (стенд `simple`)

Не подменяет решение пользователя «разрешить писать код» — это чек-лист
на момент, когда решение принято. Каждый пункт — воспроизведение уже
существующего прогона **через фасад**, не заново придуманный сценарий:

1. `explore` на `main` — сопоставимо с
   [logs/e3-chain-simple.md](logs/e3-chain-simple.md) шаг 1.
2. `docs` на `main`, запрос «НаборЗаписей» — итог должен сойтись с
   [logs/r01-mcp-apply-simple.md](logs/r01-mcp-apply-simple.md)
   (5 секций/80 hits), артефакт ушёл в файл, в envelope — только summary.
3. `edit.view`/`edit.apply dryRun` на `cf220` — сопоставимо с
   [logs/r01-mcp-apply-cf220-simple.md](logs/r01-mcp-apply-cf220-simple.md).
4. `static` (оба движка) на `cf220`.
5. `verify.unit` на `simple` — envelope должен быть `ok=false`,
   `code=verify_unavailable`, **не** зелёный (регресс — если фасад
   вдруг покажет `ok=true`, это баг фасада, а не починка E1).
6. `verify.form` — session start/window/screenshot, сопоставимо с
   [logs/r20-mcp-simple.md](logs/r20-mcp-simple.md); PNG путь, не base64
   в ответе.
7. `verify.scenario` — `smoke-engine.feature`, сопоставимо с
   [logs/r22-va-smoke-simple.md](logs/r22-va-smoke-simple.md).
8. Два target одновременно (`simple` + вторая копия ИБ) — операция на
   одном не меняет sha256 другого, как в
   [logs/r01-r22-e2-two-targets.md](logs/r01-r22-e2-two-targets.md).
9. Полный цикл 1–7 подряд — сумма байт в чат укладывается в ≈30 КБ
   (раздел 8 [FACADE-TZ.md](FACADE-TZ.md)); если превышает — регресс
   порога §6, не «новая находка про контекст».

## 11. Вне рамок

Не меняется относительно [FACADE-TZ.md](FACADE-TZ.md) §12: свой
парсер/индекс/справка/сборка/UI-движок не пишутся; фасад не реализует
протокол обмена; Cursor не обязателен как хост; обычные формы не
требуются. Дополнительно на техническом уровне: фасад не хранит копию
исходников продуктов и не патчит их код — патч продукта (порядок
доработки, [FACADE-TZ.md](FACADE-TZ.md) §12) — отдельная задача вне
этого ТЗ, с отдельной записью зачем.

## 12. Прослеживаемость

Все числа и коды ошибок в этом документе — из
[FACADE-TZ.md](FACADE-TZ.md), [VALIDATION.md](VALIDATION.md),
[logs/e3-chain-simple.md](logs/e3-chain-simple.md),
[logs/r01-r22-e2-two-targets.md](logs/r01-r22-e2-two-targets.md),
[logs/r22-yaxunit-e1tests-simple.md](logs/r22-yaxunit-e1tests-simple.md),
[logs/r15-e4-stdio-whitelist-simple.md](logs/r15-e4-stdio-whitelist-simple.md).
Схемы конфигов, envelope, таксономия ошибок §5 и алгоритмы §7–9 —
новые технические решения этого документа, не проверены прогоном; при
написании кода могут потребовать точечной правки, если реальность API
продуктов не ляжет в предложенную форму. Новых прогонов для составления
документа не выполнялось.
