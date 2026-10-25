# Firmware-matched Orca U1 G-code investigation — 2026-10-25

## Result and scope

Normal, intact Orca U1 exports **remain blocked**. This follow-up establishes
version-matched source identities and adds only bounded numeric forms: M73
progress, auxiliary cooling P2, M204 S, acceleration-only SET_VELOCITY_LIMIT,
and absolute XY IJ arcs with G17. These work in otherwise supported synthetic
programs. They do not make any of the eight inspected normal exports acceptable.
No setup, safety, camera, calibration or cleaning command was removed or ignored.

The printer was accessed only through read-only capability, printer-info and
configuration GETs. No live preparation/upload, camera start/stop, print control,
configuration or calibration operation occurred. Uploads remain disabled locally
and by default. Test uploads target a loopback simulator only.

## Evidence identity and limits

Fresh capability observation at **2026-10-25 10:10:41 UTC** reported printer
`2.0.0.205_20260914173503`, Moonraker `2.0.0`, five implemented tools and uploads
disabled. A separate GET read the active configuration; it does not prove which
Python bytes the running process loaded or provide an atomic runtime snapshot.

The [vendor upgrade artifact](https://public.resource.snapmaker.com/firmware/U1/U1_2.0.0.205_20260914173503_upgrade.bin)
has 216,715,726 bytes and computed SHA256
`e6269eb0f1d9e8da74173e9da6350a14b18dd2fe5c4e8f2cabc48b0cdaf2aad7`.
Its filename/version agrees with the observed firmware. This is artifact identity,
not a signed attestation that the live filesystem is identical. The SquashFS 4
root starts at byte 22,655,718 and reports 177,137,172 bytes used. Extraction
read only selected Klipper Python/configuration files, never executed target
code and never installed or flashed firmware.

Public main was insufficient. The [2.0.0 release PR](https://github.com/Snapmaker/u1-klipper/pull/13)
was open/unmerged when queried; its pinned head is
`bc271fb351f8c3ad84300e652e46fd93c53b9de1`. Each selected downloaded source
was verified against its Git blob, then compared byte for byte with the matching
file extracted from the vendor image. Fourteen Python files and the release's
`printer.cfg` and `fluidd.cfg` matched. Relevant identities:

| Source in pinned release | Git blob (matches artifact bytes) |
| --- | --- |
| `klippy/gcode.py` | `f57bb794c281ffd27a5c354837ea72f22d171219` |
| `klippy/toolhead.py` | `63c7b0b286bf68deec0c4306e76b41cdfbd98946` |
| `klippy/kinematics/extruder.py` | `6978d8a1b33c4b767e0f0cd783a2b50b6ed115dd` |
| `klippy/extras/gcode_move.py` | `3627a74d67cc75d23ce9cedf2c20ec398380225b` |
| `klippy/extras/gcode_arcs.py` | `b48ecd52d89ef2041e63f8cc97c0e4c6132c2269` |
| `klippy/extras/fan.py` | `0964ab0ae537f7b65562402248c821b542dd9f72` |
| `klippy/extras/homing_xyz_override.py` | `d6f3c3531828608184b1231f8350ceeca791cf23` |
| `klippy/extras/flow_calibrator.py` | `43ec0b5b82378def1a5a58c027c705cfb8ffdf08` |
| `klippy/extras/print_stats.py` | `433dcb62ca4aedd7336b12fa77641ad979b1a95e` |
| `klippy/extras/print_task_config.py` | `ba2fe4115b9bd22ce736bcd776a56f5cf199d987` |
| `klippy/extras/bed_mesh.py` | `e2ebe448886327c780640f7e2ec5aea77ca9ae84` |
| `klippy/extras/exclude_object.py` | `f4dea918e02666c1bd886a70693b62a9242bd705` |
| `klippy/extras/timelapse.py` | `58fe59bb2a1a464453d8dd922085efa5b614ebf4` |
| `klippy/extras/defect_detection.py` | `2a5ce634883730157ac8116a4f7a16c928944307` |
| `lava/printer.cfg` | `c3e7b94678665e23cc83aa960108eaf0feb640fc` |
| `lava/fluidd.cfg` | `f158f3c171403df29b31d15aa879f4457a71f9fe` |

The artifact's `display_status.py` was read directly; SHA256 is
`335cebf3434b68d7a67b9595cfa33832fcc6a8580078cdbdcabd658275be7c0d`.
No public-main identity is substituted for it. For the active macro comparison,
87 available bodies were compared to release configuration after trimming
indentation, blank and comment-only lines: 86 matched exactly. The sole textual
difference, `SET_PRINT_STATS_INFO`, consists of two removed inline comments
after pause calls. Its executable sequence agrees; no behavioral divergence was
demonstrated. Live fan configuration maps P2 to the auxiliary cavity fan and
arc resolution is 0.5 mm. These are time-specific configuration observations.

Analysis used a separate ignored Python 3.11 environment with
`dissect-squashfs==1.12`, `dissect-cstruct==4.7`, `dissect-util==3.24` and
`backports-zstd==1.8.0`. Product environments/dependencies were unchanged. REA
was unnecessary: the specific missing contracts were available as Python source
in the matched artifact. Raw GETs, manifests, source, extraction and export
inventories remain ignored under `.tmp/u1-profile-research/`; local filenames,
geometry, machine identifiers and installation paths are not tracked.

## Representative exports

Eight existing local exports were inspected without reslicing or modifying them.
They are representative single-active-tool files, including a zero first
consumption entry with later T1 use; they are **not** a multicolor/toolchange
acceptance corpus. Raw filenames and geometry remain private. Stable aliases:

| Alias | Bytes / lines | SHA256 | Current first rejection |
| --- | --- | --- | --- |
| 01 | 2,015,394 / 71,569 | `f9fe9ece25e8cd628a3742ba7949a71617586b32adf08e45a214bd93740ab240` | `unsupported_command` |
| 02 | 2,134,416 / 74,728 | `ad926a8ea153f9a935a1d263f2438d8ad0cb9a2bca45d0998fffcd93c5c0ca3f` | `unsupported_command` |
| 03 | 952,110 / 34,426 | `c248f20c80d1529cef119aee595394cee9b8bec6b5854e232ea70260c4a9e8c6` | `unsupported_command` |
| 04 | 2,692,654 / 98,752 | `8e56ec2131249fff110d5d73624462fedc2a4707f31b0d2cf926e0349939cda3` | `unsupported_command` |
| 05 | 10,316,133 / 363,690 | `830e2d578ef32e822dacb06bc1d5842d2f8961c20afa6b7f3253f8105a56c90b` | `job_requirements` |
| 06 | 10,316,133 / 363,690 | `3220c66943049d9e23891dca30fec07c0f0c6dd642e8568ee893a69431a3e805` | `job_requirements` |
| 07 | 10,316,133 / 363,690 | `f862f15471a6ddcb1a5f6b9080fc35c1135bc9fe4de7057056b800cfc1954c90` | `job_requirements` |
| 08 | 2,092,287 / 75,236 | `82b149cbc935ff796f32d50cf7b676c9a294290c503489609e6543e75df9ad01` | `unsupported_command` |

05–07 declare one consumption/material entry but four nozzle entries. The
logical-filament versus physical-nozzle relationship needs explicit validation;
the parser does not replicate entries or guess unused-tool requirements. Other
files encounter `EXCLUDE_OBJECT_DEFINE` first. Every original remains rejected.

Across this corpus, the baseline lacked these **36 command names** (parameters
also matter):

```text
BED_MESH_CALIBRATE DEFECT_DETECTION_DETECT DEFECT_DETECTION_DETECT_BED
DEFECT_DETECTION_START DEFECT_DETECT_NOODLE_FIRST DETECT_BED_PLATE
EXCLUDE_OBJECT_DEFINE EXCLUDE_OBJECT_END EXCLUDE_OBJECT_START
FINELY_CLEAN_NOZZLE_STAGE_1 FINELY_CLEAN_NOZZLE_STAGE_2
G17 G2 G3 M204 M73 MOVE_TO_DISCARD_FILAMENT_POSITION
MOVE_TO_XY_IDLE_POSITION_EXTRUDER PRINT_END PRINT_START
ROUGHLY_CLEAN_NOZZLE ROUGHLY_CLEAN_NOZZLE_WITH_DISCARD
SET_PRESSURE_ADVANCE SET_PRINT_AUTO_BED_LEVELING SET_PRINT_STATS_INFO
SET_PURIFIER_MODE SET_TIME_LAPSE_CAMERA SET_VELOCITY_LIMIT
SM_PRINT_AUTO_FEED SM_PRINT_CHECK_SWITCH_EXTRUDER SM_PRINT_EXTRUDER_PREHEAT
SM_PRINT_FLOW_CALIBRATE TIMELAPSE_START TIMELAPSE_STOP TIMELAPSE_TAKE_FRAME
WAIT_CHAMBER_TEMP
```

Already recognized names also had unsupported forms: `M106 P2 S178`,
`M106 P2 S0`, `G28 X Y`, `G28 Z`, `G28 Z I140 J140`. Only fan P2 is added here.
Normal geometry uses both G2/G3 and G17; acceleration examples include
`M204 S10000` and `SET_VELOCITY_LIMIT ACCEL=5000 ACCEL_TO_DECEL=2500`.

## Established effects and remaining blockers

| Phase / commands | Established source effects | Why complete-profile validation remains blocked |
| --- | --- | --- |
| `PRINT_START` | `fluidd.cfg:193`: applies stored flow K on all physical tools, resets job macro variables, disables motors, resets E and speed multiplier. | Stored flow parameters and initial machine state are not bound/modelled by current preparation. This is not an inert marker. |
| T0–T3 and `SM_PRINT_CHECK_SWITCH_EXTRUDER` | `extruder.py:1330–1818`: logical mapping, physical pick/park, retry branches, optional homing, saved modes/E restoration and active XYZ offsets. Macro checks all job-used physical tools, not merely the visible first tool. | Existing T recognition only tracks logical E requirements; it does not validate the entire toolchanger path or calibrated machine coordinates. Do not broaden this into stock-profile acceptance. |
| Preheat / auto-feed / flow calibration | `fluidd.cfg:876–905`, `print_stats.py:255`, `flow_calibrator.py:627`: used-tool/job flags select physical tools; A0 bypasses logical mapping inside macros; feeding/extrusion/calibration depend on runtime filament data. | Hidden purge/calibration/retraction, temperatures, feed amounts and optional replenishment must be included for every physical tool. Slicer mm/g arrays alone cannot bound those effects. |
| Discard / rough / fine cleaning | `fluidd.cfg:179,788–864`: discard movements, extrusion, relative XYZ, contact probing; behavior varies by selected head. | Need a state/coordinate model of the complete transitive call chain and probe outcomes; no fixed safe coordinates are inferred from names. |
| G28 and bed calibration | `homing_xyz_override.py`, active override settings and `bed_mesh.py`: homing/probing, Z hops, templates and mesh transformation. | Partial homing, I/J probe positions, calibrated offsets and mesh compensation cannot be treated as ordinary linear XYZ. Full G28 retains its prior firmware-owned/unknown-final-position limitation. |
| Temperatures / extrusion | `extruder.py:1267` maps T by default; macros can use A0 and material-derived temperatures. | Added numeric forms preserve explicit heater limits and M109 wait checks; those do not establish hidden macro temperatures, actual temperature or material suitability. |
| `SET_PRINT_STATS_INFO` | Active/release macro calls a configurable pause command when layer flags trigger, then delegates to the base handler. | Cannot whitelist as harmless progress metadata without binding the pause variables and called behavior. |
| `EXCLUDE_OBJECT_*` | `exclude_object.py` installs a move transform to skip excluded objects and maintain extrusion/position state. | Cannot ignore object markers while claiming the same movement/E model. |
| Pressure advance / purifier / chamber | Pressure advance can be suppressed by flow-calibration settings; purifier/chamber behavior depends on additional runtime configuration. | No complete envelope or verified parameter/state binding is implemented. Remain rejected. |
| Defect detection / timelapse | `defect_detection.py:700+`, `timelapse.py:79,148,183`: LED control, motion/probing for bed checks, MQTT camera requests, conditional failures/pauses. | Normal profile commands can invoke camera services. Camera compatibility/ownership/expiry/safe cleanup remain unresolved; no camera call was issued to investigate them. |
| `PRINT_END` | `fluidd.cfg:216`: retracts, raises Z, optionally unloads, parks heads, moves XY, shuts down heat/fans and resets job state. | End motion/consumption and state-dependent branches need validation too; validating only startup or geometry would be insufficient. |

These are focused static findings, not completion of the macro interpreter or
hardware acceptance. No general Jinja evaluator or raw-G-code execution tool was
introduced. Slicing remains outside this repository.

## Implemented numeric envelope

- M73 requires P in 0–100; optional R is 0–1,000,000 minutes. The matched
  `display_status.py:35` only updates display progress/expiry and does not read R.
  The validator still bounds R and refuses other parameters.
- M106 requires S in 0–255; M107 turns cooling off. Optional P must equal 2
  using firmware-compatible integer syntax (P2.0 is rejected),
  confirmed as auxiliary cooling in active configuration and handled by
  `fan.py:cmd_M106/cmd_M107`. Other fan IDs remain rejected.
- M204 accepts only S, >0 and <=10,000 mm/s². SET_VELOCITY_LIMIT requires
  ACCEL in that same range; optional ACCEL_TO_DECEL must be >0 and <=ACCEL.
  `toolhead.py:723–783` changes acceleration/junction planning without moving
  or changing coordinate/temperature state. Velocity, corner-speed, pressure
  advance and arbitrary named parameters remain rejected. The ceiling is
  conservative software policy, not a measured hardware limit.
- G17 explicitly establishes the sole supported XY plane for each file; inherited
  firmware plane state is never assumed. G2/G3 require known homed XYZ,
  absolute XYZ and nonzero I/J center offsets. R, K, relative coordinates and
  other planes remain rejected. `gcode_arcs.py:65–208` creates points on a
  supporting circle and appends the exact endpoint; Z interpolates linearly.
  The inspector bounds the **whole circle**, start and endpoint in O(1) memory,
  including full circles and unequal endpoint radii. It never checks endpoints
  alone or allocates firmware segments. Partial sweeps near a boundary can be
  conservatively rejected even if the actual sweep would fit. G-code coordinates
  are checked in the existing 0–270 envelope, not certified calibrated machine
  coordinates. Feed, waits, positive/negative E and every-tool consumption checks
  are shared with linear moves. Absolute E still needs a reset after selection.

All existing path/open-handle checks, hash rechecks, mapping/feed/material
binding, process serialization, expiry and no-replay reconciliation remain.
Validator policy identity is now 2: old preparation receipts cannot authorize a
new upload; old inflight operations remain unknown on policy mismatch and do not
resend. Existing terminal results remain historical. Preserve the journal and
investigate old uncertain uploads through ordinary read-only reconciliation;
do not delete receipts or manufacture a new operation to replay them.

## Verification and next acceptance

Tests use synthetic programs and an intact stock-shaped rejected sequence,
including each observed macro as an independently rejected input. Actual MCP
subprocess/HTTP tests verify unchanged bytes and SHA256 for accepted numeric
fragments, and pre-upload refusal of stock input, unsafe arc interior/endpoint,
cold extrusion, understated consumption and later undeclared tools. Restart tests
cover old-policy undispatched and inflight receipts. Existing failure tests
continue to cover mapping, feed, hash mismatch, HTTP-200 errors, expiry, races
and reconciliation. Final suite/build results are recorded in PROJECT_STATE.md.
Independent review reproduced acceptance without an explicit G17 and acceptance
of decimal fan-selector syntax; both findings were observed failing in regression
tests before fixes and now have parser and actual-MCP coverage.

The smallest **separately authorized hardware upload acceptance** is one uniquely
named, fully validated restricted file uploaded with `print=false`, followed by
read-only remote byte/SHA256 verification and before/after checks that the print
state, active filename, virtual SD and queue did not change. Confirm the normal
authentication and actual response root/path/false flags. No start, job-parameter
change, camera operation or automatic deletion belongs in that step. It tests
file transfer only; it cannot establish stock-profile safety. No such action was
performed or enabled here.

For full normal-profile support, first resolve the bounded macro/offset/mesh,
hidden every-tool thermal/consumption, camera and metadata contracts above and
bind the needed runtime evidence. Printing then needs a separate specific-plate
authorization, fresh human clear-bed confirmation and the usual start checks;
first-layer/completion/quality remain separate observations.
