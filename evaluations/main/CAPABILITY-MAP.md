# Возможности относительно цели

Версия критериев: 2; источник — [BRIEF.md](BRIEF.md).
Матрица при цели v1 — в снимке `history/goal-v1/CAPABILITY-MAP.md`
(читать только если нужен старый критерий).
Основания обзора — [EVIDENCE.json](EVIDENCE.json), кандидаты —
[INVENTORY.json](INVENTORY.json).
Глубина: r02–r14, r16–r19 overview; **r01, r15, r20, r21 и r22 DEEP_STATIC по S1–S5**.
Покрытие — по прочитанному объёму. Static стыковка пяти закрыта.
Слот сборки: **r22 выбран** (2026-09-21); r09 не в контуре.

Обозначения покрытия: **полное** (в роли кандидата), **частичное**,
**не установлено**, **неприменимо**.

## Матрица

| C* | Кто закрывает | Покрытие | Доказательство | Готовность | Недостаёт |
|---|---|---|---|---|---|
| C1 explore без дампа | **r15 выбран** (13 1С-tools + core); r02 сильный, но не в контуре; r01 частично (`search`/`view`); r19 RAG | r15 частичное→сильное как заявка | c15-bsl-thirteen; c15-entry; c15-cli-core; c15-index-simple; c15-search-callers-simple; c15-mcp-simple; c15-mcp-whitelist | r15 продуктовый; CLI, MCP и whitelist RUN на sample | точность на большой выгрузке |
| C2 связи BSL | r15 (индекс callers + 1С-tools); r02 хелперы не трассированы; r01 call graph на v0.13 нет | частичное | c15-bsl-thirteen; c15-entry; c15-search-callers-simple; c15-mcp-simple; c01-search-limits | CLI callers + MCP handlers/writers RUN на sample | подписки: dump пуст; большая конф. |
| C3 метаданные и УФ | метаданные: r01, r15, r02, r12; УФ: r01 edit, r15 read. Обычные формы в v2 не обязательны; пробел Form.bin не блокер | частичное (достаточно для v2) | c01-forms-managed, c01-view-simple, c15-forms-managed-src, c15-autodetect, c02-forms-managed-xml | edit УФ заявлен; r01 view RUN; apply publish RUN | ОФ не ищем |
| C4 справка API | r01 `unica.docs` выбран; r04 core; r10/r18 не в контуре | частичное→сильное у r01/r04 | c01-docs-simple, c04-*, c10-* | r01 docs RUN на 8.3.27.1936 | полный текст страницы; admin-guide unavailable |
| C5 edit | r01 основной; r12 дубль, не в контуре; r17 только EDT | частичное (УФ+метаданные) | c01-facade, c01-apply-fence, c01-apply-dryrun-simple, c01-apply-cf220-simple, c01-apply-publish-cf220-simple, c12-managed-forms | dryRun preview + публикация ifRev RUN на Designer 2.20; рукописный дамп `invalid_source` | загрузка опубликованного дампа в ИБ; ОФ не требуется |
| C6 static | r01 `unica.check`; **r22 syntax designer/edt** (r09 не в контуре) | частичное | c01, c01-check-format-simple, c22-eight-tools; c22-ib-simple | продуктовая; r22 modules RUN clean; Unica.check ответил на фикстуре `source_unreadable` | check на выгрузке 2.20, которую Unica принимает |
| C7 build/run | r01 `unica.run`; **r22 CLI `build`/`launch` + `--json-message`** | частичное→сильное у r22 | c22-entry; c22-json-envelope; c22-ib-simple; c01-entry | r22 init/build RUN; r01 static | launch/apply; dual-IB |
| C8 runtime/UI test | **r22 YaXUnit CLI + `test va`**; **r20 Answer42**; **r21 Vanessa (движок)** | частичное | c22-entry; c22-yaxunit-empty-simple; c22-va-unconfigured-simple; c22-va-smoke-simple; c20-entry; c20-mcp-simple; c21-cli-target | Vanessa engine smoke RUN 1/1; Answer42 smoke RUN; YaXUnit на simple без расширения | фикстура с модулями YaXUnit; dual live r20 |
| C9 compact results | r01 typed data; r15 fragments; **r22 Envelope + retained_paths**; r02 truncation (не в контуре) | частичное | architecture/tool-surface; c22-json-envelope | заложено | замер токенов; фасад |
| C10 min surface | фасад обязателен; **r01 живой `tools/list` = 11, прячутся**; **r15 без секции list = 33, с `[tools].enabled` list = 9**; **r22 CLI без tools/list**; **r20 живой `ui` = 103 (static `full` 122), режется `--tool-profile`**; r21 MCP 37, **но scenario идёт через r22 CLI** | частичное | c01-facade, c01-mcp-simple, c01-adapter-choice, c15-mcp-whitelist, c15-adapter-choice, c15-mcp-simple, c22-eight-tools, c22-adapter-choice, c20-tool-surface, c20-tool-profile, c20-mcp-simple, c21-tool-surface, c21-adapter-choice | r01/r15/r20/r21/r22 можно спрятать за facade без патча; whitelist r15 RUN | execution фасада |
| C11 знания вне окна | r15 SQLite; r01 кэш; r04 | полное у индексных | c15; c01; c04 | высокая | — |
| C12 независимость от адаптера | r01 ядро vs plugin; r15 бинарь; r22 CLI; Cursor не критерий | частичное | c01-mcp-json; c22-entry | средняя | свой фасад |
| C13 feedback loop | контур r15→r01→r01.check/r22→r22/r20/r21 | системное, не закрыто одним | синтез v2; c22-adapter-choice; c01-adapter-choice; c15-adapter-choice | собираемый на бумаге | execution |
| C14 без дубля | explore r15 не вместе с r02; edit r01 не вместе с r12/r13; docs unica.docs не вместе с r10/r18; **r09 не вместе с r22** | решение в DECISION + c22-vs-r09 | карточки | — | не возвращать r09 |

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

