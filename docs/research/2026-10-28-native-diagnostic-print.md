# Owner-directed native diagnostic print

Date: 2026-10-28 UTC. This is normal vendor-UI hardware evidence, not acceptance
of stock G-code by the bridge or an implementation of an MCP start/control tool.

## Authorization and exact job

The owner explicitly directed a small print now, confirmed current clearance,
and separately confirmed that the build plate was installed. Exact statements
and receipt times are retained in the ignored local handoff. This authorizes one
existing diagnostic plate; it is not standing physical clearance for another.

Reused the previously transferred, unedited native coupon: nominal
**10 × 10 × 0.6 mm**, plate 1, physical **tool 1 / T0**, white SnapSpeed PLA,
0.4 mm nozzle and 1.75 mm filament. Sliced layer tops are 0.25/0.45/0.65 mm.
The native export is **49,972 bytes**, SHA256
`5cc8a731668d55083580e02994f86f5e277a9ee9d4af1fb0283c80bf339a9ea7`.
Declared model consumption is **40.92/0/0/0 mm**, **0.12/0/0/0 g**, with a
**37-second** slicer estimate. These do not bound complete startup consumption,
time or macro-owned motion. Purpose: observe ordinary native start, progress and
completion for a small single-tool model. No slicing or geometry was added here.

## Checks and one native start

Fresh supported reads established ready Klipper, idle print state, inactive
virtual SD, explicitly unpaused state, known empty exceptions and zero heater
targets. All four heads reported loaded PLA and 0.4 mm nozzles; current logical
T0–T3 mapped to physical tools 1–4. Ordered status/material/status observations
agreed on the reported runtime subset. Local handle/root checks and bounded
remote download matched the original bytes exactly before start.

The normal connected Device view's Local Files card opened the expected generated
filename and coupon thumbnail. File information displayed tool 1 and PLA/0.12 g.
Flow calibration, time-lapse and auto-leveling circular controls appeared empty;
they were left unchanged. Subsequent supported status continued to report those
three preferences false. Display/preference evidence does not expose every
effective hidden parameter. No separate firmware, persistent configuration,
calibration or safety controls were selected; original setup commands remained
intact.

A durable single native-start intent was recorded under the existing private
vendor-UI journal/OS lock before one **Send** click at approximately **12:02:30
UTC**. No crafted start/setter/G-code POST was used. The UI showed loading and
returned to Device. At **12:02:55 UTC**, supported reads observed the exact
expected filename, `printing`, active virtual SD, three layers, tool 1 heating
and bed target 65 °C, with no exceptions. The native start was not replayed.
Filename and status reads are separate HTTP observations, not an atomic receipt.

The ignored one-use preflight helper checks its JSON intent for reentry and also
persists the receipt in SQLite. It does not independently fence reentry from the
journal if that JSON copy is removed. Preserve both and never rerun the helper;
the evidence supports one actual click without replay, not a tested general
start-idempotency implementation.

Normal camera Play and chamber light controls were used for observation. After
navigating back from Local Files, the viewer showed Camera not on; a normal Play
action restored a usable chamber image. No direct camera API or viewer-stop
command was issued. Ownership, frame timestamps and completed cleanup remain
unverified. Camera visibility is separate from human physical clearance.

## Outcome and limits

The exact job has an observed accepted native start, model-layer progress and
printer-reported completion:

| Observation (UTC) | Expected filename | Print state / SD | Other evidence |
| --- | --- | --- | --- |
| 12:02:55 | Matches | Printing / active | Startup, layer 0/3; tool 1 target 140 °C, bed target 65 °C; no exceptions. |
| 12:04:33 | Matches | Printing / active | Startup, layer 0/3; tool 1 130/130 °C, bed 63/65 °C; no exceptions. |
| 12:06:29 | Matches | Printing / active | Layer 1/3; tool 1 220/220 °C, bed 65/65 °C; no exceptions. |
| 12:06:54 | Matches | Printing / active | Layer 3/3; same targets; no exceptions. |
| 12:07:24 | Matches | Complete / inactive | Progress 1.0, layer 3/3, main/action 0/0, unpaused, no exceptions, all nozzle and bed targets zero. |

At the completion observation, tool 1 was cooling at 178 °C and the bed at 63 °C.
Printer `print_duration` was **49.20 s**. About five minutes separated the native
click and completion observation; that includes startup and the observation
interval, and is not an exact measured physical-job duration. The 37-second
slicer estimate was not the complete elapsed time.

Compared with preflight, the final reported tool-1 pressure advance changed from
0.026 to 0.02 and the reported probed/mesh matrix digests changed, while the mesh
profile digest stayed equal. These are observed runtime changes; cause,
persistence and calibration provenance are not established by the reports.

Camera showed setup/model movement and the subsequent parked-head/lowered-bed
view. It did not provide a close, reliable view of the finished coupon. At
**12:17:45 UTC**, the owner's subsequent statement **"Coupon inspected. Approved"**
and supplied photograph were recorded. This closes the requested human inspection
and approval for this coupon. The photograph shows a small square coupon on the
textured plate; no measured dimensions or separate fit result were supplied.
Original photo bytes and an approval receipt remain ignored local evidence.
No pause/resume/cancel was requested or tested. Do not start a
second plate: remove finished parts and obtain new installed/clear-bed confirmation
and task authorization as applicable first.

The bridge still rejects this intact file at `EXCLUDE_OBJECT_DEFINE`; uploads
remain disabled locally and by default. Policy 12, five MCP tools and all file,
material, thermal, hash, expiry and no-replay guards are unchanged. The missing
effective-parameter/transform/startup contracts still block broad bridge stock-file
acceptance; they do not replace the owner's explicit authorization for this
ordinary native diagnostic. This observation does not certify general control
semantics, pause/resume/cancel recovery, camera lifecycle or full readiness.

Ignored receipts: `.tmp/diagnostic-start-20261028/` holds current authorization,
preflight/start intent, single-click record, timestamped normalized observations
and review/verification records; the shared journal remains private in `.local/`.
See the [prior preparation/transfer report](2026-10-27-diagnostic-preprint-evidence.md)
for the original file analysis and vendor upload evidence.
