# Reported job flags implementation plan

> **For agentic workers:** Use superpowers:executing-plans inline under the
> owner's ongoing authorization, then obtain one fresh independent review.

**Goal:** Bind the supported job preference reports to file receipts without
claiming execution, completion, effective calibration or camera ownership.

**Architecture:** Extend existing status/runtime reads with a fixed projection
of `print_task_config`. Normalize eight exact booleans, two four-boolean physical
tool arrays and one fixed sensitivity enum. Reuse repeated runtime binding under
policy 9. No new tool, G-code acceptance or live mutation.

**Tech stack:** Existing Python 3.11+, Pydantic, HTTPX, MCP and pytest.

**Spec:** [Bridge design](../specs/2026-10-24-snapmaker-u1-mcp-design.md),
[pause/end evidence](../../research/2026-10-25-pause-end-evidence.md) and
[machine/action evidence](../../research/2026-10-26-machine-state-evidence.md).

## Constraints and rulings

- Stay on main; preserve unrelated changes. Review, verify, commit and push;
  no branch or PR, no hardware mutation or upload enablement.
- Carry forward the unsupported transform/provenance diagnostic gap. Do not
  repeat discovery, source identity verification or ineffective live snapshots.
- Flags report preferences, not success/completion. True and false are both
  valid reports, neither authorizes macro/control/camera execution.
- Arrays are exact four-element boolean lists in physical T0–T3 order; never
  coerce numbers/strings or infer logical mapping. Unknowns block preparation.
- Fixed projection retains the three material fields consumed by existing
  materials normalization; omit arbitrary configuration and nested reprint data.
- Preserve idle semantics and all prior guards. Policies 1–8 cannot dispatch or
  promote uncertain work; historical terminal results keep their original time.
- Getter refreshes in-memory existence/edit flags; it is not a mutation-free
  snapshot or action-completion diagnostic. No live request is needed here.

Ruling: Execute the bounded contract supplied by the owner's continuation and
prior handoff without another approval round. Use ignored `.tmp/job-flag-evidence/`
for logs/review/audit. The existing checkout is explicitly authorized on main.

## Tasks and execution ledger

1. [x] Reconcile memory, clean main at `f210a3b`, required docs and existing
   source/artifact. No existing graph or concurrent checkout editor identified.
2. [x] Add failing normalization/privacy/projection/race/policy and actual MCP
   tests. Implement only established reports; run focused tests to green.
3. [x] Document getter/reset/reprint and startup/feed/end/camera consumers with
   precise source anchors and explicit remaining gaps. Update source-of-truth docs.
4. [x] Independent review, both full Python suites, Ruff, wheel/source builds,
   package/privacy/link/ignore audit and untouched export refusals.
5. Integration: inspect full scope, commit/push main, verify remote ref and save
   handoff. The resulting commit/ref receipt is recorded in automation memory.

## Execution evidence

- Initial targeted run: **196 failed, 26 passed (40.51s)** before production
  changes. Failures established absent job reports/projection/binding/policy-8
  refusal; existing MCP cases also caught the new required output assertion.
- Focused green run: **222 passed (54.61s)**, including each field's change and
  absence through preparation/preflight/hash/restart plus actual MCP and old
  policy refusal. No printer request or upload enablement.
- Full suites: **700 passed on Python 3.13.12 (94.63s)** and **Python 3.11.14
  (94.90s)**. Ruff check/format, whitespace and wheel/source builds passed. All
  12 source modules match both archives. Audit: 63 files, 142 local links, both
  archives and 23 ignore samples; zero configured private-literal/generated
  artifact/credential-pattern matches or broken links. All eight original export
  bytes/hashes and first refusals unchanged. Local/default uploads stay disabled.
- Automation timing: observed next reset 2026-10-26 16:01:04 UTC; updated the
  same active automation to 16:21:04 UTC, every five hours. Saved readback changed
  only schedule/update time; full prompt, project, model/reasoning/environment,
  target/cwds/status and creation fields preserved. No duplicate or reset credit.
- Fresh independent review: Critical 0, Important 0, Minor 0; no fix pass or
  deferred minor. Reviewer independently passed **700 tests on Python 3.13.12
  (94.20s)** and **176 probes**: 139 malformed/missing, five valid/schema/list-copy/
  idle and 32 true historical-schema receipt cases. Policies 1–8 refused
  dispatch/promotion without POST replay; terminal timestamps/results preserved.
  Saved anchors/new consumer hashes agree. Review is ignored with other logs.
- Review boundary: installed/loaded field behavior, macro/physical/calibration
  completion, camera ownership/cleanup/freshness, transform/provenance/saved K/
  hidden demand and hardware/stock-export acceptance remain unestablished.
  Parent separately owns second-Python, Ruff/build/scope/package/privacy/export
  and scheduling/integration checks; those are not reviewer-run evidence.
- Integration preflight fetched origin/main and found the same baseline
  `f210a3b`. Main and all 18 changed/new files contain only this reviewed work;
  no existing staged or unrelated changes. Final docs rebuilt and audited.
