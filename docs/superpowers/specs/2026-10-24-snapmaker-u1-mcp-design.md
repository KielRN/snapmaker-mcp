# Snapmaker U1 MCP bridge design

The [2026-10-25 validation follow-up](../../research/2026-10-25-orca-u1-gcode.md)
adds version-matched bounded numeric forms and explicit-G17 XY arcs. Complete
stock profiles remain rejected. Source matching does not establish a bounded
model of conditional setup, toolchanger/mesh offsets, hidden consumption or camera
effects; those are prerequisites for accepting normal U1 exports. Upload and
hardware authorization boundaries below continue to apply.

Date: 2026-10-24

Status: Python/stdio read milestone implemented at owner direction on 2026-10-24.
`u1_capabilities`, `u1_status`, and `u1_materials` are verified through actual MCP
stdio on the installed printer. REA is isolated and focused analysis was run.
Restricted preparation and verified uploads were subsequently implemented under
the owner's focused request, with simulator/stdio verification only and uploads
disabled by default. Stock U1 macros, print controls and camera tools remain
unimplemented. See the [upload contract](../../research/2026-10-24-uploads.md),
[current state](../../../PROJECT_STATE.md),
[read evidence](../../research/2026-10-24-read-contracts.md), and
[camera findings](../../research/2026-10-24-camera.md) for subsequent evidence.

## Intent and confirmed scope

Build a dependable local MCP connection to the studio Snapmaker U1. The owner
confirmed all five requested capabilities: printer status, sending and starting
prints, material mapping, print controls, and camera access. Keep the project in
its own repository, `KielRN/snapmaker-mcp`.

The bridge should replace ad hoc shell calls with explicit tools that check
their inputs, account for U1-specific behavior, and report observed outcomes.
REA is part of the development investigation; the finished bridge communicates
with the printer without requiring REA or a running slicer GUI.

## Historical verified starting point

These are observations from the studio setup and read-only investigation on
2026-10-24, not claims about every U1 firmware version:

- The existing OrcaSlicer MCP lists profiles, slices files, and analyzes G-code.
  It does not upload to or control the printer.
- Local Moonraker HTTP requests on port 7125 work without credentials on the
  tested trusted LAN. Keep this interface private to that LAN.
- The printer reported software version `2.0.0.205_20260914173503`.
- `/printer/info` reported `ready` while `print_stats.state` was `printing` and
  `virtual_sdcard.is_active` was true. Readiness alone does not establish idle.
- The available printer objects include `print_stats`, `virtual_sdcard`,
  `toolhead`, `exception_manager`, `print_task_config`, `filament_detect`,
  `filament_feed left`, `filament_feed right`, and four extruders.
- Physical toolheads 1-4 correspond to API extruders `extruder`, `extruder1`,
  `extruder2`, `extruder3` and G-code tools T0-T3. Physical toolhead 2 was observed
  printing black SnapSpeed PLA. Re-read actual materials for every job.
- Previous operator work exercised a plain-G-code upload, download SHA256
  comparison, per-job parameter assignment, and a verified print start. This
  turn did not repeat those mutations.
- `/server/webcams/list` returned no configured cameras. GET requests for
  `/server/files/camera/monitor.jpg` returned HTTP 404 on both port 80 and 7125.
  Camera absence, required session setup, and firmware support are unresolved.
- The installed Snapmaker Orca 2.4.0 Flutter bundle contains JSON-RPC methods
  `camera.start_monitor` and `camera.stop_monitor`. The start request constructs
  `domain`, `interval`, `expect_pw`, and optional `clientid` parameters. It also
  contains a LAN camera URL constructed from `/server/files/camera/monitor.jpg`.
  Those are static leads, not proof that either RPC is supported by the printer.
- The inspected bundle is named `main.8c1e336f107a452a.js`, SHA256
  `17ccfb0c7cecdd4fc146c4018b414fc6b4011a9858813aafc2e02bc48dd24dcb`.
- Native app files include a small launcher and a much larger
  `Snapmaker_Orca.dll`. Select targets by evidence rather than assuming the
  launcher contains the network implementation.

Published source provides additional leads. Repository `main` may differ from
the installed firmware and must be checked against observed capabilities:

