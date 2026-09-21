# r22 YaXUnit / Vanessa on stand simple — 2026-09-21

Stand `simple`, `--no-build` (IB already loaded). No `.feature` in the
dump; no YaXUnit modules/extension in the configuration.

## YaXUnit `test --no-build yaxunit all`

Runner **did** start the thin client:

```
1cv8c ENTERPRISE /C RunUnitTests=<run>/config.json
```

`config.json` asked `closeAfterTests: true`. There is no YaXUnit in this
IB to handle that parameter, so the client sat on the desktop and wrote
no `report.xml`. After ~3 minutes the client was killed; runner returned
`ok=false`, `junit_not_produced`, enterprise exit -1, duration ~295 s.

This is not «tests failed». There were no tests to collect.

## Vanessa `test --no-build va`

Immediate validation error, 1С не запускалась:

`tests.va.profile is not configured` (`invalid_argument`, exit 2).

`v8stands.yaml` has `vanessa: false`; stand yaml has no `tests.va`.
Dump has zero `*.feature` files.

Raw JSON: `r22-yaxunit-simple.json`, `r22-va-simple.json`.