- **Сборка+YaXUnit: выбран r22** (2026-09-21). r09 METR не в контуре.
- **Клиент без тестов:** r01 `unica.run`; r22 `launch`.
- **UI формы:** r20 Answer42 — stdio MCP, `--tool-profile ui --disable-rag`,
  `session_id`; smoke на simple PASS (`tools/list` = 103).
- **Сценарий:** движок r21 Vanessa; запуск через r22 `test va` (не сырой
  `1cv8 /Execute` фасада). MCP Vanessa — интерактивная отладка.
- **Спецслучаи:** r06, r07, r17 (EDT не основа контура).

### Предлагаемый минимальный контур (цель v2)

```
агент ← тонкий facade
         ├ explore → r15
         ├ docs    → unica.docs
         ├ edit    → r01
         ├ static  → unica.check и/или r22 syntax
         └ verify  → r22 YaXUnit; form → r20; scenario → r21 через r22
```

Все связи `PROPOSED_INTEGRATION`. Фасад не запускался
(`VERIFIED_INTEGRATION` нет). Dump-only: r15 CLI+MCP, r22 IB, r01
`view`/`check`/`apply` dryRun/`docs`/публикация ifRev. **r20 Answer42 smoke RUN**.
r01/r15/r20/r21/r22 прочитаны в объёме S1–S5.

## Пробелы

1. Execution пяти: индекс r15, Unica view/docs/apply dryRun и публикация
   ifRev на Designer 2.20, Vanessa engine и Answer42 smoke есть.
   YaXUnit на simple без расширения, не баг runner.
2. Call graph на поверхности Unica v0.13 — не поддержан (explore закрывает r15).
3. Структура обычных форм — по-прежнему отсутствует, **не блокер** цели v2.
4. Признаки автоопределения 1С-проекта фасадом: ориентиры есть у r01/r15/r22;
   единый закрытый список всё ещё не утверждён запуском.

