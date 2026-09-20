# Проверки и следующий эксперимент

Запуски продуктов не выполнялись. Основания: [EVIDENCE.json](EVIDENCE.json).
Версия цели: 2.

## Стыковка (цель v2)

План — [INTEGRATION-PLAN.md](INTEGRATION-PLAN.md), частичный результат —
[INTEGRATION.md](INTEGRATION.md).

Сейчас только **r21 Vanessa достиг DEEP_STATIC**; r01/r15/r09 остаются
OVERVIEW, r20 PENDING.

| ID | Вопрос | r21 Vanessa |
|---|---|---|
| S1 | Чем звать | DOCUMENTATION+SOURCE: batch CLI через 1С; дополнительно Streamable HTTP MCP |
| S2 | Как передать feature/ИБ | DOCUMENTATION+SOURCE: один feature через featurepath, scenariofilter, Test Client definitions/profiles |
| S3 | Узкая surface | SOURCE+INFERENCE: CLI без MCP tools; MCP 37 statically active, скрывать фасадом |
| S4 | Две цели | SOURCE+INFERENCE: несколько definitions/profiles; simultaneous two-target UNKNOWN |
| S5 | Project detection | INFERENCE: explicit WorkspaceRoot/projectpath; generic 1C detection facade-side |

Шкала r21: S1 удобно; S2 удобно; S3 удобно через CLI / терпимо через MCP;
S4 терпимо с неизвестной одновременностью; S5 терпимо.

Execution запрещён текущими permissions и остаётся NOT_RUN.
Следующий static CONTINUE-AUDIT — r01/r15/r09/r20.
