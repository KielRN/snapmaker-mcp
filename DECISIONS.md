# Decisions

Last updated: 2026-10-26

Record durable choices with their date, status, and reason. **Confirmed** means
directly established by owner direction or carried-forward printer operating
instructions. **Proposed** means a working design choice awaiting resolution;
documentation alone does not make it owner-approved. Supersede an entry
explicitly when its direction changes.

## D001 — Dedicated repository

Date: 2026-10-24 · Status: Confirmed

Develop the bridge in `KielRN/snapmaker-mcp`, as requested by the owner. Keep
bridge code, tests, research, and documentation here. The 3DPrintPosters product
repository remains a separate project; changes to it need their own task scope.

## D002 — Full connection scope

Date: 2026-10-24 · Status: Confirmed

Cover printer status, file upload and start, pause/resume/cancel controls,
physical tool/material mapping, and camera access. The owner confirmed all of
these capabilities. Snapshot and live camera behavior are described in the
draft design; their actual protocol remains under investigation.

## D003 — Per-plate physical authorization

Date: 2026-10-24 · Status: Confirmed operating constraint

Every start requires authorization for the specific plate and fresh human
confirmation that the build plate is installed and clear. One start does not
authorize the next plate. Check current printer state, material feed, mapping,
exceptions, and the actual exported file before a start. An MCP argument cannot
independently establish physical clearance.

Do not change firmware, persistent printer configuration, or calibration as part
of this bridge workflow. Read-only inspection is appropriate while printing;
control actions must stay within the authorized job scope.

## D004 — Local connection using the verified protocol

Date: 2026-10-24 · Status: Confirmed for read milestone; advanced RPC proposed

The owner's implementation request adopts local Moonraker HTTP for the first
three read tools. All three were verified through actual MCP stdio on the
installed firmware. Build around the local HTTP connection exercised on the studio
U1. Add U1-specific RPC and subscriptions only after verifying the installed
version's transport and behavior. Public repository source is a research lead,
not evidence that the installed firmware has identical behavior.

Keep the printer interface private to the trusted LAN. Cloud-account dependence
is not assumed; a camera limitation that requires cloud login needs an explicit
decision rather than silently changing the architecture.

## D005 — Keep slicing outside the connection bridge

Date: 2026-10-24 · Status: Confirmed by focused upload implementation request

Use the existing OrcaSlicer integration for slicing. The new bridge validates
exported G-code, checks physical tool/material requirements, uploads it, and
coordinates verified printer operations. It does not generate geometry or
automatically send product-app customer orders to the printer.

## D006 — Python server over stdio

Date: 2026-10-24 · Status: Confirmed for this milestone by owner implementation request

Use Python 3.11+ and the official Python MCP SDK, with HTTP and WebSocket clients
where the verified protocol needs them. Run locally over stdio; send diagnostic
logs to stderr. This follows the existing local Python tooling. Exact compatible
dependencies and module layout are implementation choices. The implemented
package uses official MCP SDK 1.30.0 and HTTPX 0.28.1, with a committed uv lock.
No WebSocket dependency is introduced before the needed contract is verified.

## D007 — REA as a focused development tool

Date: 2026-10-24 · Status: Confirmed development direction by owner request

