# r22 E1 — YaXUnit engine + hand-authored test extension on stand `simple` — 2026-09-22

Goal (INTEGRATION-PLAN.md E1): install YaXUnit engine and a small test extension
(pass + fail test) into `.v8/ib/simple`, get a JUnit report with both outcomes.
**Not reached.** Test discovery finds 0 scenarios; root cause narrowed but not
fixed.

## What was built

- `e1tests` extension: hand-authored Designer-format XML (no EDT/1cedtcli
  available in this environment — verified missing via `where 1cedtcli`).
  One CommonModule `ТестыE1` with `ИсполняемыеСценарии` registering a passing
  and a failing test (`2+2=4`, `2+2=5`), matching the official "first test"
  doc example verbatim. Loaded via `v8-runner build --source-set e1tests`.
- `YAXUNIT` extension: `v8-runner tools download yaxunit` (no `--sources`,
  since `--sources` yields EDT-layout source unusable in a `format: DESIGNER`
  project) → `YAxUnit-25.12.cfe`. `v8-runner load --extension` requires the
  target extension to already exist, so an empty placeholder shell was built
  first (hand-authored Configuration.xml + Languages/Русский.xml), then the
  real `.cfe` was applied with `load --mode merge --settings <file>`.

## Bugs/gaps found and worked around (local only, not published)

