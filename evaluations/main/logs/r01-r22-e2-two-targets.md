# E2 — two targets in one project, on stand `simple` — 2026-09-22

Goal (INTEGRATION-PLAN.md E2): confirm two independent source-sets/targets
addressable without a second process (Unica), and two independent
targets/processes not cross-contaminating (r22). Both sub-steps **PASS**.

## E2a — Unica: two source-sets in one `v8project.yaml`

Script: `r01-mcp-e2a-multi-sourceset.py`. One `unica.exe` stdio process, one
`v8project.yaml` with two `CONFIGURATION` source-sets (`main` →
`source-checkouts/simple1CAiConf`, `cf220` → `.v8/work/simple-cf-220`),
addressed via `at="<name>:<path>"`.

**Discovery gap, not a product bug:** Unica rejects `source-set.path`
values that are absolute or that escape the workspace root — the error is
`v8project.yaml is present but invalid: project source-map route is not a
closed workspace-relative path`. The two target dumps
(`source-checkouts/...` and `.v8/work/simple-cf-220`) only share the repo
root as a common ancestor, so the config had to live at the repo root with
relative paths. Since a stray root-level `v8project.yaml` risks being
picked up by unrelated future work (e.g. `v8-runner` invoked from repo
root without `--config`), it was created only for this run and deleted
immediately after (`git status` confirms it is not present in the working
tree).

Result: **8/8 PASS** (`run-r01-e2a-multi-sourceset-simple`).
- `unica.view {}` from the single process lists both `main` and `cf220`.
- `at="main:Document.ЗаказПокупателя"` and `at="cf220:Document.ЗаказПокупателя"`
  both resolve (`ok=true`), to visibly distinct payloads (different dumps).
- `at="bogus:Document.ЗаказПокупателя"` — named refusal
  (`"view source set was not admitted by the workspace actor"`,
  `diagnostics[0].code = "provider_unavailable"`), not a silent default to
  `main`.
- sha256 fingerprint of both dump trees unchanged before/after.

## E2b — r22: two IBs, two processes

Two separate `v8-runner` CLI invocations (no shared daemon — CLI is
one-shot), each with its own `--config`:
- A: `.v8/stands/simple/v8project.yaml` → `.v8/ib/simple`.
- B: `.v8/work/r22-e2b/v8project.yaml` (new, minimal) → the existing copy
  `.v8/work/r20-dual/ib-b` (created during the r20 dual-live test, not a
  new IB).

Operation: `syntax designer-modules --server --thin-client` on each,
sequentially. sha256 of each `1Cv8.1CD` captured before/after every step.

Result: **PASS**.
- A's `1Cv8.1CD` hash changed after operating on A (`471c7b… → f8e869…`) —
  expected; the platform touches session/lock metadata in the file even
  for a syntax check. B's hash was untouched by A's operation
  (`44884b…` unchanged).
- B's hash changed after operating on B (`44884b… → f1c441…`); A's hash
  was untouched by B's operation (`f8e869…` unchanged, confirmed after).
- Both `syntax` runs: `status=clean`, `errors=0`.
- `--config .v8/work/r22-e2b/does-not-exist.yaml syntax …` →
  `ok=false`, `error.code=invalid_argument`,
  `message="config file not found: …"` — explicit refusal, no silent
  fallback to a default project.

Raw JSON: `r22-e2b-syntax-A-simple.json`, `r22-e2b-syntax-B-ibb.json`.

## r21 (Vanessa) simultaneous — still UNKNOWN, by design

Per plan: not tested this round. The facade's `target -> profile/connection`
contract stays single-threaded for Vanessa; recorded as a stated
limitation, not an unnoticed gap.