Use the official [REA project](https://github.com/morluto/rea) to investigate
specific missing contracts, beginning with the installed app's camera flow.
Inspect JavaScript and relevant native components as evidence directs. Keep
REA and any required Node/Ghidra runtime isolated from product environments.
The finished bridge should not require REA or the Snapmaker GUI to run.

REA 6.7.0 and checksum-verified Node 24.22.1 are isolated under ignored tooling.
The follow-up adds checksum-verified Rizin 0.9.1 through REA's child-scoped
`REA_RIZIN_COMMAND`, without changing product dependencies or global tools.
Focused GUI and native inspection worked; full doctor/Ghidra readiness is not
claimed. Native byte/call evidence and pinned source establish the selected WCP
camera transport statically, while installed camera compatibility remains
unverified. See the [camera report](docs/research/2026-10-24-camera.md).

## D008 — Verify effects and reconcile uncertain outcomes

Date: 2026-10-24 · Status: Implemented for preparation/uploads; controls remain proposed

Hash the selected file, download and verify uploaded bytes, bind preparation to
the selected mapping/materials, and check the actual printer outcome. Preserve
operation receipts across restarts. After a timeout or disconnect, reconcile
state before retrying; never blindly replay a start.

Represent accepted, rejected, unavailable, and unknown outcomes distinctly.
Print acceptance, first-layer success, print completion, and physical quality
are separate claims requiring separate evidence.

The upload implementation persists an atomic claim/inflight record before POST,
uses one receipt database/OS lock per printer, and never repeats a dispatched
POST. Reconciliation after expiry can establish byte transfer without renewing
preparation or authorizing start. Lost-reply reconciliation explicitly marks
response flags unconfirmed. Bad acknowledgment/hash results are terminal. See
the [upload contract](docs/research/2026-10-24-uploads.md) for exact limits.

## D009 — Traffic-light roadmap and honest project state

Date: 2026-10-24 · Status: Confirmed

Use a table with 🟢 / 🟡 / 🔴 status in [ROADMAP.md](ROADMAP.md), as requested by
the owner. Keep compact evidence and next actions in [PROJECT_STATE.md](PROJECT_STATE.md),
implemented changes in [CHANGELOG.md](CHANGELOG.md), and detailed contracts in
the [design draft](docs/superpowers/specs/2026-10-24-snapmaker-u1-mcp-design.md).
Do not promote a proposal or an untested capability to complete through a docs update.

## D010 — Strict read-only first milestone and conservative results

Date: 2026-10-24 · Status: Implemented engineering choice within owner scope

Expose exactly three parameterless, typed read tools. Use fixed HTTP routes and
known objects, bounded uncompressed raw reads with total deadlines, no redirects,
environment proxies or automatic retries, and no stale fallback cache. Return
partial/unknown values rather than coercing missing evidence. Suppress SDK/HTTP
diagnostics that can echo raw requests; publish fixed safe errors and selected
fields only. Do not expose raw exception messages, filenames, machine paths or
RFID card identifiers. Preserve the full future scope as unimplemented.

## D011 — Camera session changes deferred during this investigation

Date: 2026-10-24 · Status: Confirmed operating scope for this session

The owner's request requires read-only live checks. No camera start/stop or
printer mutation was issued. Inspect the pinned GUI artifact and isolated REA
results without executing target code. Keep installed-printer camera transport/
authentication compatibility and session ownership unresolved until demonstrated
through the ordinary supported flow; static findings alone do not authorize or
validate a session implementation.
This constraint continues through the focused native follow-up: its only fresh
printer interaction was the read-only capability tool.

## D012 — Separate native camera evidence from session guarantees

Date: 2026-10-24 · Status: Confirmed investigation boundary; implementation deferred

The selected native WCP branch publishes camera JSON-RPC through TLS MQTT. Its
camera handlers rebuild parameters without the GUI's optional `clientid`.
Preserve that branch-specific finding rather than substituting generic WebSocket
assumptions or treating a GUI client ID as proof of camera ownership.

Keep the GUI's 300-second monitoring policy, MQTT keepalive, native callback
timeouts, certificate lifetime, and server camera expiry distinct. None of the
first three establishes the latter two. Require installed-firmware evidence for
credential provisioning, ownership, expiry and noninterfering cleanup before
camera tools. A bounded passive trace is the next validation probe; it does not
authorize creating/closing a session or prove the remaining lifecycle contracts.

## D013 — Restricted preparation and simulator-only upload acceptance

Date: 2026-10-24 · Status: Implemented engineering choices within owner scope

Add two typed file tools while leaving print controls/camera absent. Preparation
has no printer effects; uploads require local enablement, default false. The
owner limited all hardware checks in this chat to reads, so source contracts
and simulated success do not establish installed upload compatibility.

Fail closed on unresolved macros, transforms, commands and job requirements.
Inspect every consumption entry and executable heater/move command. Use an
opened-file-handle check on Windows/Linux to reject symlink/junction escapes,
bounded streaming passes and worker-thread inspection. Enforce the documented
conservative envelope; do not claim those limits were measured on the printer.
Operator-configured nozzles are explicitly attested, not sensor evidence.

The pinned upload code supplies a narrow `print=false` no-start/no-queue contract
and raw HTTP-201 JSON envelope; no further REA/native work was needed for this
contract. Ordinary Orca U1 macros remain unresolved and rejected, rather than
inferred safe from names. Hardware upload acceptance and firmware-matched macro
analysis are required before broad profile support. Do not remove safety/setup
commands to bypass validation. This supersedes D010's exactly-three-tool
inventory only; its read behavior, redaction and data boundaries remain.

## D014 — Match the release artifact before extending the U1 dialect

Date: 2026-10-25 · Status: Implemented engineering choice within owner scope

The vendor artifact for observed firmware `2.0.0.205_20260914173503` matches
pinned release source, rather than public main, for the inspected contracts.
Live macro/configuration reads agree with relevant executable definitions; they
are not live-code attestation. Record identities and limits in the
[Orca U1 report](docs/research/2026-10-25-orca-u1-gcode.md).

Accept bounded M73, auxiliary fan P2, M204 S, acceleration-only named settings,
and absolute XY IJ arcs only after explicit in-file G17. Bound the full circle
and endpoint without allocating segments; retain every-tool consumption/thermal
checks and conservative limits. Policy 2 prevents old preparations/inflight
receipts from being promoted under new validation; no uncertain POST is replayed.

Complete normal profiles remain blocked by state-dependent startup, cleaning,
toolchange offsets, flow/bed calibration, object transforms, camera side effects
and metadata ambiguity. Do not whitelist macros as no-ops, strip them or infer
hardware safety from the source match. This follow-up authorizes only live reads;
hardware upload/start/camera acceptance still needs separate authorization.

## D015 — Preserve unknown state across firmware-owned setup

Date: 2026-10-25 · Status: Implemented engineering choice within owner scope

Matched-source tracing establishes that selection can move the carriage and
replace XYZ offsets; even a same-head shortcut depends on hardware state. Forget
XYZ after every T and active tool/E after full G28, which can reselect a physical
head. Require canonical tool names and integer heater selectors. Explicit XYZ
only reestablishes G-code-space inspection, not machine-space safety.

Positive heater targets participate in declared material/feed requirements.
Reject aliases in the requested physical mapping until physical heater/E tracking
can support them; per-logical tracking must not certify a heater cooled through
another logical index. Policy 3 invalidates old-policy undispatched preparations
and uncertain-result promotion without replaying a POST.

No macro is newly accepted. Saved flow, physical feed/calibration demand,
homing/mesh, pause/object/end and camera effects require a bound runtime-evidence
contract before broader acceptance. The
[focused report](docs/research/2026-10-25-startup-toolchange.md) records the
transitive paths and limits. No live request, camera action, configuration change
or hardware acceptance occurred in this follow-up; full milestones remain partial.

## D016 — Bind reported runtime evidence without promoting it to motion safety

Date: 2026-10-25 · Status: Implemented engineering choice within owner scope

Extend the existing status query with bounded coordinate, per-head offset/park
and active-mesh reports. Keep selection separate from gripping, reported offset
separate from configured/backup calibration, and global origin separate from
per-head origins. Project exact types, signed finite vectors, fixed enums and
bounded mesh/profile digests; keep missing fields unknown and raw config private.

Policy 4 binds this normalized subset to preparation and upload receipts, with
repeated equal runtime observations bracketing material/job reads and ordered
source times. Recheck before dispatch and around remote byte verification;
persist the reconciliation time watermark. Refuse policies 1–3 for dispatch or
uncertain-result promotion without replaying an upload. Matching HTTP snapshots
are not atomic or proof against intervening changes and stale peer data.

The live seven-object GET establishes field availability on one observed setup.
It does not attest running code, calibration provenance, every transform or any
firmware-owned motion. No macro/stock export is newly accepted, uploads remain
disabled, and hardware acceptance remains pending. See the
[runtime report](docs/research/2026-10-25-runtime-evidence.md).

## D017 — Bind exclusion reports without inferring transform lifecycle

Date: 2026-10-25 · Status: Implemented engineering choice within owner scope

Extend existing status/runtime receipts with a fixed three-field exclusion
projection, bounded private label hashes/counts, current-object presence and
reported region state. Explicit null and absent current-object fields have
different meanings. Policy 5 refuses policy-1–4 dispatch/uncertain promotion;
existing repeated-read/time/receipt/no-replay checks remain.

Matched source shows an empty exclusion list can coexist with an installed
transform, and region state can lag object markers. Installation stays null;
neither membership nor matrices attest chain order, effective mesh fade/lookup/
ZFADE or calibration provenance. The inspected supported status/dump contracts
do not expose those decisive values. No guessed endpoint/field or G-code probe
substitutes for a supported read. See the
[transform lifecycle report](docs/research/2026-10-25-transform-evidence.md).

One read-only GET confirmed the exclusion field forms. No command/stock export
is newly accepted, uploads remain disabled and all hardware/control/camera
acceptance stays pending. The owner explicitly authorized review, commit and
push on main for this one-time continuation; no branch/PR is needed.

## D018 — Bind head reports without inventing physical extrusion evidence

Date: 2026-10-25 · Status: Implemented engineering choice within owner scope

Policy 6 adds all-head reported nozzle diameter/volume type, pressure advance,
smoothing and queue-name evidence to existing repeated receipt binding. Used
reported diameters must agree with both file requirements and operator nozzle
attestation. Policies 1–5 cannot dispatch/promote uncertain operations; no upload
is replayed. Missing/malformed values remain unknown and prevent preparation.

Persisted nozzle labels do not measure physical nozzles; current advance does
not establish saved calibrator K. The matched constructor attaches its own trapq
without updating the null queue name, so neither null nor a name attests actual
attachment. Preserve that unknown alongside hidden feed/thermal demand and the
unresolved transform/provenance contract. No command/export is newly accepted.
See the [head report](docs/research/2026-10-25-head-extrusion-evidence.md).

Reuse the historical seven-object response and verified source/artifact for
this contract; no new live query is necessary. The owner authorized this immediate
development/review/commit/push on main and the existing recurring loop. That does
not authorize hardware mutations. Advance pause/end callback/job-flag research
next instead of repeating unsupported transform or head snapshots.

## D019 — Require explicit unpaused evidence without certifying resume/end

Date: 2026-10-25 · Status: Implemented engineering choice within owner scope

Project only `pause_resume.is_paused` through the existing status/runtime reads.
Treat it as independent of print statistics and virtual-SD activity. True blocks
idle; missing/null/malformed reporting stays unknown and cannot establish idle.
Policy 7 binds this report through existing repeated observations and refuses
policy-1–6 dispatch/uncertain promotion without replay. Historical model defaults
exist only for receipt deserialization. Preserve every prior guard.

Supported status does not expose saved restore state or the internal pause-request/
SD-pause flags. Source tracing establishes motion, heat/feed/flow/cleaning and
camera-dependent pause/resume/end/cancel branches, plus configurable layer/error/
idle callbacks. Reported job flags and macro variables do not attest template
identity, transitive effects or action completion. Commented client-hook examples
are not installed callback execution. See the
[pause/end report](docs/research/2026-10-25-pause-end-evidence.md).

One focused read-only GET confirmed boolean false; no mutation or hardware control
acceptance occurred. No command/export is newly accepted. Continue with the
supported machine/action-state provider and transition hooks rather than repeating
pause/head/mesh snapshots. Readiness remains incomplete and the recurring loop
continues under the owner's review/commit/push authorization on main.

## D020 — Treat machine/action labels as independent idle vetoes

Date: 2026-10-26 · Status: Implemented engineering choice within owner scope

Project only machine_state_manager.main_state/action_code through both runtime
queries. Normalize exact integer enum members from the verified artifact; keep
missing/malformed/future values unknown. Positive idle requires both IDLE codes
alongside prior checks; either recognized nonzero report independently blocks
idle, including when the other is unknown. No inferred pair compatibility table.
Policy 8 binds both reports and refuses policy-1–7 dispatch/uncertain promotion,
preserving historical terminal results, every prior guard and no-replay behavior.

The provider exposes mutable labels, not transition locks/history, rule/hook
identity, post-hook success or drained physical queues. Label/history update
precedes post-hooks; SD/statistics/pause sequencing remains separate. One passive
GET confirmed both integer zero forms, not safe control or hardware acceptance.
See the [machine/action report](docs/research/2026-10-26-machine-state-evidence.md).
No new command/export/tool is accepted; uploads remain disabled. Continue with
job flags/read-time effects and their consumers instead of repeated snapshots.
Readiness remains incomplete; live mutations need separate authorization.

## D021 — Bind reported job preferences without certifying their effects

Date: 2026-10-26 · Status: Implemented engineering choice within owner scope

Project only eight boolean preferences, two four-boolean physical-head arrays
and fixed entanglement sensitivity into runtime evidence. Preserve the three
existing materials fields in the fixed provider projection. Missing/malformed
reports stay unknown, both boolean values are valid, and current preferences
do not establish activity, completed actions or calibration/camera results.
Policy 9 binds all reports and refuses policy-1–8 dispatch/uncertain promotion
without replay, preserving all prior guards and historical terminal results.

The supported getter refreshes in-memory filament existence/edit reports before
returning a shallow dictionary. Projection does not suppress this behavior;
independent sensor/feed checks remain required. Reset/reprint and hidden second
job parameters remain distinct from action completion. The time-lapse local bit
can clear after a failed stop and does not establish server cleanup or ownership.
See the [job report](docs/research/2026-10-26-job-flag-evidence.md).

No live request or new tool/command/export acceptance; uploads remain disabled.
The transform/provenance diagnostic gap is unchanged. Continue distinct camera
RPC/failure-lifecycle research from saved artifacts, without starting/stopping
cameras. Readiness remains incomplete under the owner's ongoing main/review/
verification/commit/push authorization.
