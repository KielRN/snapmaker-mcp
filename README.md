# Snapmaker U1 MCP

A local Python/stdio MCP bridge for a Snapmaker U1. Repository:
[KielRN/snapmaker-mcp](https://github.com/KielRN/snapmaker-mcp).

The bridge implements three read tools plus `u1_prepare_print` and
`u1_upload_print` for restricted plain G-code. Reads have installed-U1 evidence;
preparation and uploads have local simulator/real-MCP verification only. Uploads
are disabled by default. This is unreleased development software, `0.1.0.dev0`.
Print controls and camera tools remain unimplemented.

## Setup

Python 3.11+ and [uv](https://docs.astral.sh/uv/) are required for these commands.
They were exercised on Windows with Python 3.11.14 and 3.13.12. From this checkout:

```powershell
uv sync --locked --extra dev
New-Item -ItemType Directory -Force .local | Out-Null
Copy-Item config.example.json .local/config.json
```

Edit the ignored local JSON to set your trusted LAN printer origin. The example
uses a deliberately nonworking `.invalid` host. The origin must be HTTP(S), with
no credentials, path, query, or fragment. `U1_PRINTER_URL` can override the JSON
origin; `U1_API_KEY` optionally supplies the normal `X-Api-Key` header. Credentials
belong in a secret store/local environment, not in JSON examples or Git.

```powershell
$env:U1_CONFIG_FILE = (Resolve-Path .local/config.json).Path
uv run --locked --extra dev python tools/check_connection.py
```

This launches the actual stdio server, initializes MCP, checks its five-tool
inventory, calls only the three read tools, and prints normalized JSON. It makes
no printer changes. The updated checker was exercised against the simulator;
prior three-tool live evidence remains historical. A raw launch is:

```powershell
uv run --locked python -m snapmaker_u1_mcp
```

The raw launch waits for an MCP client on stdin; stdout is reserved for MCP.
Invalid setup exits with a fixed stderr message. SDK/HTTP diagnostic logging is
suppressed because it can echo private payloads; tool failures carry sanitized
error codes and guidance.

## Connect an MCP client

Configure stdio with this checkout's absolute `.venv` Python executable, arguments
`-m snapmaker_u1_mcp`, and `U1_CONFIG_FILE` pointing to the absolute ignored JSON.
The editable install makes the working directory immaterial. Tool arguments
cannot substitute an endpoint. Preparation accepts an absolute local file path
only under configured allowed roots.

The local Codex entry `snapmaker_u1` was added. Its exact configured command/env
were used for successful MCP initialize/list/calls. A subsequently discovered
`u1_capabilities` tool also succeeded in the active chat. Reload MCP or start a new
client session if the running chat has not discovered the new tools. Remove the
entry in Codex MCP settings when no longer wanted. Stop its clients before
removing this checkout's `.venv`; no printer cleanup/configuration is needed.

## Tools and interpretation

Call the three read tools with `{}`. Discovery includes typed input/output schemas.

| Tool | Result |
| --- | --- |
| `u1_capabilities` | Observed firmware/Moonraker identity, HTTP/object inventory, implemented/future tools, unresolved camera support. |
| `u1_status` | Klipper/print state, virtual SD, saved pause, machine/action codes, job preferences, progress, temperatures, exceptions and bounded reported coordinate/selection/offset/mesh/exclusion evidence. |
| `u1_materials` | Four physical tools, T0–T3/API names, 32 logical mapping slots, job-use flags, RFID identity/color, feed/toolhead sensor evidence, loaded state. |
| `u1_prepare_print` | Read-only inspection of one allowed file/plate and fresh mapping/material/feed evidence; expiring durable receipt. |
| `u1_upload_print` | No-start/no-queue upload of a prepared hash, exact returned-path check and remote download SHA256 verification; simulator-verified only. |

Results include the observation window, source event time when available,
outcome, errors, and data. `ok` means reported read fields were understood, not
that an action is safe. `partial` retains usable data and marks missing evidence
as null/unknown. `unavailable` covers failed reads, `rejected` includes error
objects on HTTP 200, and `unknown` covers unexpected normalization failures.
No cached success is returned after failure. Failed outcomes set MCP `isError`;
partial results do not.

Physical tools are one-based. `logical_to_physical[0]` is logical T0's one-based
physical tool. Unused mapping defaults do not imply material use; `used_by_job`
is the current physical job-use flag. Klipper ready can coexist with printing.
Idle requires an inactive print state, inactive virtual SD, explicitly false
`runtime_evidence.pause_resume_is_paused`, ready Klipper and known clear exceptions.
A true saved-pause report is busy independently of the statistics label. Missing,
null or malformed pause reports prevent a positive idle result. This bit does
not establish safe resume, saved-coordinate validity or completion of pause/end
actions. See the [pause/end report](docs/research/2026-10-25-pause-end-evidence.md).
Idle also requires exact integer zero (IDLE) for both
`runtime_evidence.machine_main_state` and `machine_action_code`. Recognized
nonzero activity independently makes the printer busy; absent/malformed/unfamiliar
codes remain unknown. These mutable labels do not establish transition/hook or
physical completion, loaded code or drained motion queues. See the
[machine/action report](docs/research/2026-10-26-machine-state-evidence.md).
Separate HTTP requests are not atomic. Exception levels
2/3 are classified as blocking from pinned public source; active hardware fault
semantics remain untested. Raw messages, filenames, machine identity/paths, RFID
card UIDs, and camera credentials are omitted.

`runtime_evidence` distinguishes the selected object from park/grip reports,
per-head reported offsets from the global homing origin, and toolhead/G-code
positions from one another. Mesh profile/matrices are represented by digests
and dimensions. Missing/malformed fields stay unknown; a populated mesh and
zero offsets do not establish an applied transform or calibrated safety.
The fixed exclusion projection adds private label hashes/counts, current-object
presence and reported region state. Explicit null current object is known absence;
missing/malformed fields remain unknown. Empty exclusions do not prove transform
removal; region state can lag a marker. Installation stays null. Unexposed base
positions, per-head origins, effective fade/lookup/ZFADE, calibration provenance
and complete transform chain remain unestablished. See the
[runtime evidence report](docs/research/2026-10-25-runtime-evidence.md) and
[transform lifecycle report](docs/research/2026-10-25-transform-evidence.md).

Each head also reports nozzle settings, pressure advance/smoothing and bounded
queue-name evidence. These values bind receipts, including on unused heads.
Nozzle settings are persisted software reports; used heads must agree with both
the file and operator nozzle attestation. An explicit null queue name is known
unnamed reporting, not proof of stepper detachment: the matched constructor
attaches a queue without updating that name. Current advance does not establish
saved calibration K. Actual trapq attachment and hidden feed thermal/consumption
demand remain unknown. This subset was confirmed in the earlier saved response;
no new hardware query was needed. See the
[per-head extrusion report](docs/research/2026-10-25-head-extrusion-evidence.md).

`runtime_evidence.job` reports eight boolean job preferences, four-head flow/
end-unload flags in physical T0–T3 order and fixed entanglement sensitivity.
Missing/malformed reports stay unknown; preferences do not establish completed
calibration, effective protection, feed/end actions or camera ownership/cleanup.
The fixed provider projection retains existing material fields. Its getter
refreshes in-memory filament existence/edit reports before returning a shallow
copy; projection does not avoid that refresh. Independent feed/sensor loading
checks remain required. No new live request was needed for this source-backed
contract. See the [job report](docs/research/2026-10-26-job-flag-evidence.md).

`loaded` requires an enabled positive toolhead sensor plus present/positive feed
module reporting completed loading without a feed error. An enabled negative
toolhead sensor gives `not_loaded`; missing, disabled, contradictory, or
transitional evidence gives `unknown`. RFID describes identity only. Sensor
reports do not establish physical inspection or suitability for a future job.

## File preparation and uploads

Keep slicing in the separate OrcaSlicer integration. Only a restricted plain
`.gcode` dialect is accepted, including bounded absolute XY arcs after explicit
G17, M73 progress, P2 auxiliary cooling and acceleration forms. Stock U1 profiles
contain unresolved machine macros and remain rejected. All eight inspected normal
exports still fail validation; no full stock pattern is newly supported.
Do not strip their setup/safety commands to make a
file pass. See the [upload contract and evidence](docs/research/2026-10-24-uploads.md)
and [firmware-matched G-code report](docs/research/2026-10-25-orca-u1-gcode.md)
for supported forms, artifact identities, exact blockers and remaining acceptance.
Arc bounds include the entire supporting circle and can reject a partial sweep
near a boundary. Acceleration is capped at 10,000 mm/s²; arbitrary named settings,
other planes, R arcs, partial homing and coordinate transforms remain rejected.

Tool selection forgets XYZ and requires explicit absolute X/Y/Z before further
motion; absolute E still needs a reset. Full G28 forgets active tool/E because
the U1 override can reselect a physical head. Positive heater targets require
declared consumption and material/feed evidence even without E. Requested
physical mappings must be unique; aliases return `mapping_ambiguous`. T0–T3
command names must be canonical and heater T selectors must use integer syntax.
These checks bound G-code-space inspection, not calibrated machine-space or
firmware-owned homing/toolchanger motion. The
[startup/toolchange report](docs/research/2026-10-25-startup-toolchange.md)
traces hidden effects and the runtime evidence needed before broader acceptance.

For preparation, edit the ignored configuration: set `allowed_roots` to existing
absolute directories, add `receipt_db` as an absolute SQLite path in an existing
private directory (normally `.local/`), and set `nozzle_diameters` to four
operator-verified physical nozzle sizes in millimeters. Nozzle sizes are local
attestations, not sensor readings. The example leaves file access unconfigured
and `enable_uploads=false`. Do not enable hardware uploads until separately
authorized acceptance; no live upload was performed for this milestone.

`u1_prepare_print` requires `operation_id` (canonical UUID4), `local_path`, `plate`
(1–1000), and `logical_to_physical` (one to four one-based physical tools, one per
declared logical filament entry). The mapping must match the current printer.
Plate labels this exported file; it does not extract a plate from 3MF. Every mm/g
consumption entry and nonzero E move participates in requirements, even when the
first entry is zero. Used tools need matching material and completed feed/sensor
evidence. Preparation also requires idle state and known prior job identity.
It now requires the supported coordinate-evidence subset without missing or
inconsistent fields. Repeated runtime reads bracket material/job evidence; their
normalized values must agree and source times must be ordered. The receipt
includes that observation window and reported subset, with explicit non-atomic
semantics. Fresh homing or physical gripping is not asserted by preparation.

`u1_upload_print` requires a **new** UUID4 `operation_id` and the returned
`preparation_id`. When enabled, it rereads the file hash and current printer
evidence, checks expiry, uploads with `print=false`, validates root/path/flags,
then downloads and hashes the bytes. No job parameters, start or queue commands
are sent. Each preparation permits at most one upload claim. Neither tool grants
print authorization; there is no start tool.

Defaults: 32 MiB file cap, 500,000 lines, 8,192 raw bytes per line, 30 seconds per
file request and 600-second receipt life. `max_gcode_bytes` can be 1 KiB–128 MiB,
`upload_timeout_seconds` can be >0–120, and `receipt_ttl_seconds` can be 1–600.
All coordinators for one printer must share one journal/lock. Keep them private
and persistent across restarts; moving/deleting them defeats local idempotency.
Path-handle checks support Windows and Linux `/proc/self/fd`; other platforms
refuse file access until an equivalent verifier is implemented.

Repeat an upload with the **same arguments and operation ID** after an uncertain
outcome. It reconciles only by reads, never another POST. A missing remote file
stays unknown because a late write is possible. Matching bytes can reconcile a
lost reply; `response_flags_confirmed=false` records that its acknowledgment was
not observed. `verified` establishes observed bytes, not hardware acceptance or
print suitability. Terminal results retain their original observation and expiry;
repetition is historical, not a fresh check. Bad acknowledgments/hash mismatches
stay terminal. Use the supported app to investigate; no automatic delete occurs.

## Verification and recovery

```powershell
uv run --locked --extra dev pytest -q
uv run --locked --extra dev ruff check .
uv run --locked --extra dev ruff format --check .
uv build
```

The suite exercises the actual stdio process and a local HTTP simulator, including
mapping/feed failures, partial objects, HTTP-200 errors, authentication,
timeouts/disconnects, no stale success, malformed MCP input, redaction, redirects,
and oversized/compressed responses. File tests cover canonical paths/junctions,
all-tool consumption, actual heater/move commands, mapping/material changes,
SHA mismatch, HTTP-200 errors, races, expiry, duplicate IDs, process serialization,
cancellation and restart reconciliation. Tests need no printer or credentials.
No MCP hardware upload/control acceptance tests have run.

Receipt policy 12 invalidates policy-1–11 preparations for new uploads. Old inflight
receipts with a policy mismatch remain unknown and never resend a POST; retain
the journal and investigate with read-only checks in the supported app.
Runtime evidence is rechecked before dispatch and around remote byte verification;
changes or backwards source times block dispatch/promotion. Repeated equal HTTP
reads cannot exclude intervening changes, stale peer data or other-client races.
Each completed status/material/closing-runtime read with a valid source timestamp
advances the reconciliation journal before later validation or asynchronous reads.
Failures and cancellation therefore retain observed history across restart;
older evidence stays unknown and the POST is never replayed. Invalid timestamps
cannot advance it; recording a time does not make failed evidence acceptable.
See the [observation fix ledger](docs/superpowers/plans/2026-10-28-reconciliation-observations.md).
Exclusion reports participate in the binding; known reports do not establish
the running transform chain. Reported nozzle/advance/smoothing/queue values also
participate; missing fields prevent preparation, used nozzle conflicts return
`nozzle_mismatch`, and all-head changes prevent dispatch/promotion. The restricted
G-code dialect is unchanged. Saved pause is also bound across both runtime reads;
its missing/changed report blocks dispatch or uncertain-result promotion. Pause,
resume, cancel, end and configurable layer callbacks remain unsupported commands.
Machine/action reports bind both runtime observations too; missing or changed
codes prevent dispatch/promotion. Transition/hook completion remains unknown.
Job preferences bind both reads as well; missing/malformed/changed reports block
dispatch/promotion. Their values do not change idle classification or authorize
macros. Nested reprint/second job parameters and action completion remain unknown.

Reads use fixed routes/objects, disable environment proxies/redirects, request
uncompressed data, reject other encodings, and cap raw bytes and total request
duration. JSON evidence and upload acknowledgments reject duplicate object keys
at every depth, including equal values and escaped spellings. Ambiguous reads
return `invalid_response`; ambiguous upload acknowledgments stay terminal
`unknown` with `upload_contract`, without confirming flags or replaying POST.
Firmware-shaped labels retain configured credential/host and length filters.
See the [response-boundary correction](docs/superpowers/plans/2026-10-28-json-evidence.md).
Defaults are 256 KiB and five seconds per request. On failure, check
local config, normal authentication, printer availability and firmware, then
repeat the read. Reads have no automatic retries; file transactions follow the
durable recovery rules above and uploads require explicit local enablement.

## Camera and remaining scope

REA 6.7.0/Node 24.22.1 are isolated under ignored tooling. The tested installer is
`powershell -File tools/setup_rea.ps1`; it changes neither global Node nor agent
registrations. The follow-up used checksum-verified, isolated Rizin 0.9.1 through
REA to inspect seven native functions and additional GUI excerpts. Static evidence
traces the native WCP camera branch to TLS MQTT and identifies a dropped camera
`clientid` and a 300-second GUI renewal/close policy. Installed camera behavior,
server expiry/ownership, decryption/freshness and safe cleanup remain unverified.
No camera session was opened or closed. Full REA doctor/Ghidra readiness is not
claimed. The [camera report](docs/research/2026-10-24-camera.md) records artifact
identities, exact native/source anchors, tooling limits and the smallest passive
validation probe. Camera tools remain unimplemented.

The saved firmware [camera RPC report](docs/research/2026-10-26-camera-rpc-evidence.md)
adds server-side evidence: monitor stop can acknowledge without cleanup,
time-lapse stop can detach work, and coarse server status lacks ownership,
expiry, freshness and completed cleanup. These are static limits; no camera
session or new live request was made and no camera API is newly supported.

The [worker continuation](docs/research/2026-10-26-camera-worker-evidence.md)
finds shared timer expiry and destructor/join paths, but no externally observable
owned-session cleanup contract. False flags can precede resource release;
compiled timing and notification timestamps do not prove cleanup or fresh images.
The independent [feed report](docs/research/2026-10-26-feed-resolution-evidence.md)
records table fallback/rollback that can discard material-temperature lookups.
Neither investigation broadened accepted files/tools; current receipt policy
also includes the cancellation fix described above.

The [flow-calibration report](docs/research/2026-10-27-flow-calibration-evidence.md)
establishes finite local measurement counts and field-specific parameter
precedence. Effective parameters/provenance, full material/thermal/time demand
and completed cleanup remain unreported. No status provider is exposed by the
inspected calibrator; static counts do not authorize calibration or stock files.

The [hidden-parameter report](docs/research/2026-10-27-job-parameter-evidence.md)
traces parser fallback, array roles and reset/reprint lifetime. The setter can
assign hidden tables before filename checks; persistence only enqueues separate
writes. Neither acknowledgment nor visible preferences establishes file-bound
effective parameters. Consumer nozzle-entry-zero indexing does not resolve the
three ambiguous export headers. No runtime policy or file acceptance changed.

The [desktop/metadata report](docs/research/2026-10-27-desktop-metadata-evidence.md)
closes the upstream source trace: server submission preserves independent raw
array lengths, while client preprint display can pad/truncate consumption and
fall back to a first nozzle. These fallbacks are not bridge validation rules.
The first ordinary LAN connection attempt found the U1 but expired waiting for
touchscreen authorization, with Binding rejected. An attended follow-up now
reaches the connected Device view and a usable camera image after enabling the
chamber light. That is vendor-UI evidence; bridge transfer, print/control and
camera ownership/freshness/cleanup acceptance remain incomplete.

A later [diagnostic round](docs/research/2026-10-27-diagnostic-preprint-evidence.md)
prepared one small external coupon and exercised the ordinary Upload-only path.
That path opens a second Send page; after operator assistance, bounded readback
matched all 49,972 native-export bytes and SHA256 while the printer stayed idle
with inactive virtual SD. This establishes vendor transfer evidence only. The
file is still rejected by the bridge; setup macros leave its complete physical
demand unresolved. No print started and no fresh installed/clear-bed confirmation
was supplied during that transfer round. Later human installed/clear-bed
confirmation was recorded for the diagnostic; it is historical, time-specific
clearance. The saved file's ordinary preprint page has now been inspected without
submission. It displays tool 1, PLA/0.12 g and flow/time-lapse/leveling controls,
without effective parameter readback or complete startup bounds. No Send/start
was selected. A later return to Device showed Camera not on; no viewer stop was
selected and cleanup is unverified. Reuse the receipt/file; do not repeat transfer
or use option setters/start as probes. A supported passive effective-parameter/
startup diagnostic remains the concrete hardware prerequisite.

Future controls must retain per-plate authorization and fresh human confirmation
of an installed, clear bed. The owner now delegates selection of very small
diagnostic prints and permits normal desktop UI use, including observation;
see D026 in [DECISIONS.md](DECISIONS.md) and the workflow in [AGENTS.md](AGENTS.md).
This does not establish new hardware or MCP acceptance. Bed-clear statements are
time-specific; later plates need fresh clearance. Slicing stays in the separate
OrcaSlicer integration.
This bridge introduces no firmware/calibration/configuration changes, cloud
dependence, or automatic product-order dispatch.

## Project documents

| Document | Purpose |
| --- | --- |
| [PROJECT_STATE.md](PROJECT_STATE.md) | Evidence, blockers, next actions. |
| [ROADMAP.md](ROADMAP.md) | Traffic-light milestones. |
| [DECISIONS.md](DECISIONS.md) | Confirmed choices and proposals. |
| [CHANGELOG.md](CHANGELOG.md) | Actual changes and release status. |
| [AGENTS.md](AGENTS.md) | Agent and printer operating rules. |
| [Design](docs/superpowers/specs/2026-10-24-snapmaker-u1-mcp-design.md) | Full scope and future safety contracts. |
| [Milestone plan](docs/superpowers/plans/2026-10-24-read-milestone.md) | Implementation record. |
| [Read evidence](docs/research/2026-10-24-read-contracts.md) | Live observations, pinned source, software checks. |
| [Camera report](docs/research/2026-10-24-camera.md) | Tooling, artifact identity, findings and gaps. |
| [Upload evidence](docs/research/2026-10-24-uploads.md) | Restricted dialect, source identity, receipt/recovery semantics and hardware gaps. |
| [Upload plan](docs/superpowers/plans/2026-10-24-verified-uploads.md) | Focused implementation and verification record. |
| [Orca U1 G-code report](docs/research/2026-10-25-orca-u1-gcode.md) | Version-matched firmware evidence, bounded numeric additions and stock-profile blockers. |
| [Orca validation plan](docs/superpowers/plans/2026-10-25-orca-u1-validation.md) | Focused follow-up execution and acceptance limits. |
| [Startup/toolchange report](docs/research/2026-10-25-startup-toolchange.md) | Transitive source effects, validation hardening and missing runtime evidence. |
| [Startup/toolchange plan](docs/superpowers/plans/2026-10-25-startup-toolchange-validation.md) | Focused hardening, review and verification record. |
| [Runtime evidence](docs/research/2026-10-25-runtime-evidence.md) | Observed coordinate/selection/mesh fields, policy-4 binding and remaining provenance/transform gaps. |
| [Runtime evidence plan](docs/superpowers/plans/2026-10-25-runtime-evidence.md) | Focused collection, normalization and receipt verification ledger. |
| [Transform lifecycle report](docs/research/2026-10-25-transform-evidence.md) | Exclusion field evidence, policy-5 binding and unsupported lifecycle/provenance claims. |
| [Transform evidence plan](docs/superpowers/plans/2026-10-25-transform-evidence.md) | Focused continuation, review and verification ledger. |
| [Per-head extrusion evidence](docs/research/2026-10-25-head-extrusion-evidence.md) | Nozzle/advance/queue report semantics, policy-6 binding and hidden-demand limits. |
| [Per-head extrusion plan](docs/superpowers/plans/2026-10-25-head-extrusion-evidence.md) | Focused implementation, review and verification ledger. |
| [Pause/end evidence](docs/research/2026-10-25-pause-end-evidence.md) | Independent saved-pause status, policy-7 idle/receipt checks and unresolved callback/end dependencies. |
| [Pause/end plan](docs/superpowers/plans/2026-10-25-pause-end-evidence.md) | Focused implementation, review and verification ledger. |
| [Machine/action evidence](docs/research/2026-10-26-machine-state-evidence.md) | Conservative activity reports, policy-8 binding and transition/SD/hook limitations. |
| [Machine/action plan](docs/superpowers/plans/2026-10-26-machine-state-evidence.md) | Focused implementation, review and verification ledger. |
| [Job preference evidence](docs/research/2026-10-26-job-flag-evidence.md) | Fixed job reports, policy-9 binding and getter/reset/reprint/feed/end/camera limits. |
| [Job preference plan](docs/superpowers/plans/2026-10-26-job-flag-evidence.md) | Focused implementation, review and verification ledger. |
| [Camera RPC evidence](docs/research/2026-10-26-camera-rpc-evidence.md) | Client correlation/timeouts and saved server stop/status/cleanup limits. |
| [Camera RPC plan](docs/superpowers/plans/2026-10-26-camera-rpc-evidence.md) | Focused static investigation, review and verification ledger. |
| [Camera worker evidence](docs/research/2026-10-26-camera-worker-evidence.md) | Shared renewal/expiry, normal exit/destructor and external cleanup limits. |
| [Feed resolution evidence](docs/research/2026-10-26-feed-resolution-evidence.md) | Per-key fallback, rollback and missing effective parameter provenance. |
| [Worker/feed plan](docs/superpowers/plans/2026-10-26-camera-worker-evidence.md) | Focused continuation, independent review and verification ledger. |
| [Flow-calibration evidence](docs/research/2026-10-27-flow-calibration-evidence.md) | Parameter precedence, finite search counts and unresolved full-demand/provider evidence. |
| [Flow-calibration plan](docs/superpowers/plans/2026-10-27-flow-calibration-evidence.md) | Focused source investigation, review and verification ledger. |
| [Hidden job-parameter evidence](docs/research/2026-10-27-job-parameter-evidence.md) | Parsing/fallback, array roles, reset/reprint lifetime, asynchronous persistence and unresolved file provenance. |
| [Hidden parameter plan](docs/superpowers/plans/2026-10-27-job-parameter-evidence.md) | Focused source investigation, independent review and verification ledger. |
| [Desktop/metadata report](docs/research/2026-10-27-desktop-metadata-evidence.md) | Attended connection/camera observation, matched metadata producer and distinct client display fallbacks. |
| [Desktop/metadata ledger](docs/superpowers/plans/2026-10-27-desktop-metadata-evidence.md) | Focused UI/source continuation, review, verification and acceptance limits. |
| [Diagnostic preprint report](docs/research/2026-10-27-diagnostic-preprint-evidence.md) | External coupon, native/portable export differences and operator-assisted vendor transfer with exact remote bytes. |
| [Diagnostic preprint ledger](docs/superpowers/plans/2026-10-27-diagnostic-preprint-evidence.md) | Review, fresh checks, one-use UI receipt and remaining acceptance. |
| [Observation retention ledger](docs/superpowers/plans/2026-10-28-reconciliation-observations.md) | Policy-11 failure/cancellation/restart correction and verification record. |