- `v8-runner load --mode merge` builds the `/MergeCfg` artifact path from a
  Windows verbatim (`\\?\`) canonicalized path; the platform then fails with
  `Файл не обнаружен 'file://\\?\C:\...'`. Patched locally
  (`src/platform/designer.rs`, `strip_verbatim_prefix`) in the pinned
  `v8-runner` checkout at `C:\Users\Enduro\Documents\1c\Tools\v8-runner` and
  rebuilt — not applied upstream, not committed to this repo.
- `/MergeCfg -Settings` requires a settings file whose root element carries a
  `version` attribute matching an *older* schema (`1.0` worked; `2.20`, the
  Designer dump format version, was rejected as "not supported by this
  platform version" — the opposite of what the message suggests).
- A hand-authored extension `Configuration.xml` must set
  `<ObjectBelonging>Adopted</ObjectBelonging>` and a root `version=` attribute
  on `<MetaDataObject>`, and must **omit** `InterfaceCompatibilityMode`
  (any explicit value here fails `update_db_cfg` with a "controlled property
  mismatch" against the base configuration's implicit value).
- `v8-runner extensions` (disables SafeMode via `ibcmd`) and `v8-runner dump
  --extension`/`load --extension` all resolve their `--name`/`--extension`
  argument against the **v8project.yaml source-set name**, not the real
  platform extension `Name` property. The real YaXUnit `.cfe` declares
  `Name=YAXUNIT` (not `yaxunit-shell`, the source-set name originally used);
  the source-set had to be renamed to `YAXUNIT` to make these commands work.
- A freshly built/merged extension defaults to `SafeMode=yes`; YaXUnit's own
  run-config read fails inside SafeMode
  (`Расширение подключено в безопасном режиме. Чтение конфигурационного
  файла недоступно`). Disabled via `ibcmd infobase config extension update
  --safe-mode no --unsafe-action-protection no` for both extensions.

## The unresolved finding: cross-extension test discovery

With both extensions active, SafeMode off, and `e1tests`'s module properties
adjusted to match YaXUnit's own reference test module (`ОМ_ЮТКоллекции` from
`bia-technologies/yaxunit`'s self-test extension) property-for-property
(`ClientOrdinaryApplication=true` was the one mismatch, fixed), `test yaxunit
all` / `test yaxunit module ТестыE1` both report `0 сценариев`.

Debug-level logging (patched locally: `run_tests.rs` YaXUnit config
`logging.level` hardcoded `"info"` → `"debug"`) shows `ТестыE1` **is**
discovered as an extension-owned candidate module (`Анализ модуля: ТестыE1`),
but rejected as "not a test module".

Instrumented the local copy of YaXUnit's own
`ЮТМетодыСлужебный.МетодМодуляСуществует` (the function that probes
`Выполнить("ИмяМодуля.ИмяМетода(,,,...90 commas...)")` and classifies the
platform error) to dump the raw exception per probed module/method to
`.v8/work/e1-debug/diag_*.txt`. Result for `ТестыE1.ИсполняемыеСценарии`:

```
Описание=Метод объекта не обнаружен (ИсполняемыеСценарии)
```

Added a second, trivial, unrelated export method `Пинг()` to `ТестыE1` purely
to isolate whether this was about `ИсполняемыеСценарии` specifically. Probed
it from the exact same call site/context/timing:

```
Пинг: Описание=Метод объекта не обнаружен (Пинг)
```

**Conclusion: the entire `ТестыE1` module is unresolvable by bare name from
dynamic (`Выполнить`) client-side code running inside a sibling extension
(`YAXUNIT`)'s own module — for any method, not a discovery-signature issue.**
This rules out module property mismatches and `ИсполняемыеСценарии`'s
signature as the cause.

**Not yet established:** whether this is specific to a hand-authored
(non-Designer/non-EDT) extension scaffold — i.e. Designer/EDT-created
extensions might set up some extension-to-extension visibility this raw XML
scaffold is missing — or a general platform/YaXUnit limitation for any two
independently-loaded sibling extensions. Load-order/priority and
extension-dependency-declaration hypotheses were not tested before recording
this. This is an open risk for the facade's `verify.unit` capability if real
users' test extensions hit the same wall; it is *not* known to be a dead end,
only unresolved.

## Round 2 (same day): ruled out order, naming, filter, dynamic-vs-static

Per follow-up user direction, tested — and ruled out — every remaining
config-level hypothesis before escalating further:

- **Extension load order/priority**: per `its.1c.ru` and practitioner
  articles, `_ExtensionOrder`/priority governs only `&Перед`/`&После`/
  `&Вместо` interceptor sequencing for the *same* procedure across multiple
  extensions modifying it — it does not govern name resolution of a sibling
  extension's native objects. Not the mechanism here.
- **`"filter": {"extensions": [...]}`** in YaXUnit's own config.json (found
  in `bia-technologies/yaxunit` issue #526): added support for it to the
  local v8-runner patch (`YaXUnitFilter.extensions`), confirmed via the
  written `config.json` and via debug logs that non-matching modules were
  now skipped with "не подходит под отбор" *before* reaching the
  discovery check — but `ТестыE1` itself still failed with the identical
  "Метод объекта не обнаружен". Reverted this hardcoded filter afterward
  (it would otherwise silently change `test yaxunit all` behavior for all
  future runs, not just this diagnostic).
- **Alphabetical/name-based extension application order**: renamed the test
  extension `e1tests` → `AE1TESTS` (sorts before `YAXUNIT` in ASCII) on the
  theory that "extensions apply sequentially by name" (per a practitioner
  search summary). Renaming via `LoadConfigFromFiles -Extension AE1TESTS`
  did **not** rename in place — it created a new extension and left the old
  `e1tests` orphaned (deleted manually via `ibcmd ... config extension
  delete --name e1tests`). Result unchanged.
- **Compile-time-frozen visibility**: rebuilt `YAXUNIT` again *after*
  `AE1TESTS` already existed (in case cross-extension linkage is fixed at
  the point an extension was last compiled). Hash-sum changed, confirming a
  real rebuild; result unchanged.
- **Dynamic (`Выполнить`) vs static resolution — the one substantive new
  data point**: added a literal, non-dynamic, source-level statement
  `ТестыE1.Пинг();` inside `YAXUNIT`'s own instrumented module. It
  **compiled without error**, but **failed at runtime with the identical
  `Метод объекта не обнаружен (Пинг)`**. This means the failure is not
  specific to `Выполнить()`/dynamic compilation — ordinary static calls to
  a sibling extension's native module fail identically at runtime in this
  setup. It also means `LoadConfigFromFiles` accepting the reference at
  build time is **not** reliable evidence of resolvability — a follow-up
  probe using a deliberately nonexistent identifier
  (`e1tests_ТестыE1.Пинг()`, an NamePrefix-qualified guess) also "compiled"
  but then failed to even reach the diagnostic write on invocation,
  confirming `LoadConfigFromFiles` does not meaningfully validate
  cross-references at load time.

**Net result: root cause still not isolated.** Every mechanism this session
could test from the CLI/XML side (order, naming, filter config, dynamic vs.
static, rebuild timing) has been ruled out. What's left untested: whether a
test extension authored through real 1C:Designer or 1C:EDT (rather than
hand-written XML) avoids this entirely — which would require tooling not
available in this environment — or whether this needs an official 1C
support channel. By user direction, parked as an open risk; work moved on
to E2.

## Cleanup still owed

Local instrumentation (diagnostic file writes and the `ТестыE1.Пинг()`
static probe in `ЮТМетодыСлужебный.Ext/Module.bsl`) is still present in the
`YAXUNIT` extension inside `.v8/ib/simple` as of this writing. The local
`v8-runner` patch's diagnostic-only changes (hardcoded `filter.extensions`,
`logging.level: debug`) were reverted and rebuilt; the genuine bug fix
(`strip_verbatim_prefix` for `/MergeCfg`) was kept. The IB-side
instrumentation itself was **not** reverted — rebuilding `YAXUNIT` from the
clean `YAxUnit-25.12.cfe` artifact (discarding
`.v8/stands/simple/yaxunit-shell` edits) is still owed before this stand's
YaXUnit state is considered clean, and before any future attempt to make
`test yaxunit` PASS on it.

Raw JSON: `r22-e1tests-build-attempt{1..6}.json`,
`r22-yaxunit-download-cfe-simple.json`, `r22-yaxunit-merge-cfe-simple.json`,
`r22-yaxunit-debug-simple.json`, `r22-yaxunit-debug2-simple.json`,
`r22-yaxunit-ping-run.json`, `r22-extensions-safemode-simple.json`.
