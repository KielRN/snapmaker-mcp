# Bounded coordinate runtime evidence

Execute inline on main under the owner's explicit continuation, implementation,
independent review and commit/push request. No further approval gate or branch
change is needed. All live interactions are read-only.

**Goal:** Collect and bind the reported coordinate/selection/active-mesh subset
whose fields can be established on the observed firmware. Keep complete stock
profiles blocked and distinguish reported values from calibration or live-code
attestation.

**Sources:** [Startup/toolchange report](../../research/2026-10-25-startup-toolchange.md),
[design](../specs/2026-10-24-snapmaker-u1-mcp-design.md), receipt/upload contracts.
Reuse the existing ignored matched artifact/source, mapping and configuration.

## Interfaces and scope

- `runtime.normalize_runtime(snapshot: dict) -> RuntimeEvidence` projects only
  bounded numeric vectors, booleans, fixed enums and digests of active mesh data.
  Unknown/malformed fields stay null with fixed missing-field codes. No raw mesh
  profile labels, saved profiles, config, printer names or arbitrary extra fields.
- `Status.runtime_evidence` carries that subset in the existing status query;
  no sixth tool. Offsets are reported values (firmware can emit zero fallback),
  homing origin is global, and selection is separate from park/grip reports.
- `Coordinator._evidence` returns the private binding digest and `RuntimeBinding`.
  Bracket materials/job reads with two matching normalized coordinate snapshots
  and nondecreasing event times. Bind the entire normalized subset, policy and
  existing evidence. Missing fields/inconsistent indices refuse preparation;
  changed observations refuse dispatch/promotion. HTTP is never atomic.
- Policy 4 refuses policies 1–3 for undispatched and uncertain operations, with
  no replay. Historical terminal results retain existing semantics. Unexposed
  base positions, mesh fade/tool offset, transform chain and running code remain
  explicitly unestablished; none is invented from configuration or matrices.

## Review focus

1. Firmware zero-offset fallback must not become calibration proof.
2. All parked must not become a physically selected/gripped head from toolhead.
3. Transformed machine/G-code positions may differ; do not require equality.
4. Nonfinite/bool/coerced/ragged/oversized fields must remain unknown and private
   profile labels/extra fields must not leak through results or errors.
5. Snapshot races, stale/backwards event times, missing new evidence and old
   policy receipts must prevent dispatch/promotion without replay.

## Tasks and verification ledger

1. [x] Read required sources/contracts; verify clean baseline main `58ca1e0`.
   No existing Graphify graph; no rebuild. One bounded GET for seven objects
   completed, raw reply ignored. Trace source field semantics and record limits.
2. [x] Add failing normalization/read tests with synthetic fixtures; implement
   `runtime.py`, typed models and fixed transport/status object collection.
3. [x] Add failing preparation/upload tests, policy-3 restart and actual MCP
   transport cases. Implement receipt evidence window and policy 4. Retain all
   path/material/feed/thermal/hash/expiry/serialization/no-replay safeguards.
4. [x] Recheck unchanged eight-export hashes/rejections. Update focused research,
   design, README, state, roadmap, decisions and changelog with actual scope.
5. [x] Independent fresh-context review; fix material findings with regressions.
   Run full Python 3.11/3.13 suites, Ruff check/format, wheel/source builds; audit
   tracked scope, document links, private values, archives and ignore coverage.
6. Integration: inspect branch/full working tree and fetched remote base; commit and push
   main as requested. Record Git receipt and smallest remaining evidence step.

No new dependencies, macros, slicer work, camera sessions, printer mutations or
hardware acceptance belong in this plan.

## Execution evidence

- Initial normalization tests: 23 failures demonstrated absent projection and
  missing-field handling before implementation; then 50 read/normalization tests
  passed. Sixteen receipt/policy regressions reproduced missing binding before
  fixes. Further failing tests established backwards time across operations,
  material timestamps outside the window, drift during remote hash reads and
  persisted reconciliation watermark behavior.
- All 20 source manifest identities and three additional artifact-only identities
  reverified without new discovery. The single live reply normalized offline with
  no missing fields or identified inconsistencies in the established subset.
- All eight original export hashes/rejections rechecked unchanged. No new command
  acceptance or stock-profile compatibility is inferred from the evidence.
- Independent fresh-context review ran the complete pre-fix suite (295 passed)
  and Ruff checks. It found two P2 contradictions: status-1 aggregate selection
  differing from toolhead, and an empty mesh sentinel with nonzero extrema.
  Four normalization/preparation regressions reproduced both before correction.
  Both now refuse; 47 normalization/binding tests pass. No other actionable or
  declined-to-judge findings were reported. A misplaced pair of test assertions
  caused a test-only NameError during the fix pass; corrected and rerun.
- Final complete suites: 300/300 on Python 3.11.14 and 3.13.12. Ruff check/format
  and wheel/source builds passed after fixes. Audit: 49 source/doc files, 76 local
  links, both archives and nine ignore samples; no configured private value or
  generated runtime artifact in tracked/package scope. No deferred findings.
- Integration preflight: branch remains main; fetched origin/main still equals
  baseline `58ca1e0b4f722abe69c41a50dd4f9044a01004db`. Complete scope inspected;
  no unrelated work present. The resulting commit and remote ref are the final
  integration receipt. No PR or branch change.
