# Возможности относительно цели

Версия критериев: 2; источник — [BRIEF.md](BRIEF.md).
Матрица при цели v1 — в снимке `history/goal-v1/CAPABILITY-MAP.md`
(читать только если нужен старый критерий).
Основания обзора — [EVIDENCE.json](EVIDENCE.json), кандидаты —
[INVENTORY.json](INVENTORY.json).
Глубина: r01–r19 overview; r20 PENDING; **r21 DEEP_STATIC по S1–S5**.
Покрытие — по прочитанному объёму. Полная стыковка пяти ещё не закрыта.

Обозначения покрытия: **полное** (в роли кандидата), **частичное**,
**не установлено**, **неприменимо**.

## Матрица

| C* | Кто закрывает | Покрытие | Доказательство | Готовность | Недостаёт |
|---|---|---|---|---|---|
| C1 explore без дампа | **r15 выбран** (13 1С-tools + core); r02 сильный, но не в контуре; r01 частично (`search`/`view`); r19 RAG | r15 частичное; r02 частичное→сильное как наблюдение v1 | c15-bsl-thirteen; c02-six-tools, c02-formats; c01-search-read | r15 продуктовый | Точность графа r15; живой tools/list |
| C2 связи BSL | r15 (индекс callers); r02 хелперы не трассированы; r01 call graph на v0.13 нет | частичное | c15-bsl-thirteen; c01-search-limits | заявлено у r15 | deep-static/стыковка r15 |
| C3 метаданные и УФ | метаданные: r01, r15, r02, r12; УФ: r01 edit, r15 read. Обычные формы в v2 не обязательны; пробел Form.bin не блокер | частичное (достаточно для v2) | c01-forms-managed, c15-forms-managed-src, c02-forms-managed-xml | edit УФ заявлен | стыковка Unica; ОФ не ищем |
| C4 справка API | r01 `unica.docs` выбран; r04 core; r10/r18 не в контуре | частичное→сильное у r01/r04 | c01-docs, c04-*, c10-* | r01 как адаптер контура | проверка на HBK 8.3.27 |
| C5 edit | r01 основной; r12 дубль, не в контуре; r17 только EDT | частичное (УФ+метаданные) | c01-facade, c12-managed-forms | высокая заявка | стыковка Unica; ОФ не требуется |
| C6 static | r01 `unica.check`; r09 CheckConfig/EDT | частичное | c01, c09-eight-tools | продуктовая заявка | компактность отчёта |
| C7 build/run | r01 `unica.run`; r09 build/launch | частичное | c09-eight-tools | высокая заявка | стыковка / execution |
| C8 runtime/UI test | r09 YaXUnit; r20 Answer42 PENDING; **r21 Vanessa: batch single-feature run + status file и MCP run_scenario/get_test_results подтверждены static** | частичное | c09-eight-tools; c21-cli-target; c21-cli-status | r21 static готовность подтверждена, runtime NOT_RUN | r09/r20 static; r21 execution/two-target |
| C9 compact results | r01 typed data; r15 fragments; r02 truncation (не в контуре) | частичное | architecture/tool-surface | заложено | замер токенов; фасад |
| C10 min surface | фасад обязателен; r01 11 tools, r15 широкая, r09 8; r21 MCP 37 active static, **но r21 имеет batch CLI без MCP surface** | частичное | c01-facade, c15, c09-eight-tools, c21-tool-surface, c21-adapter-choice | r21 CLI хорошо ложится за facade | стыковка остальных |
| C11 знания вне окна | r15 SQLite; r01 кэш; r04 | полное у индексных | c15; c01; c04 | высокая | — |
| C12 независимость от адаптера | r01 ядро vs plugin; r15 бинарь; Cursor не критерий | частичное | c01-mcp-json | средняя | свой фасад |
| C13 feedback loop | контур r15→r01→r01.check/r09→r09/r20/r21 | системное, не закрыто одним | синтез v2 | собираемый на бумаге | стыковка; оркестратор |
| C14 без дубля | explore r15 не вместе с r02; edit r01 не вместе с r12/r13; docs unica.docs не вместе с r10/r18 | решение в DECISION | карточки | — | не подключать дубли |

## Альтернативы и сочетания

### Explore

- **Выбран (v2):** r15 как ядро/бинарь за фасадом, не сырой `tools/list`.
- **Не в контуре:** r02 (наблюдение v1: узкий MCP из 6 tools).
- **Не основной:** r01 search, r19 RAG.

### Docs

- **Выбран:** `unica.docs`.
- **Запас/ядро:** r04. Не брать r10/r18 рядом.

### Edit

- **Выбран:** r01 (`unica.apply`/`view`/`check`). Хост не обязан быть Cursor.
- **Не в контуре:** r12/r13.

### Verify / loop

- **Сборка+YaXUnit:** r09.
- **Клиент без тестов:** r01 `unica.run`.
- **UI формы / сценарий:** r20 Answer42 остаётся PENDING. r21 Vanessa
  static подтверждён; для `verify.scenario` предпочтителен batch CLI,
  MCP — дополнительный интерактивный backend.
- **Спецслучаи:** r06, r07, r17 (EDT; конфликт с обязательными ОФ в v1 снят, роль EDT не выросла).

### Предлагаемый минимальный контур (цель v2)

```
агент ← тонкий facade
         ├ explore → r15
         ├ docs    → unica.docs
         ├ edit    → r01
         ├ static  → unica.check и/или r09 Check*
         └ verify  → r09 YaXUnit; form → r20; scenario → r21
```

Все связи `PROPOSED_INTEGRATION`. Стыковка не проверялась
(`VERIFIED_INTEGRATION` нет). Взаимных зависимостей в коде обзора 19
между r01/r15/r09 не найдено; r20/r21 в том обзоре не входили и ещё
не читались.

## Пробелы

1. Стыковка пяти выбранных с фасадом — не исследована (главный пробел v2).
2. r20 Answer42 и r21 Vanessa — заготовки, глубина не достигнута.
3. Точность графа r15 и компактность отчёта r09 — не execution.
4. Call graph на поверхности Unica v0.13 — не поддержан (explore закрывает r15).
5. Структура обычных форм — по-прежнему отсутствует, **не блокер** цели v2.
6. Признаки автоопределения 1С-проекта — не зафиксированы аудитом.

