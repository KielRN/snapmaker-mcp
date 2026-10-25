# Startup and toolchange validation follow-up

> Execute inline under the owner's implementation, independent review and
> commit/push request. Stay on main; no live mutation is authorized.

**Goal:** Trace the matched firmware's transitive startup/toolchange effects and
close concrete validation gaps without claiming complete stock-profile support.

**Architecture:** Keep the five-tool bridge and restricted inspector. Invalidate
unknown coordinates after selection, bind thermal consumers to requirements,
refuse ambiguous physical heater aliases, and advance receipt policy. Dynamic
macro execution, slicing and firmware configuration remain outside the bridge.

**Tech stack:** Existing Python 3.11+, MCP/HTTPX/Pydantic; no new dependencies.

**Spec:** [Bridge design](../specs/2026-10-24-snapmaker-u1-mcp-design.md), validation,
transaction/data boundaries and acceptance; the owner's focused follow-up.

## Constraints and review focus

- Reuse the pinned firmware artifact/source and ignored investigation files.
- Distinguish G-code-space bounds from transformed machine motion; no offset,
  homing, probe, toolchanger or mesh acceptance follows from a source match.
- Follow conditional feed/calibration/replenishment and end effects for every
  used physical head; slicer consumption is not a bound on hidden macro E.
- Do not strip or evaluate setup/safety macros or start/stop camera sessions.
- Preserve path/hash, material/feed, mapping, expiry, serialization and recovery.
- Review stale XYZ after same/different tool selection, aliased physical heaters,
  undeclared thermal consumers, integer heater selectors and policies 1/2.

## Tasks and verification ledger

1. [x] Trace matched startup, selection/offset/E restoration, feed/calibration,
   cleaning/homing/mesh, pause/object/end/camera chains. Record source anchors,
   runtime inputs and unresolved bounds in a focused research report.
2. [x] Add failing parser/coordinator tests for stale coordinates, thermal
   consumers, heater selectors, alias mappings and old-policy receipts. Implement
   minimal hardening in `gcode.py` / `uploads.py`; require current policy 3.
3. [x] Exercise supported coordinate re-establishment and refused cases over
   real MCP stdio/local HTTP simulation, including no upload after refusal.
4. [x] Recheck all eight intact private exports without modifying them. Update
   state/roadmap/decisions/changelog/README/design with actual scope and limits.
5. [x] Obtain independent review, resolve material findings, run both Python
   suites, Ruff and builds, audit full scope/privacy/archives/links and inspect
   the complete working tree and remote base before integration.

**Integration:** Owner-requested commit/push on main follows the final audit;
Git history and the remote ref are its receipt. No branch change or PR.

**Preflight:** Baseline clean main `f84c200`; no Graphify graph exists. Existing
source and artifact identities are in the prior report. The owner explicitly
authorized implementation and independent review, so no additional design or
execution-method approval is needed. No printer access is necessary for this
follow-up; simulations must use loopback only.

**Shared interfaces:** `Inspection.used_tools` controls material/feed/nozzle
binding in `Coordinator._evidence`; positive heater targets must participate.
Per-logical heater tracking is sound only for injective requested mapping.
`Coordinator._policy` protects undispatched and inflight receipt promotion;
policies 1 and 2 must both refuse dispatch/promotion without replay.

## Execution evidence

- Independent source review reproduced stale-coordinate and physical-heater
  alias acceptance and identified thermal-demand and selector-syntax gaps.
  Thirteen new targeted cases failed before implementation, including policy-2
  dispatch and uncertain-result promotion; G28 identity and noncanonical T
  regressions were separately observed failing before fixes.
- Existing cold-extrusion tests now explicitly establish XYZ after selection so
  they continue to reach and verify the heat checks instead of failing earlier.
- Ruling: no new stock macro acceptance. Traced conditional dependencies remain
  unbound; explicit XYZ restoration certifies only G-code-space inspection.
- The first new real-MCP restart test used the wrong configuration object API;
  corrected it to dataclass replacement. Both restart modes subsequently passed.
- Final suites: 246/246 on Python 3.11.14 and 3.13.12. Ruff check/format and
  wheel/source builds passed. All eight unchanged hashes and rejection outcomes
  were rechecked. Audit: 43 scoped files, 64 local links, two archives and nine
  ignore samples; no configured private value or generated runtime artifact.
- Independent final diff review found no actionable findings. It separately
  passed 187 parser/coordinator/actual-MCP tests on Python 3.13.12 and reverified
  all 20 source and five additional artifact identities. No deferred findings.
- Fetched origin/main matched clean baseline `f84c200` before integration.
  No live request or configuration change occurred.
