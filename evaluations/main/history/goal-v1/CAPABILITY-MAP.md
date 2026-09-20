# Возможности относительно цели

Версия критериев: 1; источник — [BRIEF.md](BRIEF.md).
Основания — [EVIDENCE.json](EVIDENCE.json), кандидаты — [INVENTORY.json](INVENTORY.json).
Глубина: overview. Покрытие — по прочитанному объёму, не по обещаниям README.

Обозначения покрытия: **полное** (в роли кандидата), **частичное**,
**не установлено**, **неприменимо**.

## Матрица

| C* | Кто закрывает | Покрытие | Доказательство | Готовность | Недостаёт |
|---|---|---|---|---|---|
| C1 explore без дампа | r02 основной; r15 альтернатива (13 1С-tools + core); r01 частично (`search`/`view`); r19 RAG | r02 частичное→сильное; r15 частичное; r01 частичное; r19 слабое | c02-six-tools, c02-formats; c15-bsl-thirteen; c01-search-read | r02/r15 продуктовые | Точность графа; ordinary Form.bin |
| C2 связи BSL | r02 (хелперы, код хелперов не трассирован); r15 (индекс callers + 1С-tools); r01 слабее (symbol/call graph на v0.13 не поддержаны) | частичное | c01-search-limits; c15-bsl-thirteen | заявлено сильно | deep-static helpers r02 |
| C3 метаданные и оба типа форм | метаданные: r01, r02, r12, r15; управляемые формы: r01/r12 edit, r02/r15 read; **обычные формы как структура — не закрыты** (r17 явный отказ; r12 только правило) | частичное / пробел | c01-forms-managed, c02-forms-managed-xml, c12-managed-forms, c12-ordinary-rule, c15-forms-managed-src, c17-ordinary-refused | edit УФ готов; ОФ нет | Form.bin / ordinary DSL |
| C4 справка API | r01 `unica.docs`; r04 core; r10 MCP; r18 ES; r11 корпус | r04/r10/r01 частичное→сильное | c04-*, c10-*, c01-docs | r10/r01 готовее как адаптер; r04 богаче как ядро | проверка на HBK 8.3.27 |
| C5 edit | r01 основной facade; r12 скрипты/skills; r17 только EDT | частичное (УФ+метаданные) | c01-facade, c12-managed-forms | высокая для УФ XML | ordinary forms |
| C6 static | r01 `unica.check`; r09 CheckConfig/EDT (8 tools); r12 validate-скилы | частичное | c01, c09-eight-tools | продуктовая заявка | компактность отчёта |
| C7 build/run | r01 `unica.run`; r09 build/launch; r12 `1c-db-*`; r07 только CI install | частичное | tool-surface; c09-eight-tools; c07-ci-install | высокая заявка | execution |
| C8 runtime/UI test | r09 YaXUnit (серверная логика); r06 REST/данные; r12 Vanessa-скил; r05 видео-DLL | частичное; UI ОФ не закрыт | c09-ordinary-flags; r06/r05 карточки | YaXUnit — лучший целевой контур | UI ordinary forms |
| C9 compact results | r02 stdout+truncation; r01 typed data+limit/cursor; r15 index fragments; r04 JSON statuses | частичное | architecture/tool-surface | заложено в r01/r02 | замер токенов |
| C10 min surface + disclosure | r02 (6 tools); r01 (11 tools + skills); r09 (8 tools); r12 router-скил; r15 широкая | частичное | c02-six-tools, c01-facade, c09-eight-tools | лучше у r01/r02 | 25 tools если склеить r02+r01+r09 без facade |
| C11 знания вне окна | r02 SQLite; r15 SQLite; r04 SQLite; r01 кэш движков; r18 ES; r19 Qdrant | полное у индексных | c02-cli-core; c04; c15 | высокая | — |
| C12 независимость от адаптера | r02 CLI+helpers; r04 resolver crates; r01 ядро vs plugin manifests; r12 скрипты vs skills | частичное | c02-cli-core; c04-resolver; c01-mcp-json | средняя | свой тонкий слой всё же нужен |
| C13 feedback loop | ни один репозиторий не замыкает всё; контур r02→r01/r12→r01.check/r09→r09/r01.run | системное, не закрыто одним | синтез | собираемый | ordinary UI; свой оркестратор |
| C14 без дубля | docs: r04/r10/r18/unica.docs; explore: r02/r15/r19; edit: r01/r12/r13; skills r12≡r13 | решение ниже | карточки | — | не подключать все |

## Альтернативы и сочетания

### Explore

- **Основной:** r02 (facade 6 tools, CF/EDT, sandbox). Связь к агенту: MCP HTTP/stdio. `PROPOSED_INTEGRATION` с собственным router.
- **Альтернатива/core:** r15 (персистентный граф, больше tools). Если нужен callers из индекса — брать бинарь, не сырой `tools/list`.
- **Не основной:** r01 search (нет графа на v0.13), r19 RAG (EPF+Qdrant).

### Docs

- **Ядро:** r04 (HBK→SQLite/JSON, resolver). `PROPOSED_INTEGRATION`: один capability `docs` вызывает CLI/lib.
- **Готовый адаптер:** r10 (5 tools, platform-path, Cursor-пример) или `unica.docs`.
- **Не брать вместе:** r18, r11 как второй индекс.

### Edit

- **Основной facade:** r01 (`unica.apply`/`view`/`check`), если MCP в Cursor заводится.
- **Fallback/Cursor-native:** выбранные скрипты r12 (meta/form/db), не весь каталог. r13 не нужен.
- Связь r01↔r12: `PROPOSED_INTEGRATION`, оба пишут платформенный XML; не звать оба на одну форму.

### Verify / loop

- **Сборка+YaXUnit:** r09. `PROPOSED_INTEGRATION` после edit.
- **Сборка/клиент без тестов:** r01 `unica.run`.
- **CI install only:** r07.
- **Данные в ИБ:** r06 спецслучай.
- **EDT semantics:** r17 спецслучай, конфликт с обязательными обычными формами.

### Предлагаемый минимальный контур

```
агент ← тонкий facade (5 capability)
         ├ explore → r02 (ядро; r15 fallback)
         ├ docs    → unica.docs или r10; индекс r04 если нужна независимость
         ├ edit    → r01; иначе скрипты r12
         ├ static  → unica.check и/или r09 Check*
         └ verify  → r09 build+YaXUnit (+ unica.run при необходимости)
```

Все связи `PROPOSED_INTEGRATION`, не `VERIFIED_INTEGRATION` и не
`OBSERVED_DEPENDENCY` между этими репозиториями (взаимных зависимостей в
коде не найдено).

Собственный слой нужен не чтобы переписать 1С-логику, а чтобы (1) не
показывать 20–30 MCP tools, (2) выбрать один docs и один edit, (3) писать
компактные артефакты на диск.

## Пробелы

1. **Структура обычных форм** (Form.bin / ordinary XML) — ни у r01, ни у
   r02, ни у r12, ни у r15 не доказана. Модули форм находятся.
2. **Целевой UI-тест обычных форм** — нет современного агентского контура
   (r05 устарел; Vanessa в r12 — скил, не движок).
3. **Call graph на поверхности Unica v0.13** — не поддержан.
4. **Официальный хост Unica ≠ Cursor** — подключение вероятно, не проверено.
5. **Сборка r04** может требовать соседний репозиторий.
6. Не подтверждены запуском качество индекса r02/r15 и отчёт r09.
