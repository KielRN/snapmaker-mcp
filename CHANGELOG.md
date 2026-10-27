# Changelog

Implemented changes only. No published release exists.

## Unreleased — 0.1.0.dev0

### Fixed — 2026-10-27 UTC

- Reconciliation now durably records a completed opening runtime observation
  before awaiting remote bytes. Cancellation during the download can no longer
  lose that watermark and promote older evidence after restart. Policy 10 refuses
  policy-1–9 dispatch or uncertain promotion without replaying uploads. Five tools,
  the restricted file dialect and disabled uploads remain; no hardware acceptance.

### Added — 2026-10-27 UTC

- Normal desktop LAN connection evidence: discovery succeeded, but binding
  expired pending touchscreen authorization and reported Binding rejected.
  Firmware/public-matched metadata producer and saved client display/submission
  paths are documented. Raw array lengths remain independent; display fallbacks
  do not justify new acceptance. Documentation only; no runtime/policy change,
  upload, print/control or camera acceptance.
- Durable owner instructions for normal Snapmaker desktop UI use and delegated
  very small diagnostic prints. Physical-clearance freshness, session ownership,
  validation and evidence boundaries remain. Authorization record only; no UI/
  printer execution, new MCP capability or hardware acceptance.
- Saved-source hidden job-parameter evidence: per-field parsing/fallback, array
  roles, reset/reprint lifetime, assignment before filename checks and separate
  asynchronous persistence. Effective file-bound provenance and upstream metadata
  correspondence remain unresolved. Documentation only; no live request,
  runtime/policy/tool/field change or expanded file acceptance.
- Saved-source flow-calibration evidence: field-specific parameter precedence,
  default-validation limits, finite per-invocation search counts and conditional
  direct-E arithmetic. Abort/thermal/pressure-advance/cleanup effects leave total
  demand, effective provenance and completion unresolved. Documentation only;
  no live request, runtime/policy/tool/field change or expanded file acceptance.

### Added — 2026-10-26

- Saved-firmware camera worker renewal/expiry/normal-exit/destructor evidence.
  Shared expiry exists but supplies no externally completed owned cleanup;
  notification timestamps do not establish image freshness. Independent feed
  resolver tracing establishes per-key fallback and rollback after later flow
  validation. Documentation only; no live request, runtime/policy/tool change or
  new file acceptance. Camera and stock-file readiness remain incomplete.
- Focused saved-firmware camera RPC research: client correlation/timeout/QoS
  limits and server registrations/status/stop handlers. Monitor stop can return
  success without cleanup, while time-lapse stop can detach work; coarse server
  flags do not establish ownership, expiry, freshness or completed cleanup.
  Documentation only; no live request, new tool/field/policy or acceptance.
- Bounded job preference reports in existing status/runtime receipts under
  policy 9, with a fixed projection retaining existing material fields. Missing,
  malformed or changed flags block dispatch/promotion; policy-1–8 uncertain
  receipts cannot promote or replay. Getter refresh/reset/reprint and calibration,
  feed/end/time-lapse consumer limits are documented. No live request, new command,
  tool or export acceptance; uploads remain disabled and readiness incomplete.
- Fixed machine main-state/action-code status projection and policy-8 receipt
  binding. Positive idle requires both exact reported IDLE codes alongside prior
  checks. Recognized activity independently blocks idle; missing or unfamiliar
  codes stay unknown. Policy-1–7 uncertain receipts cannot promote or replay.
  One passive GET confirmed integer forms; source transition/SD/control ordering
  and omitted hook/completion evidence are documented. No command/export newly
  accepted; uploads remain disabled and hardware acceptance pending.

### Added — 2026-10-25

- Fixed saved-pause status projection, independently conservative idle checks and
  policy-7 receipt binding. Explicit false is required for idle; true/null/missing
  pause races cannot dispatch/promote uploads. Policies 1–6 cannot reuse old
  uncertain receipts; no upload replay. One passive GET confirmed the boolean.
  Pause/resume/end/cancel and configurable callback dependencies are documented,
  not newly accepted. Uploads remain disabled; hardware acceptance is pending.
