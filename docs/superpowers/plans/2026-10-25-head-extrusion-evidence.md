# Per-head extrusion evidence implementation plan

> **For agentic workers:** Use superpowers:executing-plans inline, then one fresh-context independent review of the complete change.

**Goal:** Bind the supported reported nozzle/pressure-advance/queue subset without claiming physical nozzle, saved K, actual stepper attachment or hidden feed demand.

**Architecture:** Extend `HeadEvidence` and existing runtime normalization/binding. Keep exactly five tools and the existing fixed object queries. Policy 6 invalidates policy-1–5 dispatch and uncertain promotion; no upload is replayed.

**Tech stack:** Existing Python 3.11+, Pydantic/MCP/HTTPX, pytest, Ruff and uv.

**Spec:** [Existing design](../specs/2026-10-24-snapmaker-u1-mcp-design.md), [startup dependencies](../../research/2026-10-25-startup-toolchange.md), and [transform limits](../../research/2026-10-25-transform-evidence.md).

## Global constraints / rulings

- Owner explicitly directs implementation, review, commit and push on main. No branch or PR; preserve unrelated work. All live printer interaction remains read-only.
- Reuse matched source/artifact and the historical seven-object response. No new live query, download, config snapshot or target-code execution is needed.
- Inspected transform status/dump has no decisive chain/effective mesh/provenance read. Keep unknowns; move to an independent contract.
- Reported nozzle sizes use the supported 0.2/0.4/0.6/0.8 mm values and volume types `standard`/`high_flow`. These are software settings, not sensor evidence. Used heads must agree with the file AND operator nozzle attestation.
- Normalize exact finite numeric PA in [0, 1e6] (resource bound, not safety limit), smoothing time in [0, 0.2]. Bind every head, including unused ones.
- Preserve explicit null queue as a known unnamed report; missing/malformed is unknown. Only canonical extruder names map to physical tools. Constructor directly attaches trapq while leaving the name null, so neither null nor a name establishes actual attachment.
- Saved calibrator K, material temperature resolution, retry/motor/purge demand and running-code identity remain unknown. No command/macro/export becomes newly accepted.

## Review focus

- Null queue vs missing field; no false disconnected/attached inference.
- Booleans, strings, NaN/infinity, containers and invalid enums cannot become valid numeric/queue evidence or leak private text.
- Used nozzle mismatch rejects preparation; unused settings still bind without inventing file use.
- Every new field can drift during repeated preparation, destination preflight, remote hashing or restart reconciliation; no dispatch/promotion/replay on drift.
- Historical models deserialize with unknown defaults; policy 5 receipts cannot bypass expanded evidence under policy 6.

## Task 1: Normalize and enforce the bounded contract

Files: `models.py`, `runtime.py`, `uploads.py`; tests in `conftest.py`, a focused `test_head_evidence.py`, and existing receipt/MCP tests.

- [x] Add synthetic five-field head reports. Write failing status normalization/unknown/privacy, nozzle agreement, binding/race, policy-5 and actual MCP regressions; observe failures before production changes.
- [x] Extend `HeadEvidence` with optional defaults for historical receipts: `reported_nozzle_diameter`, `reported_nozzle_volume_type`, `pressure_advance`, `pressure_advance_smooth_time`, `motion_queue_named`, `motion_queue_physical_tool`. Keep actual attachment unestablished in `RuntimeEvidence`.
- [x] Normalize fixed types/ranges/labels through `normalize_runtime`; add fixed missing-field codes. Explicit null queue gives named=false/tool=null; canonical name gives named=true/tool=1–4.
- [x] Require used-head reported nozzle diameter to match file and existing attestation in `Coordinator._evidence`; increment validator identity to 6. Preserve every other safeguard.
- [x] Run focused tests and full suite, then record results.

## Task 2: Evidence, review and integration

- [x] Verify reused source/artifact hashes; document supported passive-read limitation and detailed nozzle/PA/queue and hidden-feed evidence with source anchors. Recheck original export hashes/first refusals without editing bytes.
- [x] Update README/state/roadmap/decisions/changelog/design with exact implemented semantics, unknowns and evidence. Keep all incomplete milestones incomplete.
- [x] Obtain independent fresh-context review; reproduce/fix material findings with meaningful regressions. Run full Python 3.11/3.13 suites, Ruff check/format, wheel/sdist builds and full scope/privacy/package/link/ignore audit.
- [x] Inspect branch/full scope and remote state; only this reviewed project work is selected on main.

Final integration: commit/push the selected scope, verify actual remote ref and
clean tree, and save precise shared automation memory. Git, the ignored push
receipt and that memory supply the resulting commit/push identity without a
self-referential follow-up documentation commit.

## Execution ledger

- Baseline `f884c20a1c7a734b5f92d6547c38ef61eccd5b75`, clean main. Source chat idle; no other active checkout editor. Existing automation remains ACTIVE with its five-hour schedule.
- No existing Graphify graph; no rebuild performed. Required project documents and focused evidence read. Owner already supplied scope and execution authorization; proceed without another approval round.
- Historical response at 13:59:41 UTC contains all five selected fields on all four heads (0.4/standard, PA 0.02, smoothing 0.04, null queue). No fresh hardware evidence is asserted.
- Initial focused regressions: 67 failures/14 passes; a separate pre-implementation run reached and reproduced all 20 field/phase drift failures (`ok` dispatch/promotion where refusal/unknown was required). First focused green: 81 passed.
- Full suites: 403 tests passed on each of Python 3.11.14 and 3.13.12. Ruff check/format and wheel/source builds passed. All 20 release-manifest entries and two artifact-only feed/parameter files verified; all eight export hashes/lengths/first refusals unchanged. No live request.
- Independent fresh-context whole-scope review found no actionable findings or deferred minors. Reviewer independently passed 403 tests on Python 3.13.12, Ruff/check-format, 50 malformed/privacy cases and four canonical queue projections, and verified source/artifact/historical evidence. Loaded live bytes, current/physical state and hardware acceptance were explicitly unestablished, as required by scope.
- Full privacy/artifact/link/ignore audit passed: 54 tracked/new source/doc files, 104 local links, both archives, 14 ignore samples, no configured private literal or generated-runtime matches. Git preflight inspected the entire 16-file change scope; fetched origin/main still matched baseline with no staged/unrelated work.
