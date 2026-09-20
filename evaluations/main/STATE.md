# Состояние main / 20260920T044856175227Z

Версия цели: **2**. Статус: INTEGRATION_PARTIAL_R21.
Последнее обновление: 2026-09-20.

Состав контура выбран ([DECISION.md](DECISION.md)).
План: [INTEGRATION-PLAN.md](INTEGRATION-PLAN.md).
Стыковка начата: **r21 Vanessa достиг DEEP_STATIC по S1–S5**.
Внедрение и execution не начинались.

## Восстановление без чата

1. Этот файл.
2. [request.json](request.json), [BRIEF.md](BRIEF.md).
3. [DECISION.md](DECISION.md), [FACADE.md](FACADE.md).
4. [INTEGRATION-PLAN.md](INTEGRATION-PLAN.md).
5. [INTEGRATION.md](INTEGRATION.md) — фактический частичный результат.
6. [VALIDATION.md](VALIDATION.md).
7. Для r21 — [reports/r21.md](reports/r21.md); остальные карточки читать по необходимости.

## Прогресс

- r01/r15/r09: OVERVIEW, static стыковка ещё впереди.
- r20 Answer42: NOT_CHECKED / PENDING.
- **r21 Vanessa: AVAILABLE / DEEP_STATIC**, commit `7db5c2bbbf91fd965613a6119121a098bf64cd9e`.
- Главное новое наблюдение r21: Vanessa давно имеет batch CLI через
  `1cv8 /Execute ... /C StartFeaturePlayer`; MCP не обязателен для
  обычного `verify.scenario`.
- CLI умеет выбрать один feature-файл и пишет машинный status 0..4.
- MCP остаётся полезным интерактивным backend, но имеет 37 statically
  active tools, поэтому raw surface агенту не показывать.
- simultaneous two-target exchange остаётся UNKNOWN.

Разрешения: `permissions.* = false`. Все runtime runs r21 NOT_RUN.
DECISION/FACADE не менялись.

## Следующий шаг

CONTINUE-AUDIT по S1–S5 для одного или нескольких r01/r15/r09/r20.
После static-стыковки всех пяти отдельно запросить execution.

## Журнал

2026-09-20 → план стыковки подготовлен.
2026-09-20 → по просьбе пользователя выполнен partial CONTINUE-AUDIT r21:
инвентаризация + deep-static S1–S5. Обнаружен существующий batch CLI;
создан INTEGRATION.md. Execution не выполнялся.
