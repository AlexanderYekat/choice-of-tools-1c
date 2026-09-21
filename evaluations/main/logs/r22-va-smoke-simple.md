# r22 Vanessa smoke on stand simple — 2026-09-21

User correction: empty dump is not a reason to skip the test loop.
Wrote a technical `.feature`, enabled Vanessa on stand `simple`, ran it
against the existing IB.

Feature: `tests/features/smoke-engine.feature`
Step: `И выражение внутреннего языка 'Строка(1 + 1)' имеет значение '2'`
EPF: `.v8/tools/vanessa-automation-single.epf` 1.2.043.1
      (downloaded by v8-harness; not committed).
IB: `.v8/ib/simple`, `--no-build`.

Relative `tools.va.epf_path` resolved against `.v8/stands/simple/`
(nested `.v8`). Paths in stand yaml were made absolute for this run.

| # | Command | Expected | Actual | Pass |
|---|---|---|---|---|
| 1 | `test --no-build va` | 1 scenario passed | `ok=true`; total 1 passed 1; enterprise 0; 122 s | yes |

Log: «Выполнение сценариев закончено. Ошибок не было.»
Warning only: TestClient profile «Этот клиент» not found on close.

Raw JSON: `r22-va-smoke-simple.json`.
