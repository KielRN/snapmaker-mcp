# Machine/action reporting implementation plan

> **For agentic workers:** Use superpowers:executing-plans inline under the
> owner's recurring development authorization; obtain a fresh independent review.

**Goal:** Require explicit reported machine/action IDLE before positive idle or
file preparation, without certifying transition or physical completion.

**Architecture:** Add the fixed `machine_state_manager=main_state,action_code`
projection to both existing runtime queries. Normalize only exact integer members
of the artifact's enums, bind both reports under policy 8, and retain unknown
transition/hook execution. No new tool or accepted G-code.

**Tech stack:** Existing Python 3.11+, Pydantic, HTTPX, MCP and pytest.

**Spec:** [Bridge design](../specs/2026-10-24-snapmaker-u1-mcp-design.md),
[pause/end evidence](../../research/2026-10-25-pause-end-evidence.md) and the
owner's read-only continuation instructions.

## Constraints and review focus

- Stay on main, preserve unrelated work, no PR; review/test before commit/push.
- All live requests read-only; one fixed projection can answer availability/type.
- Exact integers only; null/missing/bool/float/string/future enum values unknown.
- Either recognized nonzero report independently blocks idle; both zero required
  alongside prior Klipper/statistics/SD/pause/exception checks. No invented pair
  compatibility table; setters can change action independently.
- No running-code, hook identity, physical quiescence or transition attestation.
- Preserve all file/root/handle/material/feed/thermal/hash/time/expiry/serialization/
  watermark/no-replay checks; policies 1–7 cannot dispatch/promote uncertain work.

## Tasks and ledger

1. [x] Reconcile memory, clean main baseline `3d176bf`, required docs and source.
   No existing Graphify graph; no paid rebuild or concurrent checkout editor.
   Reuse existing artifact/source identities; no downloads or target execution.
2. [x] Add failing normalization/idle/fixed-query/race/policy/actual-MCP tests.
   Implement fields/projection and policy 8; run focused tests to green.
3. [x] Trace provider/transition/SD/control callers; make one bounded passive GET
   for availability/type only; recheck intact corpus and document exact evidence.
4. [x] Independent whole-change review, full Python 3.11/3.13 suites, Ruff,
   wheel/source builds and complete privacy/package/link/ignore audit.
5. Integration: inspect full scope, commit/push main, verify remote ref and save
   precise automation memory. The final commit/ref receipt is recorded there.

Ruling: Execute inline with `.tmp/machine-state-evidence/` for ignored scratch,
following the owner's explicit main/review/commit/push scope. Existing transform
diagnostic gap is carried forward rather than repeating ineffective probes.

## Execution evidence

- Initial regressions: 59 failures (one already conservative busy case passed),
  followed by four actual-MCP failures, before production implementation. Failure
  causes confirmed absent fields/projection, ignored activity/drift and policy-7
  reuse. Focused green run: **169 passed in 33.09s**.
- Reverified all 20 source-manifest entries plus five artifact-only hashes. All
  eight intact export byte/hash checks and first refusals unchanged. One fixed
  passive GET at 05:46:40 UTC confirmed exact integer zero for both reports.
  No new discovery/download/REA/target execution or live mutation/preparation.
- Full suites: **520 passed on Python 3.13.12 (82.00s)** and **Python 3.11.14
  (82.86s)**. Ruff check/format, whitespace and wheel/source builds passed. All
  12 source modules match both archives. Audit: 60 files, 130 links, both archives,
  19 ignore samples; no configured private literals/generated artifacts or broken
  links. Credential-pattern scan found no match across the same 60 files.
- Independent fresh-context review approved: Critical 0, Important 0, Minor 0;
  no fix pass or deferred minor. Reviewer separately passed **520 tests on
  Python 3.13.12 (82.13s)**, verified exact artifact hash/15+43 enum members,
  source/export identities and historical policy-7 receipts with both new fields
  absent. Undispatched rejected; uncertain matching bytes stayed unknown; verified
  and failed terminal results kept original timestamps; no POST replay.
- Final: Ruling: reviewer declined loaded code/hooks, physical quiescence/queue/
  transition/calibration correctness, hardware upload/control/camera/quality,
  stock export safety and snapshot atomicity. Keep each explicitly unestablished
  and milestones incomplete; no readiness or expanded acceptance claim. Treating
  any as proven would exceed the evidence and risk physical operation.
- Final: Ruling: reviewer did not independently execute Python 3.11, Ruff,
  packaging/privacy audits or integration. Parent executed the former gates and
  owns final commit/push/ref checks. These are separate software/integration
  evidence, not independent hardware verification.
- Integration preflight fetched origin/main at baseline `3d176bf`; main and the
  complete 18-file scope contain only this reviewed work. No branch/PR creation.
