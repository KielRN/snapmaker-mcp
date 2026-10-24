# Read contract evidence — 2026-10-24

## Live MCP verification

The official Python MCP SDK launched the registered `snapmaker_u1` command over
stdio, initialized the session, listed exactly three tools, and called each with
`{}`. All returned `ok` at **17:34:05 UTC**, with empty stderr. An earlier check
at 17:25:36 UTC used the same package directly; the later check exercised the
configured launch after the final transport/logging fixes. Raw receipts remain
ignored locally. These observations support one installed firmware, not all U1s.

Installed versions: printer `2.0.0.205_20260914173503`, Moonraker `2.0.0`.

| Contract | Installed observation | Interpretation |
| --- | --- | --- |
| Job/readiness | Klipper ready, print state printing, virtual SD active. | Busy; readiness alone never means idle. Progress is the virtual-SD fraction. |
| Active tool | `toolhead.extruder == extruder1`. | Physical 2 / T1. Physical tools 1–4 are `extruder`, `extruder1`, `extruder2`, `extruder3`. |
| Temperatures | All extruders and bed reported numeric temperature/target. | Four nozzle readings plus bed; invalid/nonfinite/negative values become unknown. |
| Mapping | 32 zero-based entries; only physical job-use index 1 true. | Output mapping uses one-based physical tools. Unused mapping defaults do not imply use; job-use flags are separate. |
| RFID | Four entries in `filament_detect.info` and `state`. | Selected identity/color/SKU/read-state fields only, no card UID or loaded-state inference. |
| Feed | Left keys `extruder0`/`extruder1`, right `extruder2`/`extruder3`. | Feed key `extruder0` maps to API `extruder`. All four reported positive detection, completed load, and no errors. |
| Toolhead sensors | All four `filament_motion_sensor eN_filament` objects were enabled and positive. | Combined with feed evidence, four sensor-derived loaded states; no physical inspection implied. |
| Exceptions | `exception_manager.exceptions == []`. | Known clear in that snapshot; nonempty exception handling has source/simulated evidence only. |
| Camera | Empty Moonraker webcam array. | Configured count zero; proprietary camera availability unknown. |

Printer info, object inventory, and the object snapshot are separate requests.
`atomic_across_requests` is false. Observation windows and Klipper event time are
reported. This milestone has no stale cache, preparation receipt, or mutation
path. It omits filenames, machine identity/paths, and raw upstream messages.

## Pinned source provenance

Inspected files' Git blob hashes matched the following public trees. This is
source identity, not proof that repository `main` matches installed firmware.

- U1 Klipper tree `10f2f69714c059f1dee0423db4f515b8a01f5388`:
  [feed](https://github.com/Snapmaker/u1-klipper/blob/10f2f69714c059f1dee0423db4f515b8a01f5388/klippy/extras/filament_feed.py),
  [detection](https://github.com/Snapmaker/u1-klipper/blob/10f2f69714c059f1dee0423db4f515b8a01f5388/klippy/extras/filament_detect.py),
  [task config](https://github.com/Snapmaker/u1-klipper/blob/10f2f69714c059f1dee0423db4f515b8a01f5388/klippy/extras/print_task_config.py),
  [exceptions](https://github.com/Snapmaker/u1-klipper/blob/10f2f69714c059f1dee0423db4f515b8a01f5388/klippy/exception_manager.py).
  Observed status field names agree with this source. Source action levels map
  1 to no automatic print action, 2 to pause/runout pause, and 3 to cancel. The
  adapter treats 2/3 as blocking and unknown levels conservatively. No fault was
  introduced to prove those semantics on the installed machine.
- U1 Moonraker tree `a308cfae31b7eb70ebf96bc73e6968d9792e4d73`:
  [Snapmaker routes](https://github.com/Snapmaker/u1-moonraker/blob/a308cfae31b7eb70ebf96bc73e6968d9792e4d73/moonraker/components/snapmakercloud.py).
  Advanced print/file operations are research context only, not exposed or
  exercised by this milestone.

## Software verification and limits

59 tests passed on Windows/Python 3.11.14 and 3.13.12. Coverage includes real MCP
subprocess discovery/calls against local HTTP simulation, typed output schemas,
strict empty arguments, mixed mapping, RFID/feed separation, missing sensors and
objects, exceptions, numeric corruption, HTTP-200 errors, authentication,
timeouts/disconnects, no stale success, redaction, malformed stdio frames,
redirects, response limits, and refusal of compression before decoding.

Independent review reproduced two issues (compression memory amplification and
SDK logs echoing validation payloads); both fixes were regression-tested and
independently rechecked. Ruff checks/formatting and wheel/sdist builds passed.

Live reads do not verify real outage behavior, active physical faults, controls,
camera sessions, completed jobs, or print quality. Consumption arrays, unsafe
file paths, upload hash mismatch, state races, receipt expiry, repeated operation
IDs, restart reconciliation, and stale camera frames remain acceptance criteria
for the future tools that consume those inputs.
