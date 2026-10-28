# Project state

Last updated: 2026-10-28 UTC

## Current stage

Unreleased `0.1.0.dev0` now exposes five Python/stdio tools: three installed-U1
read tools plus restricted `u1_prepare_print` / `u1_upload_print`. File transactions
are verified against local simulation and actual MCP subprocesses; uploads remain
disabled by default and unaccepted on hardware. Print controls, broad stock-U1
G-code support and camera implementation remain incomplete. The owner requested
ongoing development and commit/push on `main`. The 2026-10-27 owner scope update
authorizes normal desktop UI use and very small agent-selected diagnostic prints;
see D026 and AGENTS.md. Physical clearance remains time-specific. An attended
follow-up now reaches the connected Device view and a usable ordinary camera
image. This resolves the desktop pairing dependency, not MCP camera lifecycle,
file-transfer/control acceptance or physical clearance for a diagnostic print.

The next manual round prepared one 10 × 10 × 0.6 mm coupon externally and reached
the ordinary Upload-only/Send workflow. With the owner's final Send assistance,
all 49,972 native-export bytes were read back from the exact G-code-root target
with matching SHA256 by 20:31:29 UTC; surrounding state stayed idle/inactive-SD.
This is vendor transfer evidence, not MCP upload or print acceptance. Stock setup
effects remain unbounded and the file remains rejected. The owner subsequently
confirmed an installed, clear bed at 20:41:38 UTC for that diagnostic; this is
historical clearance, not standing clearance for future starts. A subsequent
October 28 owner-directed native start is now observed below. See the
[diagnostic report](docs/research/2026-10-27-diagnostic-preprint-evidence.md).

## Verified evidence

- Owner-directed native diagnostic, **2026-10-28 12:02:30–12:07:24 UTC**: fresh
  installed/clear-bed confirmation, ready/idle/material/nozzle/mapping checks and
  exact remote/local bytes preceded one ordinary File information Send. Expected
  filename, printing and active virtual SD were observed, with no exceptions.
  Layer 1/3 then 3/3 and complete/inactive-SD were observed; final targets zero,
  no exceptions, printer duration 49.20 s. The owner subsequently inspected and
  approved this coupon with a photograph (recorded 12:17:45 UTC); no measured
  dimensions or separate fit result were supplied. This is native hardware
  start/completion and owner inspection evidence; policy 12,
  bridge rejection and disabled uploads remain. See the
  [print report](docs/research/2026-10-28-native-diagnostic-print.md).
- Policy **12** rejects duplicate JSON members before interpreting read evidence
  or upload acknowledgments. A reproduced true/false active-SD pair previously
  normalized to `ok`/idle; duplicate start/queue/path/root flags could also be
  silently collapsed. Reads now fail closed and ambiguous acknowledgments remain
  terminal unknown without replay. Policies 1–11 cannot dispatch/promote uncertain
  receipts. Firmware syntax no longer bypasses configured secret/host or label
  length filters. These are synthetic software corrections; no live request or
  hardware acceptance. See the
  [response-boundary ledger](docs/superpowers/plans/2026-10-28-json-evidence.md).
- Fresh full suites passed **785 tests each on Python 3.11.14/3.13.12**,
  including ambiguous JSON over real MCP and policy-11 fencing. Ruff check/format,
  wheel/source builds and original export byte/refusal checks passed. Final
  review/package receipts are recorded in the response-boundary ledger.
- Policy **11** retains valid source times immediately after each completed
  status, material and closing runtime read during uncertain-upload verification,
  even when later validation/read/cancellation fails. This closes a reproduced
  policy-10 stale-promotion gap across restart. Policies 1–10 cannot dispatch or
  promote uncertain operations. No upload replay or new command/file acceptance;
  [correction ledger](docs/superpowers/plans/2026-10-28-reconciliation-observations.md).
- Fresh final suites passed **764 tests each on Python 3.11.14/3.13.12**,
  including failure/cancellation in both verification windows, actual MCP restart
  and old-policy refusal. The 53 observation tests also catch omission of the
  second sink; software checks do not establish physical compatibility.
- Existing diagnostic's ordinary File information page inspected at
  **2026-10-27 23:57–23:59 UTC**: saved filename matched, displayed PLA/0.12 g,
  physical tool 1, under-one-minute estimate and flow/time-lapse/leveling controls.
  No Send/setter/start selected. Displayed options do not attest effective hidden
  tables or full setup demand. Returned Device viewer showed **Camera not on**;
  cause and completed cleanup remain unknown. No Play/stop/light action selected.