- All-head reported nozzle/volume, pressure advance/smoothing and queue-name
  evidence in status/receipts under policy 6. Used nozzle reports must agree
  with file requirements and operator attestation. Policies 1–5 cannot dispatch/
  promote uncertain uploads; repeated-read and no-replay safeguards remain.
  Historical response reused; no new live request. Actual trapq, saved K and
  hidden feed thermal/consumption remain unknown. No command/export newly
  accepted; uploads remain disabled and hardware acceptance pending.
- Fixed exclusion status projection with private label hashes/counts,
  current-object presence and reported region flag, bound into policy-5 runtime
  receipts. A single three-field live GET confirmed forms. Policy-1–4 receipts
  cannot dispatch/promote uncertain results; no upload replay. Matched-source
  lifecycle/coordinate analysis documents why installation, effective mesh
  fade/lookup/ZFADE and provenance remain unknown. No new command/stock export
  acceptance or live mutation; five tools and disabled uploads remain.
- Bounded reported runtime evidence in `u1_status`: coordinate frames/modes,
  global origin, per-head offsets/park/activation reports and current mesh/profile
  digests. One read-only seven-object hardware query confirmed availability;
  missing fields and unexposed calibration/transform provenance remain unknown.
- Policy-4 preparation/receipt binding, repeated runtime observations around
  material/job reads and remote byte verification, ordered event times and a
  persistent reconciliation watermark. Policies 1–3 cannot dispatch/promote an
  uncertain upload, and no dispatched upload is replayed. Five tools remain;
  uploads stay disabled, all eight normal exports remain blocked, and no hardware
  mutation or acceptance occurred.
- Startup/toolchange chain investigation using the already matched firmware
  artifact. Restricted validation now invalidates XYZ after T and active tool/E
  after G28, accounts for positive heater targets, rejects physical heater aliases
  and enforces canonical tool/integer heater-selector syntax. Validator policy 3
  blocks policy-1/2 receipt dispatch/promotion without replay. Synthetic and actual
  MCP regressions cover these cases; no stock macro or intact export is newly
  accepted. No live printer request or configuration change occurred.
- Version-matched vendor firmware/source/configuration investigation and exact
  command/parameter inventory from eight private normal Orca U1 exports.
- Bounded M73 progress, auxiliary fan P2, M204 S, acceleration-only
  SET_VELOCITY_LIMIT and explicit-G17 absolute XY IJ arcs. Circle interiors,
  endpoints, helical Z, E consumption and heat are inspected conservatively.
- Validator policy 2, old-policy restart/receipt rejection tests, synthetic
  stock-shaped refusal fixtures and actual MCP tests for numeric forms and
  unsafe inputs. No normal full export is newly supported; no live mutation.

### Added — 2026-10-24

- Dedicated repository, operating guide, state/roadmap/decisions, design and
  ignore coverage for machine config, credentials and generated artifacts.
- Python 3.11+ package, official MCP SDK 1.x stdio runtime, locked dependencies,
  typed `u1_capabilities`, `u1_status`, and `u1_materials` tools.
- Fixed-origin read-only HTTP transport with total deadlines, raw byte limits,
  redirect/compression refusal, no environment proxies, sanitized outcomes, and
  no automatic retries or stale cached success.
- Four-tool mapping, RFID identity, feed/toolhead-sensor evidence, conservative
  loaded/idle/unknown states, temperatures, progress and numeric exceptions.
- 59 tests including actual MCP subprocess calls and simulated printer failures;
  regression coverage for compressed-body amplification and SDK validation logs.
- Tested setup/check/build commands, local Codex registration with verified launch,
  isolated pinned REA/Node installer, camera research and read-contract evidence.
- Focused camera follow-up: isolated Rizin 0.9.1 via REA, pinned Orca 2.4.0 source
  comparison and native call/table evidence for the WCP TLS MQTT path. Documented
  separate authentication layers, omitted camera `clientid`, client timer policy,
  unresolved server contracts, and a bounded passive next probe. No camera tools added.
