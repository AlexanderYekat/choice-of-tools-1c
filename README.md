# AI-инструментарий для разработчика 1С:Предприятие 8

Исследовательский репозиторий: какой минимальный контур из существующих
open-source компонентов собрать для ежедневной разработки в 1С 8
с coding-agent’ом.

Репозиторий начат с шаблона repo-evaluation-kit. Методика осталась в
`.agents/skills/repo-evaluation/`; сами результаты исследования
версионируются здесь.

## Где читать результат

Актуальное исследование: [`evaluations/main/`](evaluations/main/).
Сначала [`evaluations/main/STATE.md`](evaluations/main/STATE.md) — обычное
продолжение не требует каталога `history/goal-v1/`.

- [`evaluations/main/STATE.md`](evaluations/main/STATE.md) — порядок чтения и следующий шаг.
- [`evaluations/main/request.json`](evaluations/main/request.json) / [`request.json`](request.json) — текущий вход (цель v2, 21 URL).
- [`evaluations/main/DECISION.md`](evaluations/main/DECISION.md) — выбранный состав контура (стыковка ещё впереди).
- [`evaluations/main/FACADE.md`](evaluations/main/FACADE.md) — методика обвязки.
- [`evaluations/main/VALIDATION.md`](evaluations/main/VALIDATION.md) — план S1–S5.
- [`evaluations/main/REPORT.md`](evaluations/main/REPORT.md) — синтез относительно текущей цели.
- [`evaluations/main/reports/`](evaluations/main/reports/) — карточки: r01–r19 обзор, r20/r21 заготовки.

По необходимости (происхождение v1, старый критерий, evidence обзора):

- [`evaluations/main/GOAL-CHANGE.md`](evaluations/main/GOAL-CHANGE.md) — смена цели v1 → v2.
- [`evaluations/main/history/goal-v1/`](evaluations/main/history/goal-v1/) — неизменяемый снимок цели v1 (исходные 19).

## Как продолжить исследование

Откройте этот проект в агенте и отправьте:

```text
Прочитай .agents/skills/repo-evaluation/SKILL.md.
CONTINUE-AUDIT: продолжи исследование evaluations/main по STATE.md.
```

Для углубления выбранных кандидатов:

```text
Прочитай .agents/skills/repo-evaluation/SKILL.md.
CONTINUE-AUDIT: каталог evaluations/main.

Проведи глубокое исследование кода (deep-static) этих репозиториев:
- [ссылка или ID репозитория из реестра]

Используй сохранённую цель проекта. Проследи ключевые сценарии по коду,
проверь реализацию важных возможностей, ошибки, заглушки и ограничения.
Обнови карточки выбранных репозиториев, общие выводы и STATE.md.
```

Сборки, установка зависимостей и запуск исследуемых программ требуют
отдельного разрешения. Полные клоны кандидатов в git не входят.

Чтобы пересмотреть цель:

```text
Прочитай .agents/skills/repo-evaluation/SKILL.md.
REASSESS-GOAL: каталог evaluations/main.
Новая цель: [новый желаемый результат]. Сохрани прежние решения в истории.
```

Готовые формулировки: [`prompts/`](prompts/).

## Проверка файлов исследования

Нужны Python 3.10+ и стандартная библиотека. В Windows вместо `python`
можно использовать `py -3`:

```sh
python .agents/skills/repo-evaluation/scripts/kit.py check-run evaluations/main
python .agents/skills/repo-evaluation/scripts/kit.py check-kit .
python -m unittest discover -s tests -v
```

[Методика](.agents/skills/repo-evaluation/references/methodology.md) ·
[Поля JSON и команды скрипта](.agents/skills/repo-evaluation/references/formats.md)