- Diagnostic continuation, **2026-10-27 20:19–20:31:29 UTC**: current supported
  status/material reads confirmed idle, zero targets, inactive virtual SD,
  mapping and loaded PLA evidence. Two intact external-slicer exports show
  one-versus-four metadata differences; the native file has aligned four-entry
  arrays and T0-only declared consumption, but setup still invokes multi-head
  feed/flow, mesh and camera paths. Ordinary Upload opens a second Send page.
  After embedded-WebView input refusals, the owner submitted that Send; exact
  remote bytes/SHA256 matched. No captured start/queue response flags, start,
  calibration or MCP acceptance. Fresh suites passed **706 on each Python
  3.11.14/3.13.12**; see the
  [ledger](docs/superpowers/plans/2026-10-27-diagnostic-preprint-evidence.md).
- Attended desktop follow-up, **2026-10-27 20:06–20:08:25 UTC**: owner reported
  connection; the normal Device view showed connected/idle, all heater targets
  zero, nozzles 28–29 °C and bed 26 °C. One normal camera-view action initially
  showed a dark image; after the ordinary chamber light was enabled, a clear
  chamber image appeared. Viewer and light remain on. No print/file transfer,
  heater/motion/calibration or separately crafted camera API command was selected.
  Camera ownership, frame timestamps and completed cleanup remain unverified;
  the image is not human installed/clear-bed confirmation. See the
  [follow-up evidence](docs/research/2026-10-27-desktop-metadata-evidence.md#attended-desktop-follow-up).
- Cancellation correction: policy **10** commits a completed opening
  reconciliation observation before awaiting remote bytes. A failing regression
  reproduced promotion of time 1500 after a cancelled time-2000 observation;
  restart now refuses older evidence and can reconcile equal-time matching bytes
  without replay. Policy-1–9 dispatch/uncertain promotion is refused. Fresh full
  suites passed **706 tests on each Python 3.11.14/3.13.12**. Five tools, restricted
  files and disabled uploads remain. Ruff/build/export/package gates passed;
  audit checked 75 files, 227 links, both archives and 33 ignore samples with
  zero configured private-literal/credential/artifact/link findings. Independent
  final review found no actionable findings; see the
  [fix ledger](docs/superpowers/plans/2026-10-27-reconciliation-watermark.md).
  One desktop observation found Add Device still disconnected; no new Connect,
  printer query, upload/control/camera action or hardware acceptance occurred.
- Desktop/metadata continuation: normal UI discovery found the U1, but one LAN
  Connect attempt required printer-touchscreen approval and ended in Binding
  rejected after expiry. No connected device/preprint/camera view or upload/print/
  control/configuration action. Three newly extracted producer modules match the
  saved image and pinned public tree. The server preserves independent metadata
  array lengths; client display padding/truncation/nozzle fallback does not
  establish effective file-bound parameters. No runtime/policy/acceptance change.
  See the [report](docs/research/2026-10-27-desktop-metadata-evidence.md) and
  [ledger](docs/superpowers/plans/2026-10-27-desktop-metadata-evidence.md).
- Desktop/metadata software checks: **700 tests on each Python 3.11.14/3.13.12**,
  Ruff check/format and wheel/source builds passed. All eight original export
  hashes/refusals remain unchanged. Audit: 74 files, 223 local links, two archives
  and 33 ignore samples; zero configured private-literal/credential-pattern/
  generated-artifact matches or broken links. All 12 modules and eight changed
  documents match their packages. Independent source/document review found no
  actionable findings; it checked parent gate receipts without rerunning suites.
  Software checks do not prove UI pairing,
  effective metadata, printer controls or hardware acceptance.
- Hidden job-parameter continuation traces per-field parser fallback, logical/
  physical/category array roles, retained reset/reprint state and selected-file
  ordering. The setter compares used heads with nozzle entry zero; that does not
  resolve export header cardinalities. It assigns tables before filename checks,
  and persistence success means enqueue acceptance, not completed atomic writes.
  Effective parameters and file association remain unreported. **No live request**
  or runtime/policy/tool/acceptance change. See the
  [parameter report](docs/research/2026-10-27-job-parameter-evidence.md) and
  [execution ledger](docs/superpowers/plans/2026-10-27-job-parameter-evidence.md).
- Parameter continuation verification: **700 tests on each Python 3.11.14/
  3.13.12**, Ruff check/format and wheel/source builds passed. Independent review
  checked five artifact identities/two public blobs and all focused source
  claims, separately passed 700 tests, and found no actionable issues. Audit:
  72 files, 209 local links, two archives and 33 ignore samples; no configured
  private-literal/credential-pattern/generated-artifact matches or broken links.
  All 12 modules and eight changed documents match their packages. These are
  software/source checks, not effective parameter or hardware acceptance evidence.
- Flow-calibrator saved-source continuation resolves per-invocation measurement
  ceilings: six dichotomy, five linear-fitting and four OS calls. Field-specific
  parameter precedence/default validation, abort checkpoints, pressure-advance
  and cleanup effects are traced. Effective environment/parameters/provenance
  and total material/time/completed cleanup remain unreported; no status provider
  exists on the inspected class. **No live request**, runtime/policy/tool/field
  change or expanded acceptance. See the
  [flow report](docs/research/2026-10-27-flow-calibration-evidence.md) and
  [execution ledger](docs/superpowers/plans/2026-10-27-flow-calibration-evidence.md).
- Flow continuation verification: **700 tests passed on each Python 3.11.14/
  3.13.12**, Ruff check/format and wheel/source builds passed. Independent review
  corrected a temporary acceleration-cap precision gap, independently checked
  all five file identities/source bounds and passed 700 tests; no findings remain.
  Audit: 70 files, 193 local links, two archives and 33 ignore samples; no configured
  private-literal/credential-pattern/generated-artifact matches or broken links.
  All 12 modules and eight changed documents match their packages. No runtime
  change or hardware acceptance; the source call counts are conditional local
  bounds, not a complete physical demand/cleanup guarantee.
- Camera worker continuation: saved `unisrv` has shared renewal/expiry and an
  object destructor that clears both domain flags and joins its worker. Flags
  can clear before callbacks/resource release; approximate compiled timing is
  not an installed lease or external completion receipt. Camera ownership,
  freshness and completed cleanup remain blocked. Independent feed tracing finds
  per-key table fallback and rollback to defaults after later flow-validation
  failure, with no exposed resolved provenance. **No live request** or tool/
  field/policy/acceptance change. See the
  [worker report](docs/research/2026-10-26-camera-worker-evidence.md),
  [feed report](docs/research/2026-10-26-feed-resolution-evidence.md) and
  [execution ledger](docs/superpowers/plans/2026-10-26-camera-worker-evidence.md).
- Worker/feed verification: **700 tests passed on each Python 3.11.14/3.13.12**,
  Ruff check/format and wheel/source builds passed. Independent review found no
  actionable findings, checked all 4,560 decoded instructions/thresholds/source
  anchors and separately passed 700 tests. Audit: 68 files, 180 local links,
  both archives and 33 ignore samples; no configured private-literal/credential-
  pattern/generated-artifact matches or broken links. Runtime is unchanged;
  these checks do not establish firmware execution or hardware acceptance.
- Camera RPC continuation: saved firmware `unisrv` registrations/handlers now
  have focused static evidence. Monitor stop validates a domain and can return
  success without clearing flags or calling cleanup; time-lapse stop can return
  after detaching work. Registered `camera.get_status` reports coarse domain/
  time-lapse flags, not ownership, expiry, freshness or completed cleanup.
  Client correlation/timeouts/subscription/QoS limits are traced. **No live
  request**, new tool/field, policy or acceptance change. Camera readiness remains
  blocked; see the [RPC report](docs/research/2026-10-26-camera-rpc-evidence.md)
  and [execution ledger](docs/superpowers/plans/2026-10-26-camera-rpc-evidence.md).
- Camera continuation verification: **700 tests passed on Python 3.11.14 and
  3.13.12**, plus Ruff check/format and wheel/source builds. Independent review
  validated all 2,976 reported instructions, separately passed 700 tests and
  caught one reversed domain-precedence statement; corrected against artifact
  bytes, with no findings remaining. Complete audit: 65 files, 156 local links,
  both archives and 27 ignore samples; no private-literal/credential-pattern/
  generated-artifact matches or broken links. Runtime behavior is unchanged.
- Job preference continuation: policy **9** binds eight exact booleans, two
  physical four-head boolean arrays and fixed entanglement sensitivity through
  existing status/runtime reads. Missing/malformed/changed reports prevent
  dispatch/promotion; policy-1–8 uncertain work cannot promote or replay. Getter
  refresh/reset/reprint and calibration/feed/end/time-lapse consumers are traced.
  Preferences do not prove action completion; a failed time-lapse stop can clear
  local activity without proving server cleanup. **No live request** or new
  tool/command/export acceptance. See the
  [job report](docs/research/2026-10-26-job-flag-evidence.md) and
  [execution ledger](docs/superpowers/plans/2026-10-26-job-flag-evidence.md).
- Job preference software verification: **700 tests passed on Python 3.11.14
  and 3.13.12**, including all-field change/missing races, actual MCP/loopback
  HTTP and policy-8 refusal. Ruff check/format and wheel/source builds passed;
  all 12 source modules match both archives. Scope audit checked 63 source/doc
  files, 142 local links, both archives and 23 ignore samples with no configured
  private literals, generated artifacts, credential-pattern matches or broken
  links. All eight original exports remain byte/hash-identical and rejected.
  Independent review found no actionable or deferred findings, separately passed
  all 700 tests on Python 3.13.12 and 176 malformed/schema/historical-receipt probes.
  Hardware compatibility, action completion and camera cleanup remain unproven.
- Machine/action continuation: policy **8** binds fixed integer main/action
  reports. Both IDLE codes are required for positive idle; recognized nonzero
  activity independently vetoes idle and unknown reports cannot establish it.
  One passive GET at **2026-10-26 05:46:40 UTC** confirmed both integer zero.
  Artifact tracing establishes separate labels/SD/statistics and post-update
  hook ordering, not transition/physical completion or loaded hook identity.
  No command/export newly accepted or live mutation; see the
  [machine/action report](docs/research/2026-10-26-machine-state-evidence.md).
- Machine/action software verification: **520 tests passed on Python 3.11.14
  and 3.13.12**, including machine report races and actual MCP/loopback HTTP.
  Ruff check/format and wheel/source builds passed; all 12 source modules match
  both packages. Scope audit passed 60 files, 130 local links, both archives and
  19 ignore samples with no configured private literals/generated artifacts or
  broken links. Independent review found no actionable findings or deferred
  minors, separately passed all 520 tests on Python 3.13.12 and checked historical
  policy-7 schemas/terminal timestamps without upload replay. See the
  [execution ledger](docs/superpowers/plans/2026-10-26-machine-state-evidence.md).
- Pause/end continuation: policy **7** binds fixed `pause_resume.is_paused`
  reports. Idle/preparation now require explicit false; true is independently
  busy and missing/null/malformed stays unknown. Source traces layer/error/idle
  callbacks and motion/heat/feed/camera effects without accepting commands or
  treating reset job flags as completed actions. One passive GET at **2026-10-25
  20:44:18 UTC** confirmed boolean false. No live mutation/preparation/control.
  Saved restore state and complete callback effects remain unknown. See the
  [pause/end evidence](docs/research/2026-10-25-pause-end-evidence.md).
- Pause/end software verification: **454 tests passed on Python 3.11.14 and
  3.13.12**, including true/null/missing pause races through preparation/preflight/
  hashing/restart and actual MCP/loopback HTTP policy-6 refusal. Ruff check/format
  and wheel/source builds passed. Independent review found no actionable issues
  or deferred minors and separately passed all 454 tests on Python 3.13.12,
  checked historical policy-6 schemas without replay, and verified source/report
  identities. Final audit passed: 57 files, 118 local links, both archives and
  17 ignore samples; no configured private literals/generated artifacts or broken
  links. All 12 source modules match both packages. The interrupted prior run was
  reconciled without another live request. See the
  [execution ledger](docs/superpowers/plans/2026-10-25-pause-end-evidence.md).
- Per-head extrusion continuation: policy **6** binds reported nozzle diameter/
  volume type, pressure advance/smoothing and queue-name evidence for all heads.
  Used reported nozzle sizes must agree with file and operator attestation.
  Reused the historical 13:59:41 UTC response; **no live request** in this round.
  Null queue name can coexist with constructor-attached trapq; actual attachment,
  saved K and hidden feed/thermal demand remain unknown. Inspected transform reads
  still lack the decisive diagnostic; no macro/export newly accepted. See
  [per-head evidence](docs/research/2026-10-25-head-extrusion-evidence.md).
- Head continuation verification: **403 tests passed on Python 3.11.14 and
  3.13.12**, including all five head-field races through preparation/preflight/
  hashing/restart and actual MCP/loopback HTTP policy-5 refusal. Ruff check/format
  and wheel/source builds passed. Independent fresh-context review found no
  actionable findings, separately passed all 403 tests on Python 3.13.12 and
  checked 50 malformed/privacy cases and source/report identities. Audit:
  54 files, 104 local links, both archives and 14 ignore samples; no configured
  private literals/generated artifacts found in source/package scope.
- Focused transform continuation: one three-field exclusion GET at **2026-10-25
  15:23:02 UTC** confirmed empty excluded list, explicit null current object and
  false region flag. Status and policy-5 receipts now bind bounded private label
  hashes/counts/presence and region reports. Policies 1–4 cannot dispatch/promote
  uncertain uploads. Matched source establishes that empty reports cannot prove
  transform removal and that region flags can lag markers. Effective mesh fade,
  lookup/ZFADE, chain installation/order and calibration provenance remain unknown
  through inspected supported reads. No command/export newly accepted; no live
  mutation/preparation. See [transform evidence](docs/research/2026-10-25-transform-evidence.md).
- Transform continuation verification: **342 tests passed on Python 3.11.14 and
  3.13.12**, including actual MCP/loopback HTTP, all three exclusion-field races,
  same-size label changes, missing reports and policy-4 restart refusal. Ruff
  check/format and wheel/source builds passed. Independent fresh-context review
  found no actionable issues, separately passed all 342 tests on Python 3.13.12,
  and verified source identities/claims and historical-model defaults. Audit:
  51 source/doc files, 89 local links, both archives and 11 ignore samples; no
  configured private literal or generated runtime artifact found in the audited
  source/package scope. One new three-field GET only; no hardware acceptance.
- Bounded runtime-evidence follow-up: one seven-object GET at **2026-10-25
  13:59:41 UTC** confirmed reported per-head offsets, global homing origin,
  coordinate/mode fields and populated mesh matrices. Selected head 2 coexisted
  with all heads reported parked and no homed axes. The five-tool bridge now
  normalizes this subset in status and binds repeated observations to policy-4
  preparations/receipts, refusing missing/inconsistent/drifting/backwards-time
  evidence without upload replay. Calibration provenance, full transform chain
  and machine-space motion remain unestablished. All eight intact exports still
  fail. See [runtime evidence](docs/research/2026-10-25-runtime-evidence.md).
- Runtime follow-up verification: **300 tests passed on Python 3.11.14 and
  3.13.12**, including actual MCP/loopback HTTP, runtime races and policies 1–3
  dispatch/reconciliation refusal. Ruff check/format and wheel/source builds
  passed. Independent review ran the full pre-fix 295-test suite and identified
  two P2 contradictions (all-parked selection and empty-mesh extrema); both were
  reproduced in failing normalization/preparation regressions and corrected.
  Final 300-test suites passed after fixes; no finding was deferred. Audit:
  49 source/doc files, 76 local links, both archives and nine ignore samples;
  no configured private value or generated runtime artifact in tracked/package
  scope. Exactly one new live GET; no mutation or hardware acceptance.
- Startup/toolchange follow-up traces physical selection/retries, calibrated
  XYZ/E origins, saved flow K, hidden feed/calibration/purge, homing/mesh and
  pause/object/end/camera branches. Restricted validation now forgets XYZ after
  T and active tool/E after G28, binds positive heater targets to requirements,
  refuses physical heater aliases and enforces firmware selector syntax.
  Policy 3 prevents policy-1/2 dispatch/promotion without replay. All eight
  unchanged normal exports remain rejected; uploads remain disabled. See the
  [focused chain/evidence report](docs/research/2026-10-25-startup-toolchange.md).
- Startup/toolchange verification: **246 tests passed on Python 3.11.14 and
  3.13.12**, including actual MCP/loopback HTTP and policy-2 restart refusal.
  Ruff check/format and wheel/source builds passed. The complete 43-file scope,
  64 local document links, both archives and nine ignore samples passed the
  privacy/artifact audit. Independent final review found no actionable issues;
  it separately passed 187 relevant tests and rechecked the source identities.
  This follow-up issued no live printer request.
- Firmware-matched G-code follow-up: eight representative local exports inspected;
  36 previously unsupported command names plus unsupported parameter forms found.
  **No complete normal export is newly accepted.** Bounded progress/fan/acceleration
  forms and explicit-G17 absolute XY arcs now work in supported synthetic programs.
  Macro/offset/calibration/camera effects remain blocking; three exports also have
  ambiguous one-entry filament/four-entry nozzle metadata. See the
  [version-matched report](docs/research/2026-10-25-orca-u1-gcode.md).
- Fresh read-only capability/configuration evidence confirms firmware
  `2.0.0.205_20260914173503`. Its downloaded vendor artifact matches 14 selected
  Python source files and two configs from pinned release head `bc271fb351f8c3ad84300e652e46fd93c53b9de1`.
  All 87 compared macro executable bodies agree (86 normalized texts match; two
  inline comments account for the other). This is static/version/configuration
  evidence, not attestation of live code or hardware upload/print acceptance.
- Previous independent follow-up review reproduced inherited arc-plane and decimal fan-ID
  syntax issues. Both were regression-tested and fixed. Policy identity 2 blocks
  old-receipt dispatch/promotion while retaining unknown-outcome no-replay rules.
  This is superseded by policy 3's stricter validation.
- Previous follow-up verification: **215 tests passed on Python 3.11.14 and 3.13.12**,
  including actual MCP numeric-form success and stock/unsafe-form refusal.
  Ruff check/format and wheel/source builds passed. Independent recheck found
  no remaining material issue in the reviewed scope. Only live GETs were issued.
- Previous upload milestone: **123 tests passed on Python 3.11.14 and 3.13.12**.
  Ruff checks/formatting and wheel/source builds passed. Real MCP subprocesses
  exercised five-tool discovery, preparation, HTTP multipart uploads, corruption,
  material/mapping/path failures, HTTP-200 errors and restart reconciliation.
  Additional tests cover expiry, late writes, cancellation, duplicate IDs/claims,
  state races and a second process holding the journal lock.
- Independent upload review reproduced G91/M82 and tool-change E-origin bypasses;
  both are regression-tested and fixed. Cold retraction is also accounted for.
  A resource concern was resolved with bounded lazy parsing and worker threads.
  The narrow source contracts and limitations are recorded in
  [upload evidence](docs/research/2026-10-24-uploads.md). No hardware interaction
  occurred during this milestone; no upload enablement or live settings changed.
- Historical read baseline: 59 tests passed on Python 3.11.14 and 3.13.12. Ruff checks/formatting and wheel/
  source-distribution builds passed. Tests exercise actual stdio MCP plus local
  HTTP simulation, without hardware or credentials.
- Independent review reproduced compression memory amplification and SDK logging
  of malformed request payloads. Both fixes were regression-tested and rechecked;
  no findings remained.
- Local Codex entry `snapmaker_u1` was registered. Its configured command/env were
  exercised by the official MCP client: initialize, exactly three tools listed,
  all three calls `ok`, empty stderr, **2026-10-24 17:34:05 UTC**. Discovery in
  this chat was subsequently confirmed by a discovered `u1_capabilities` call at
  **2026-10-24 17:54:59.822526 UTC**, returning `ok` and the same firmware.
- Live reads reported firmware `2.0.0.205_20260914173503`, Moonraker `2.0.0`,
  Klipper ready while printing, active virtual SD, and selected physical tool 2
  (`extruder1` / T1). Exceptions were empty in that snapshot.
- All four enabled toolhead sensors and feed modules reported filament present
  and completed/error-free loading. Four loaded states and the 32-slot mapping
  were returned. This is time-specific sensor evidence, not physical inspection
  or a continuing loading guarantee.
- All live checks were reads. No upload/control, motion, camera start/stop,
  firmware/configuration, or calibration action was issued.
- Isolated REA 6.7.0/Node 24.22.1 and checksum-verified Rizin 0.9.1 now support
  focused native inspection. Seven DLL functions (34,540 bytes) and seven more
  GUI excerpts were inspected without executing target code. The native WCP
  camera branch reaches JSON-RPC over TLS MQTT; pinned Orca 2.4.0 source describes
  certificate bootstrap and response correlation. This is static evidence, not
  an installed-printer camera transaction. Full doctor/Ghidra readiness is not claimed.
- The native camera branch drops the GUI's optional `clientid`. A 300-second GUI
  renewal/close timer is established; server expiry and ownership are not. See
  the [camera report](docs/research/2026-10-24-camera.md) for anchors and limits.

Raw replies, local config, receipts, app excerpts, and REA artifacts are ignored.
Tracked fixtures are synthetic. [Read evidence](docs/research/2026-10-24-read-contracts.md)
records pinned public source and installed-contract limits.

## Remaining gaps and next actions

1. Broader firmware versions, real outages, and active exceptions have
   simulated/source evidence, not hardware acceptance.
2. Validate the native camera branch against installed firmware with one bounded,
   redacted passive trace of an ordinary operator-authorized transaction. No
   unverified camera API mutation is authorized by desktop permission alone.
   Normal authenticated UI viewing is now permitted under D026. Server ownership,
   expiry, credential provisioning, freshness and safe cleanup remain prerequisites
   for camera tools; the trace alone will not resolve them all.
3. Perform scoped hardware acceptance for authorized very small diagnostic jobs:
   multipart upload/download,
   exact path/flag envelope, no-start/no-queue behavior, authentication and recovery.
   Bind the traced stock-U1 macro/offset/mesh, per-head thermal/consumption and
   conditional runtime dependencies before accepting normal Orca U1 profiles.
   The reported coordinate/mesh/head subset is collected and bound. A
   vendor-supported passive diagnostic for chain installation/order, effective
   mesh fade/lookup/ZFADE and calibration provenance: inspected status/dump fields
   do not expose them. No such diagnostic was identified; keep these unknowns.
   Pause/end source dependencies and independent saved-pause binding are now
   documented; machine/action labels now also bind receipts without certifying
   transition/hook completion. Job preferences now bind receipts, with read-time
   refreshes and reset/reprint/consumer limits documented. Camera RPC tracing now
   finds a monitor-stop acknowledgment without cleanup and a coarse server status
   candidate that cannot prove ownership/cleanup. The worker's shared expiry and
   destructor are now traced, without an external owned-completion contract.
   Do not repeat these camera traces without changed evidence. Feed resolution
   now establishes per-key fallback and rollback that can discard temperature
   lookups. Flow-calibrator precedence and finite local search counts are now
   traced; total demand and effective parameters remain unreported. Hidden-table
   parsing, array roles, reset/reprint lifetime and asynchronous persistence are
   now traced; no bound file provenance is exposed. The upstream server/client
   producer is also traced: submission preserves array mismatch while display
   fallbacks can hide it. Close both source traces without guessing mappings.
   Normal LAN binding now reaches the connected Device view, and one ordinary
   operator-assisted Upload-only transfer has exact remote-byte evidence. The
   existing uploaded diagnostic's ordinary preprint options have now been
   inspected without submission. They expose selections, not a passive effective
   parameter/startup receipt. The concrete hardware blocker is a vendor-supported
   passive diagnostic binding effective parameters and full setup demand to this
   file; none is established for broad bridge acceptance. The subsequent
   [owner-directed native diagnostic](docs/research/2026-10-28-native-diagnostic-print.md)
   has an observed start after fresh physical/file/material/state checks; retain
   its outcome separately from bridge certification. Do not repeat UI/source/
   transfer work as a substitute or start another job to discover hidden settings.
   Do not repeat pairing while the
   existing connection works or bypass normal authorization.
   Unverified camera API mutations and diagnostic raw G-code remain outside this
   scope. Callback bodies remain unbound. Saved K and hidden
   feed thermal/consumption are also
   absent from the inspected status providers. Do not repeat head/mesh/config
   snapshots or infer those values from reports. This does not bound the remaining
   macro chains. Current restricted files and journals are described in
   the [upload evidence](docs/research/2026-10-24-uploads.md).
4. Implement future print job-parameter/start/controls after their contracts are
   resolved. The preparation/upload implementation applies no job parameters.
5. D026 delegates selecting a very small diagnostic file/plate. Document it and
   verify installed-plate/current human clearance before start; fresh clearance
   is needed after each plate or uncertain intervening activity. Other jobs need
   their own authorization. Print completion/quality checks remain.

The [roadmap](ROADMAP.md) owns milestone status. This milestone is neither a
release nor full print/camera capability.