- Restricted `u1_prepare_print` and optional `u1_upload_print`: canonical roots
  and opened-handle escape checks, all-entry consumption and executable heater/
  movement inspection, fresh mapping/material/feed binding, exact no-start upload
  envelope and downloaded SHA256 verification. Uploads default disabled.
- SQLite preparation/operation receipts, ten-minute default expiry, atomic upload
  claims, process/async serialization and read-only uncertain/restart reconciliation
  without replaying a POST. Historical and missing-ack evidence are explicit.
- Focused pinned file-transfer/G-code source evidence and real MCP/HTTP simulator
  tests. Stock U1 macros remain rejected; hardware compatibility is not claimed.

### Verification

- Per-head continuation: 403 tests passed on Python 3.11.14/3.13.12; Ruff
  check/format and wheel/source builds passed. Independent review found no
  actionable issue and separately passed all 403 tests, 50 malformed/privacy
  probes and source identities. Full audit passed: 54 files, 104 links, both
  archives and 14 ignore samples. No live printer request.
- Transform continuation: 342 tests passed on Python 3.11.14/3.13.12; Ruff,
  wheel/source builds and full privacy/artifact/link audit passed. Independent
  fresh-context review separately passed all 342 tests, verified source identities
  and found no actionable issue. One focused live exclusion GET only.
- Runtime-evidence follow-up: 300 tests passed on Python 3.11.14/3.13.12;
  Ruff check/format and wheel/source builds passed. Independent review ran the
  pre-fix 295-test suite and found two P2 report-consistency gaps; failing
  regressions reproduced both, fixes passed the final complete suites, and
  no finding was deferred. Tracked/package privacy and artifact audit: 49 files,
  76 local links, both archives and nine ignore samples. One live GET only.

- Startup/toolchange follow-up: 246 tests passed on Python 3.11.14/3.13.12,
  including real MCP/loopback HTTP and policy-2 restart rejection. Ruff
  check/format and wheel/source builds passed. Complete source/doc/archive
  privacy and generated-artifact audit passed. Independent final review found no
  actionable issues and separately passed 187 relevant tests. No live printer request.

- G-code follow-up: 215 tests passed on Python 3.11.14/3.13.12, Ruff check/format
  and wheel/source builds. Actual MCP simulation covers accepted numeric forms,
  unsafe arc interiors/endpoints, missing plane, decimal fan IDs, consumption,
  temperature and stock macros. Independent review findings were reproduced and
  fixed; its recheck found no remaining material issue. Live work was GET-only.

- Upload milestone: 123 tests passed on Python 3.11.14/3.13.12, Ruff check/format
  and wheel/source builds. Real stdio/HTTP simulation covers prepare/upload and
  restart reconciliation. Independent review's E-state bypasses were fixed and
  regression-tested; parser memory amplification was also addressed. No hardware
  interaction, live upload enablement or local printer configuration change.
- Full suite passed on Windows/Python 3.11.14 and 3.13.12; Ruff checks/formatting
  and wheel/source builds passed. Independent review returned no remaining findings.
- Registered MCP command initialized, listed/called all three tools against the
  installed U1, returning `ok` with empty stderr. All live checks were read-only.
- REA CLI/MCP and camera/lifecycle excerpts worked. Follow-up REA/Rizin inspected
  seven selected DLL functions (34,540 bytes) and seven additional GUI excerpts.
  Whole-bundle heap exhaustion is historical; full doctor/Ghidra readiness is
  not claimed. A fresh discovered capability tool returned `ok` on the same firmware.
- Follow-up checks passed: 59 tests on Python 3.13.12, Ruff check/format, wheel/
  source builds, documentation links and original-byte/source-provenance audits.

### Remaining scope

No release exists. File tools/receipts are implemented with simulated upload
acceptance only. Stock-profile macros, installed upload behavior and authorized
physical acceptance remain pending. Print-control and camera tools are absent.
Installed camera wire/authentication compatibility, server expiry/ownership and
image freshness remain unresolved. Static source evidence and simulation do not
prove these hardware capabilities.
