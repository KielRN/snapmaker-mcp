# Pause/end evidence implementation plan

> Execute inline using superpowers:executing-plans, with one independent fresh-context review before commit/push.

**Goal:** Distinguish the supported saved-pause report from print statistics and prevent positive idle/preparation without explicit unpaused evidence.

**Architecture:** Extend the existing fixed status/runtime queries with only `pause_resume.is_paused`. Normalize exact booleans, bind the report through existing repeated observations, and advance receipt policy to 7. Keep callback bodies, saved restore state and physical completion unknown.

**Tech stack:** Existing Python 3.11+, Pydantic, HTTPX, official MCP SDK, pytest and Ruff; no new dependencies.

**Spec:** [Bridge design](../specs/2026-10-24-snapmaker-u1-mcp-design.md), [prior head contract](../../research/2026-10-25-head-extrusion-evidence.md), and the owner's recurring read-only development authorization.

## Constraints and review focus

- Stay on main; baseline `20ef873b14c9e4891ad5ca3a1d128f550ff7ca52` was clean, and other bridge chats were idle. No Graphify graph exists; no rebuild.
- No live mutations, upload enablement, new tool, command acceptance, branch or PR. Preserve every existing guard and no-replay rule.
- Missing, explicit null and malformed pause reports are unknown, never false. Printing/paused/active SD remain busy even if the pause report is unknown/false.
- True saved pause blocks idle independently of print-state labels. False is necessary, insufficient evidence of physical idle or safe resume.
- Opening/closing reads must use the same projection. Races during preparation, destination preflight, hashing and restart reconciliation cannot dispatch/promote.
- Policies 1–6 cannot dispatch/promote uncertain uploads; historical models may deserialize with unknown pause state.
- Trace configurable layer callbacks, error/idle scripts and job flags accurately; comments/defaults are not executed callbacks, and flags are not evidence of completed actions.

## Tasks

- [x] Verify existing source/artifact identities; trace pause/end and enumerate supported reads versus unavailable state. At most one focused passive GET if no historical report answers availability/type.
- [x] Write/run failing normalization, idle/preparation, fixed-query, phase-race, old-policy and actual-MCP regressions.
- [x] Add optional historical model field in models.py; exact normalization in runtime.py; fixed projection in transport.py; conservative idle in adapter.py; policy 7 in uploads.py. Update synthetic fixtures and policy tests.
- [x] Run focused tests; write research and update design/README/state/roadmap/decisions/changelog.
- [x] Obtain independent review; fix material findings with regressions. Run full Python 3.11/3.13 tests, Ruff and wheel/sdist builds; audit full scope, links, private literals, artifacts and ignore coverage; recheck eight intact exports.
- Integration: inspect branch/full scope and remote main; commit/push reviewed project changes. The resulting Git commit and independently checked remote ref are the integration receipt, saved with the timestamped automation-memory handoff. Automation timing was adjusted to the observed reset with other settings preserved.

## Execution ledger

Ruling: Keep this a bounded status/receipt hardening change. Job flags and callback execution are researched but do not become acceptance semantics; their motion/thermal/ownership dependencies remain unresolved.

Ruling: Existing owner authorization covers implementation, independent review, commit and push on main; no additional approval gate is needed. Hardware authorization remains read-only.

- All 20 release-manifest SHA256/Git blobs and matching inspected artifact files reverified; five additional artifact-only providers verified against the existing extraction manifest. Eight intact export bytes/hashes and first refusals unchanged. No new discovery/download/REA or target-code execution.
- Exactly one fixed GET, 20:44:17.804708–20:44:18.029262 UTC, confirmed boolean false. No other live request or preparation/mutation. Raw report ignored. Local upload enablement remains false.
- After correcting a test import typo, the pre-implementation regression run showed **32 failures / 16 passes**, including all four coordinator phase races and both policy-6 reuse cases. Focused green: 48. Added null/missing phase coverage: all 44 pause tests passed. Actual MCP/HTTP runtime and old-policy coverage: 22 passed.
- Full suites: **454 passed on Python 3.13.12** (72.60 s) and **454 on Python 3.11.14** (77.67 s). Ruff check/format and wheel/source builds passed. Python 3.11 used an isolated uv environment; registered/runtime configuration was not changed.
- Initial complete audit: 57 source/document files, 118 local links, wheel/sdist and 17 ignore samples, no configured private-literal/generated-artifact matches or broken links. Final build/audit follows review/document closeout.
- Fresh-context independent review dispatched against the full 18-file scope. Reviewer is read-only, cannot use the printer or spawn another reviewer. Final findings and verification will be recorded here before integration.
- Usage tool observed next five-hour reset **2026-10-26 00:04:22 UTC**. Updated this same ACTIVE automation through automation_update to begin **00:24:22 UTC** (October 25, 19:24:22 America/Chicago), then every five hours. Prompt/project/model/reasoning/status/environment/working-directory fields verified unchanged. No duplicate/reset credits; future runs must recheck drift when useful.

### Interrupted-run reconciliation — 2026-10-26 UTC

Ruling: The previous chat failed at its usage limit before review/integration or
memory closeout. Resume its existing 18-file change at the same baseline, rather
than repeat implementation or probes. Its chat is idle; no unrelated work or
other active bridge editor was found. No new live printer request is needed.

- A fresh independent reviewer is checking the complete inherited scope. The
  previous review had no recorded verdict and is not counted as acceptance.
- Fresh Ruff check/format and wheel/source builds passed. Complete source/package
  audit again passed: 57 files, 118 local links, both archives and 17 ignore
  samples; no configured private literals/generated artifacts or broken links.
- Usage tool now reports reset **2026-10-26 05:21:55 UTC**. Updated this same
  ACTIVE automation through automation_update to start **05:41:55 UTC**
  (October 26, 00:41:55 America/Chicago), then every five hours. A parsed before/
  after comparison found only schedule and update-time changes; all other saved
  fields are identical. No duplicate automation or reset credits used.
- Fresh full verification: **454 passed on Python 3.13.12 in 71.84 s** and
  **454 on Python 3.11.14 in 78.49 s**. Both archives contain exact copies of
  all 12 current source modules. Local upload enablement remains false. Eight
  original export bytes/hashes and first-refusal codes remain unchanged.
- Independent fresh-context review: **Critical 0, Important 0, Minor 0**;
  separately **454 passed on Python 3.13.12 in 71.00 s**, Ruff check/format and
  diff whitespace checks passed. Additional durable policy-6 receipts with the
  new pause fields removed rejected undispatched uploads, retained unknown
  outcomes despite matching bytes, and preserved verified-result timestamps;
  no POST replayed. Source/artifact identities and historical passive-receipt
  timestamps/boolean were independently checked. No tracked reviewer edits.

Final: Ruling: Hardware upload/control acceptance, loaded callback/code identity,
motion completion/safe resume and physical clearance/quality remain unjudged;
the bridge does not claim these from reports or simulation. They remain explicit
readiness blockers. The reviewer's deferred parent Python-3.11/package/privacy
checks passed as recorded above; none is an omitted verification gate.

- Final review needs no fix pass or deferred minor. Integration preflight fetched
  remote main at the unchanged baseline `20ef873b14c9e4891ad5ca3a1d128f550ff7ca52`.
  Only this plan's inherited change and closeout documentation are in scope;
  no branch/PR, unrelated changes or live printer interaction was introduced.
  Final package/audit checks follow documentation closeout before commit/push.
