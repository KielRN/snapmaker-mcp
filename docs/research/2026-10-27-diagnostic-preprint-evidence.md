# Small diagnostic preparation and ordinary upload workflow

Date: 2026-10-27 UTC. Baseline: `bf94ac54a2437b56b94e15f03411c7f2698df23e`.
Documentation and ignored local workflow only; no runtime, test, dependency,
receipt-policy or MCP-tool change. Uploads remain disabled in bridge defaults
and local configuration. This report does not establish print readiness.

## Current read evidence and scope

At **20:19:02 UTC**, the existing MCP status tool reported Klipper ready, idle,
print state complete, inactive virtual SD and no blocking exceptions. All heater
targets were zero; nozzles were 28–29 °C and the bed 26 °C. Materials reported
mapping `[1,2,3,4]` for the first four logical entries and completed feed loading,
enabled positive toolhead sensors and PLA on all four physical tools. RFID was
used only as identity. These are time-specific reports, not bed clearance or
attestation of installed physical nozzles.

The existing connected vendor Device view still displayed a usable chamber
image. No new pairing, Play, light toggle or separate camera API session was
selected in this round. Subsequent local Prepare/Preview navigation is not
evidence of camera cleanup, ownership or frame freshness.

D026 authorizes selecting and preparing a very small diagnostic, including its
ordinary upload workflow. No fresh human installed/clear-bed confirmation exists.
No start, heater/motion, calibration or persistent printer configuration action
was selected. Changing local slicer nozzle/process/filament selections does not
attest or change the installed hardware.

## One model, two intact exports

One external-workspace coupon has nominal dimensions **10 × 10 × 0.6 mm**, volume
60 mm³ and 12 triangles. Plate 1 is intended to use physical tool 1 / T0 with
white SnapSpeed PLA and a 0.4 mm nozzle. Exact local paths, generated remote
destination and operation identity are retained only in ignored local receipts.
Geometry and slicing remain outside the bridge.

| Evidence | Portable OrcaSlicer 2.4.0 | Native Snapmaker Orca 2.4.0 |
| --- | --- | --- |
| Bytes | 42,542 | 49,972 |
| Lines | 1,276 | 1,286 |
| Slicer time estimate | 36 s | 37 s |
| Declared consumption, mm | `[41.42]` | `[40.92,0,0,0]` |
| Declared consumption, g | `[0.12]` | `[0.12,0,0,0]` |
| Material / nozzle cardinalities | 1 / 4 | 4 / 4 |
| First bridge refusal | `job_requirements` | `unsupported_command` at `EXCLUDE_OBJECT_DEFINE` |
| Explicit bed target | 60 °C | 65 °C |

Portable SHA256:
`9268b69d856d6f894f48f193916d045618c12787cf18346b6991cc23117a4599`.
Native SHA256:
`5cc8a731668d55083580e02994f86f5e277a9ee9d4af1fb0283c80bf339a9ea7`.

The native UI confirmed the nominal geometry. Its stock 0.20 mm standard process
uses a 0.25 mm first layer; the three layer tops are 0.25/0.45/0.65 mm. Do not
confuse the nominal model height with the sliced top height. The native file has
four PLA, 1.75 mm filament and 0.4 mm nozzle entries. Its model extrusion uses
T0; zero entries on the other tools do not prove zero startup-macro effects.

The external G-code analyzer returned only the leading scalar consumption from
the native file. Inspection of the original text was necessary to retain all four
entries. No analyzer or external integration code was changed. This sample's
aligned native arrays do not resolve the three original ambiguous exports.

Both original exports retain their normal setup and safety commands. Both call
all four `SM_PRINT_AUTO_FEED` / `SM_PRINT_FLOW_CALIBRATE` paths, additional-head
preheat macros, bed-mesh calibration and time-lapse commands. Explicit nozzle
targets reach 220 °C; these are not a cap on hidden macro thermal demand. Native
startup also contains a purifier command. The portable profile explicitly
enables automatic leveling and time lapse; the native file does not contain those
same explicit enable lines. Current job preferences are not effective file-bound
parameters and cannot prove that these macro paths will be inactive.