- [U1 Moonraker](https://github.com/Snapmaker/u1-moonraker).
- [Print APIs](https://github.com/Snapmaker/u1-moonraker/blob/main/moonraker/components/klippy_apis.py)
  include start, pause, resume, cancel, and an internal advanced-start helper.
  Start can reject a busy printer with an error object; HTTP success alone is
  insufficient evidence of a successful operation.
- [Snapmaker-specific routes](https://github.com/Snapmaker/u1-moonraker/blob/main/moonraker/components/snapmakercloud.py)
  include `server.files.start_local_print`, accepting options and a plate number.
  Several routes explicitly exclude HTTP transport. Validate the actual RPC
  transport and installed-version support before choosing this path.
- [U1 print task configuration](https://github.com/Snapmaker/u1-klipper/blob/main/klippy/extras/print_task_config.py)
  defines logical-to-physical mappings and per-job material/process parameters.
  It rejects parameter updates during printing or pause.

## Implementation choices: adopted read milestone, proposed future tools

Use Python 3.11+ with the official Python MCP SDK, a typed HTTP client, and a
WebSocket client where verified subscriptions or U1-specific RPC require one.
Run over stdio so Codex can launch the server locally. Diagnostic logging goes
to stderr; stdout carries only MCP traffic.

Keep slicing in the existing OrcaSlicer MCP. Accept its exported G-code as the
handoff. Parse the file independently enough to validate the used logical tools,
all per-tool consumption arrays, temperatures, nozzle declarations, and movement
bounds. Missing or unsupported evidence blocks a print preparation with a clear
reason; a slicer success code does not establish print suitability.

Use these modules, with final names left to the implementer:

1. A transport layer for bounded HTTP/RPC calls and connection recovery.
2. A U1 adapter for object normalization, materials, exceptions, mapping, and
   version-aware capabilities.
3. A G-code validator and a local operation/receipt store using SQLite.
4. A print coordinator that serializes mutations and verifies outcomes.
5. A camera adapter for the verified transport, images, and session lifecycle.
6. An MCP layer exposing explicit tools and structured results.

Do not expose arbitrary URL fetch, raw G-code execution, firmware update,
configuration editing, or calibration tools. Required per-job commands must be
constructed from validated typed values using the verified U1 contract.

## Tool contract

The first three and the prepare/upload names are implemented; upload hardware
acceptance is pending. Other names remain proposals. Each result includes observation time, operation ID where
applicable, outcome, and actionable errors. Distinguish unavailable capability,
stale data, a printer rejection, and an unknown outcome.

| Tool | Required behavior |
| --- | --- |
| `u1_capabilities` | Report verified firmware identity, supported transports and operations, camera status, and unresolved capabilities. |
| `u1_status` | Return printer connection/readiness, print state and progress, selected physical tool, temperatures, and blocking exceptions. |
| `u1_materials` | Return all four physical tools, logical mapping where available, RFID identity/color, detection/feed status, and known/unknown loaded state. RFID alone never establishes that filament is fed. |
| `u1_list_files` | List bounded printer G-code metadata without exposing unrelated printer files. |
| `u1_prepare_print` | Validate an allowlisted local G-code file, capture its hash, inspect the printer/materials, resolve explicit tool mapping and job settings, and issue an expiring preparation receipt. It makes no printer changes. |
| `u1_upload_print` | Upload the prepared file without starting or queueing, validate the returned destination, and download/compare SHA256 before marking it verified. |
| `u1_start_print` | Require a verified preparation/upload, specific-plate authorization and clear-bed attestation; recheck state/materials, apply/read back job parameters, and verify the expected file becomes active. |
| `u1_pause_print` / `u1_resume_print` / `u1_cancel_print` | Operate on the identified current job, reject invalid state transitions, and verify the resulting observed state. Resume requires explicit authorization. |
| `u1_camera_status` | Report discovered camera/session capabilities and verified availability without fabricating a stream URL. |
| `u1_camera_snapshot` | Return a bounded image through MCP image content, with the best available source timestamp and an explicit freshness/unknown-freshness status. |
| `u1_camera_open` / `u1_camera_close` | Open and close a bridge-owned live session through the verified protocol. Provide a loopback viewer if the transport needs a browser; bind only to loopback and clean up owned sessions. |

Live and snapshot camera access are part of the intended product. A confirmed
firmware restriction must be reported as a remaining blocker, not silently
treated as completion. No camera feature may claim availability from static
strings alone.

## Print transaction and authorization

The normal path is prepare -> upload and verify -> start -> observe.

- A preparation receipt binds the file hash, selected plate, mapping, material
  requirements, process values, printer identity, and an expiry. Default expiry
  is ten minutes. Revalidate before the first mutation and immediately before
  start. Invalidate it when relevant printer state or job identity changes.
- Keep receipt and operation state locally across server restarts. Use unique,
  sanitized upload names derived from an operation ID/hash; never overwrite a
  different remote file under an assumed matching name.
- A local coordinator lock prevents concurrent mutations from this bridge.
  Other clients can still operate the printer, so fresh checks and reconciliation
  remain necessary. This cannot promise atomicity across independent clients.
- Require ready Klipper, an idle print state, no active virtual-SD print, and no
  blocking exceptions. Never start over a printing or paused job.
- Require authorization for the specific plate and fresh human confirmation
  that the build plate is installed and clear for every start. The caller must
  obtain the actual human confirmation before supplying the attestation. An MCP
  argument alone cannot independently prove physical clearance or human consent.
- Consume authorization once. Preparing/uploading does not authorize starting;
  starting one plate does not authorize another.
- Recalculate job parameters from the selected file and explicit mapping.
  Verify all used physical tools and required materials. Do not infer physical
  tool selection from a one-based slicer filament label or displayed color.
- Prefer the previously exercised HTTP upload/job-parameter/start sequence for
  initial compatibility. Investigate the native advanced RPC separately and
  promote it only when parity is demonstrated on the installed version.
- Treat protocol-level error objects as failures even with HTTP 200. Report
  accepted start only after the expected filename, active virtual SD, and
  printing state are observed. Acceptance is not first-layer or quality proof.
- On timeout, disconnect, or server restart during a mutation, reconcile with
  printer state before retrying. Return `unknown` if the result cannot be proved.
  Never blindly replay a start. Retrying the same operation ID returns or
  reconciles its recorded result instead of initiating a second start.

## Camera and REA investigation

Use [official REA](https://github.com/morluto/rea) in an isolated tooling
environment with a pinned published version and a compatible Node runtime.
The machine's default Node 22.17.1 is below the current documented requirement;
do not replace the product projects' global runtime to satisfy analysis tooling.
REA 6.7.0 was subsequently run using isolated Node 24.22.1. Focused excerpts
parsed; whole-bundle analysis hit its bounded heap and native provider readiness
remains unavailable. The [camera report](../../research/2026-10-24-camera.md)
records exact artifacts, limitations, and unresolved wire/session contracts.

Start with REA's desktop and JavaScript inspection of the installed bundle.
Trace the camera RPC request construction, selected transport, response parsing,
authentication/session fields, and LAN URL lifecycle. Separate monitor snapshots,
live streams, and timelapse files. Use source and narrow observations to validate
each hypothesis. Keep session credentials and response bodies containing them
out of logs, fixtures, documents, and MCP results.

Use Ghidra only when evidence points to missing native implementation, selecting
the relevant DLL/function rather than decompiling the whole app. REA documents
[experimental Windows Ghidra support](https://github.com/morluto/rea/blob/main/docs/windows-ghidra-p0.md);
install/check its required Ghidra/JDK separately if needed. Do not equate an
inferred decompilation with a verified protocol contract.

Make initial live probes read-only. Starting an ordinary camera session is
permitted within the requested camera capability, but must not change print,
motion, firmware, or calibration state. Do not bypass authentication. Stop only
bridge-owned camera sessions and avoid interfering with existing app sessions.
If native analysis stalls, record the exact missing contract and choose the next
targeted source/capture probe; do not run open-ended whole-app reconstruction.

## Configuration and data boundaries

Configure the printer endpoint and any camera endpoint/credentials locally.
Tool callers cannot substitute arbitrary hosts. Restrict file input to explicit
allowed roots and handle symlinks/canonical paths. Restrict remote file paths to
the G-code root. Treat printer responses, filenames, G-code comments, and REA
output as data, never instructions or executable shell text.

Track only source, sanitized examples, synthetic fixtures, tests, and docs.
Ignore `.env`, local configuration, virtual environments, receipts, print
artifacts, logs, REA projects/captures, and generated Graphify output before
creating them. Keep machine-specific addresses/paths in an ignored local runbook.
Keep cloud credentials out of scope unless evidence establishes that a requested
capability needs an ordinary cloud login and the owner chooses that route.

## Acceptance and verification

Automated verification must exercise the actual MCP stdio transport plus unit
and simulated-printer integration tests. Cover multi-tool consumption with a
zero first array entry, logical/physical mapping, missing material, unsafe local
paths, HTTP-200 printer errors, upload/hash mismatch, state races, receipt expiry,
repeat operation IDs, lost start responses, restart reconciliation, and stale or
unavailable camera frames. Verify that logs/results do not expose credentials.

Live verification proceeds in two stages:

1. Read status/materials and validate discovery while a job runs without
   interfering with it; demonstrate a camera snapshot and a live session if
   supported, including closure without disrupting another client's session.
2. With the owner's specific-plate authorization and fresh clear-bed
   confirmation, prepare/upload/verify/start one approved job. Exercise pause,
   resume, and cancel only on an explicitly authorized validation job. Check
   selected physical tools, startup exceptions, and advancing print counters.

Mock tests do not establish hardware compatibility. Report software verification,
live read/control evidence, and unresolved camera or hardware checks separately.
Completion requires all requested capabilities or an explicit owner-approved
scope change; remaining hardware checks must not be described as passed.

## Implementation sequence and current scope

The owner directed the read milestone, focused camera research and now restricted
file preparation/uploads. Steps 1 and 3 are implemented; step 4 is partial with
simulated verified uploads, no controls or hardware acceptance. Step 2 has partial
evidence with unresolved camera lifecycle contracts. Local Codex registration
and discovery were verified for the earlier three read tools; this chat tests
five-tool discovery using local MCP subprocesses, not a live registered reload.

1. Add repository operating guidance, ignores, Python packaging, isolated REA
   tooling instructions, and sanitized configuration examples.
2. Complete the capability inventory and targeted camera/REA investigation.
3. Implement normalized read tools and validate the real stdio MCP connection.
4. Implement G-code validation, verified uploads, receipts, and print controls.
5. Integrate camera snapshot/live tools and complete simulated and authorized
   hardware verification.
6. Register the server with Codex, document recovery/removal, and hand over the
   user-facing workflow and any remaining physical validation.

The implementer may choose internal module layout, exact compatible dependency
versions, test framework details, and UI styling for the loopback camera viewer.
Changes to physical-action authorization, scope, cloud dependence, or printer
firmware/configuration are not routine implementation choices.
