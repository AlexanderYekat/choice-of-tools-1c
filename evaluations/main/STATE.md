# Состояние main / 20260920T044856175227Z

Версия цели: **2**. Статус: COMPOSITION_R22_CHOSEN.
Последнее обновление: 2026-09-21.

Состав контура выбран ([DECISION.md](DECISION.md)): Unica, code-index-mcp,
**v8-runner (r22 вместо r09)**, Answer42, Vanessa, тонкий фасад.
План: [INTEGRATION-PLAN.md](INTEGRATION-PLAN.md).
Стыковка: **r20 Answer42, r21 Vanessa и r22 v8-runner достигли
DEEP_STATIC по S1–S5**. r01/r15 — OVERVIEW. Внедрение и execution
не начинались.

## Восстановление без чата

1. Этот файл.
2. [request.json](request.json), [BRIEF.md](BRIEF.md).
3. [DECISION.md](DECISION.md), [FACADE.md](FACADE.md).
4. [INTEGRATION-PLAN.md](INTEGRATION-PLAN.md).
5. [INTEGRATION.md](INTEGRATION.md) — фактический частичный результат.
6. [VALIDATION.md](VALIDATION.md).
7. Для r22 — [reports/r22.md](reports/r22.md); для r20 —
   [reports/r20.md](reports/r20.md); для r21 —
   [reports/r21.md](reports/r21.md); остальные карточки читать по необходимости.

## Прогресс

- r01/r15: OVERVIEW, static стыковка ещё впереди.
- r09: OVERVIEW, **не в контуре** (C14, решение 2026-09-21).
- **r20 Answer42: AVAILABLE / DEEP_STATIC**, commit
  `0406669a88144834bfdf6086c7040a25cb76d24c` (ветка `beta`, v0.5.3).
- **r21 Vanessa: AVAILABLE / DEEP_STATIC**, commit
  `7db5c2bbbf91fd965613a6119121a098bf64cd9e`. Движок `.feature`; запуск
  через r22.
- **r22 v8-runner-rust: AVAILABLE / DEEP_STATIC**, commit
  `7ce1b062843d86644fe55741dbe0ee79f7ca767d` (ветка `master`, v0.5.1).
  **Выбран** как сборка / YaXUnit / синтаксис / запуск Vanessa.

Разрешения: `permissions.* = false`. Все runtime runs r20/r21/r22 NOT_RUN.

## Следующий шаг

CONTINUE-AUDIT по S1–S5 для r01 Unica и r15 code-index-mcp.
После static-стыковки всех выбранных отдельно запросить execution.

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