A text-only scan of explicit G0/G1 operands found native X 85–185, Y 1–140.79 and
Z 0.2–5 mm; portable X 10–140.29, Y 3–140.79 and Z 0.2–5 mm. These are operand
extrema, not interpreted paths, calibrated machine bounds or bounds on homing,
toolchanging and macro-owned movement. Full startup time/material/thermal/motion
demand remains unknown. The 36/37 s and 0.12 g estimates must not be presented as
complete physical-job budgets. Neither file is authorized to start on this evidence.

## Observed vendor send sequence

The native slice was exported locally without editing its bytes. The top-level
Print action opened a filename dialog offering separate **Upload** and **Upload
and Print** choices. The Upload choice opened a second page, titled **Pretreat
the uploaded content**, showing the exact selected destination, the connected
LAN printer, an estimate below one minute, 0.12 g, 0% progress and a **Send** button.
The first Upload click is therefore not a transfer-completion receipt.

A premature GET verification before final Send found no matching remote file
and stopped with an assertion failure. No Upload action was replayed. The
existing unsubmitted Send page was reinspected and retained the same destination
and operation. A separately reviewed one-use final-Send gate rechecked the
original local bytes, source-time ordering, idle/thermal/material/runtime/job
identity and destination absence under the same private OS lock. It durably
marked the first final-Send intent before permitting any final click, retaining
the original 600-second expiry. Reentry is refused even if the JSON inspection
copy is lost; SQLite FULL synchronization is the durable authority.

The computer-use tool refused a coordinate click over the embedded WebView
process. After target activation and a fresh screenshot, its single documented
retry was also refused. A keyboard-focus observation did not expose a confirmed
Send focus. The operator was asked to perform the one final Send on the existing
Upload-only page; no control was bypassed or substituted with a crafted POST.

The owner replied **"sent"** after the operator-assistance request. At
**20:31:29 UTC**, bounded GET verification had found all **49,972 remote
bytes identical** to the native local export at the exact generated G-code-root
destination. Surrounding ready/idle, zero-target, inactive-SD, runtime/material/
mapping/feed and prior-job-identity evidence stayed consistent with the opening
observations and source times were ordered. Verification completed within the
original expiry, the SQLite receipt was saved and the local OS lock released.
The UI returned to Device view with its ordinary chamber image; no new viewer or
light action was selected. The remote file remains present; no deletion occurred.

This is operator-assisted vendor transfer plus installed readback evidence. No
MCP preparation or upload acceptance is implied by ordinary vendor behavior.
The UI path does not expose captured `print_started=false` / `print_queued=false`
response flags. Idle/inactive-SD observations cannot establish that complete
wire envelope or exclude later actions by another client.

## Remaining acceptance and next action

Transfer is complete for this exact file; do not upload it again to repeat the
same evidence. Inspect the saved file's ordinary preprint options next, without
submitting a start or setter as a probe. Keep the exact receipt and repeat fresh
bounded remote-hash/state checks only when required for a subsequent authorized
step. For a future uncertain outcome, reconcile only through reads of the same
destination; a missing file cannot exclude a late write. Keep stock files intact
and bridge uploads disabled.

Before any later start, establish the selected file's effective job options and
complete setup demand within D026, obtain fresh human confirmation that the plate
is installed and clear, then repeat mapping/feed/nozzle/thermal/hash/state checks.
Do not run calibration or enable a camera path to test whether preferences gate
it. Do not repeat closed source investigations without a specific changed-evidence
question. Full control, camera lifecycle and hardware print acceptance remain gaps.

Software/review/integration checks are recorded in the
[execution ledger](../superpowers/plans/2026-10-27-diagnostic-preprint-evidence.md).
