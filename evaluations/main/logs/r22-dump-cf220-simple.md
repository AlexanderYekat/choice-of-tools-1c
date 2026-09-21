# r22 dump Designer 2.20 from IB simple — 2026-09-21

Runner: `v8-runner` 0.5.1, one-off yaml
`.v8/work/simple-cf220/v8project.yaml` (same IB as stand `simple`,
target path **not** `source-checkouts/simple1CAiConf`).
IB: `.v8/ib/simple`. Platform 8.3.27.1936.

| # | Command | Expected | Actual | Pass |
|---|---|---|---|---|
| 1 | `dump --mode full` | XML dump of loaded IB | `ok=true`; 52885 ms; 17 files under `.v8/work/simple-cf-220` | yes |

`Configuration.xml` and `Documents/ЗаказПокупателя.xml` now have
`MetaDataObject … version="2.20"`. Original handwritten dump still has
no version attribute (Unica treated it as format 1.0).

Tree: AccumulationRegisters, Catalogs, Documents, Languages. No
CommonModules, no extensions, no `*.feature`.

Raw JSON: `r22-dump-cf220-simple.json`.
