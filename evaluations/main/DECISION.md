# Выбранный контур агента для разработки 1С

Дата: 2026-09-20. Версия цели: 2.
Статус: **состав контура выбран**. Внедрение рано: стыковка пяти
компонентов с фасадом не исследована.

Это не рейтинг всех кандидатов и не обещание, что продукты прогнали
на вашей базе. Обзор r01–r19 — [REPORT.md](REPORT.md). Answer42 и
Vanessa — r20/r21 в активном [INVENTORY.json](INVENTORY.json):
`NOT_CHECKED` / `PENDING`, карточки-заготовки, материалов не читали.
Снимок обзора при цели v1 (`history/goal-v1/`) не читать по умолчанию.

## Что входит в состав

Пять готовых продуктов плюс **тонкая своя обвязка**. Сами движки 1С
(парсер, индекс, справка, сборка, UI-тесты) не пишем.

| Слой | Продукт | Зачем |
|---|---|---|
| Поиск по конфигурации | [code-index-mcp](https://github.com/Regsorm/code-index-mcp) (`r15`, сборка `bsl-indexer`) | Найти объект, модуль, callers, обработчики, не загружая выгрузку в чат |
| Правки, справка, проверка узла, запуск 1С | [Unica](https://github.com/IngvarConsulting/unica) (`r01`) | Читать/менять XML метаданных и управляемых форм, `unica.docs`, `unica.check`, `unica.run` |
| Сборка и серверные тесты | [mcp-onec-test-runner](https://github.com/alkoleft/mcp-onec-test-runner) (`r09`) | Designer/IBCMD, YaXUnit, синтаксис конфигуратора/EDT |
| Живая форма в цикле разработки | [Answer42](https://gitlab.com/platform42/answer42-mcp) (`r20`, [PyPI](https://pypi.org/project/answer42/)) | Открыть форму, нажать, заполнить, скрин/evidence через Test Client |
| Сценарий и регрессия | [Vanessa Automation](https://github.com/Pr-Mex/vanessa-automation) (`r21`, [MCP](https://pr-mex.github.io/vanessa-automation/dev/AI/)) | `.feature`, цепочки документов, полноценный UI-сценарий |

Обвязка — не шестой 1С-движок. Это маршрутизатор: агент видит **мало
стабильных операций**, а внутри вызывается нужный продукт. Большие
выдачи пишутся в файлы, в чат — короткий итог. Как устроена обвязка:
[FACADE.md](FACADE.md).

## Как это выглядит для агента

Наружу (имена можно сменить, смысл такой):

```
агент
 └ обвязка
      ├ explore         → code-index-mcp / bsl-indexer
      ├ docs            → Unica (unica.docs)
      ├ edit            → Unica (unica.view / unica.apply)
      ├ static          → Unica (unica.check) и/или синтаксис r09
      └ verify
           ├ unit       → r09 + YaXUnit
           ├ form       → Answer42
           └ scenario   → Vanessa
```

Правило разведения проверок:

1. Изменился общий модуль / серверная логика → YaXUnit через r09.
2. «Форма открылась, кнопка нажалась, поле заполнилось» → Answer42.
3. Цепочка документов или регрессия → Vanessa.

Не подключать агенту сырой `tools/list` всех пяти MCP сразу.

Unica **не** основной поиск по большой конфигурации (call graph на
поверхности v0.13 нет). Answer42 **не** основной индекс исходников.

## Что в контур не входит

Эти репозитории **не подключаем**.

| Было в обзоре | Почему не в контуре |
|---|---|
| [rlm-tools-bsl](https://github.com/Dach-Coin/rlm-tools-bsl) (`r02`) | Тот же слой, что r15. Не включать оба |
| [cursor-1c-skills](https://github.com/Desko77/cursor-1c-skills) (`r12`) и [claude-code-skills-1c](https://github.com/Desko77/claude-code-skills-1c) (`r13`) | Дубль правок Unica |
| [mcp-bsl-platform-context](https://github.com/alkoleft/mcp-bsl-platform-context) (`r10`), [1c-syntax-helper-mcp](https://github.com/Antonio1C/1c-syntax-helper-mcp) (`r18`) | Дубль `unica.docs` |
| Остальные из 19 | Дубль, не та роль или спецслучай (EDT, CI, REST в ИБ, RAG) |

Доставать отдельно, только если контур уже упёрся в конкретный пробел:
[v8-context-hbk](https://github.com/alkoleft/v8-context-hbk) (`r04`);
[ai-edt](https://github.com/Desko77/ai-edt) (`r17`) — если появится работа
внутри EDT.

## Что снято с обязательного (цель v2)

- Хост не обязан быть Cursor.
- Обычные формы не обязательны. Контур рассчитан на управляемые формы и
  файловую выгрузку. Структура `Form.bin` не закрывается и не ищется.

## Какие требования закрывает набор (пока на бумаге)

Критерии — [BRIEF.md](BRIEF.md). Закрытие **заявлено составом**, не
подтверждено стыковкой и запуском.

- Связкой: C1 (индекс r15), C2 (граф r15 заявлен), C3 в объёме УФ и
  метаданных, C4 (`unica.docs`), C5–C7 (Unica / r09), часть C8 (YaXUnit),
  C11.
- Только вместе с фасадом: C10, C13.
- Остаток C8 (UI формы и сценария) — r20 Answer42 и r21 Vanessa,
  глубина не достигнута.
- Не закрывают и не блокируют: отладчик вне EDT; структура обычных форм.

## Следующий этап — не внедрение

Проверить интерфейсы и стыковку пяти выбранных компонентов с фасадом
(как звать, путь выгрузки/ИБ, узкая поверхность, две цели, признаки
1С-проекта). План: [VALIDATION.md](VALIDATION.md). Этот документ его
не запускает.

Порядок после успешной стыковки (не сейчас): фасад → r15+Unica на
выгрузке → r09+YaXUnit → Answer42 → Vanessa.

Ссылки на продукты:

- Unica: https://github.com/IngvarConsulting/unica
- code-index-mcp: https://github.com/Regsorm/code-index-mcp
- mcp-onec-test-runner: https://github.com/alkoleft/mcp-onec-test-runner
- Answer42: https://gitlab.com/platform42/answer42-mcp · https://pypi.org/project/answer42/
- Vanessa: https://github.com/Pr-Mex/vanessa-automation · [MCP](https://pr-mex.github.io/vanessa-automation/dev/AI/)

Состояние: [STATE.md](STATE.md).
