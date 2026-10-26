# Pause/end evidence — 2026-10-25

## Established result

The five-tool bridge now collects only `pause_resume.is_paused` from the supported
status provider and binds its exact boolean report under **policy 7**. True blocks
idle independently of `print_stats.state` and inactive virtual SD. Missing, null
or malformed reports remain unknown and prevent a positive idle/preparation result.
False is necessary for that result; it does not certify safe resume, finished
motion, physical clearance, completed end actions or the transform chain.

One fixed read-only GET at **2026-10-25 20:44:17.804708–20:44:18.029262 UTC**
requested only `pause_resume=is_paused` and returned boolean **false** through
the normal bounded transport. This establishes availability/type on the installed
setup, not pause/resume/control acceptance. No discovery, configuration snapshot,
second probe, live preparation, upload, G-code, camera/control, job-parameter,
calibration or configuration mutation occurred. Uploads remain disabled locally
and by default. Raw probe and audits remain ignored under `.tmp/pause-evidence/`.

The prior transform investigation already found no decisive supported passive
chain/provenance diagnostic in the inspected status/dump contracts. This round
reused that result and advanced this independent contract; it did not repeat mesh,
offset, head or exclusion snapshots or treat G-code as a passive read.

## Source identity

Reused the vendor artifact for historically observed firmware
`2.0.0.205_20260914173503` and release source pinned to
`bc271fb351f8c3ad84300e652e46fd93c53b9de1`. Reverified all 20 source-manifest
SHA256/Git-blob entries and matching extracted Klipper files. The existing
[Orca report](2026-10-25-orca-u1-gcode.md) owns download/version identity. No new
download, REA reconstruction or target-code execution was needed. Artifact/source/
historical configuration agreement is not loaded-code attestation.

Additional artifact-only files were verified against the existing extraction
manifest; no independent public-source comparison is claimed for them:

| File under `klippy/extras/` | Bytes | SHA256 |
| --- | --- | --- |
| `pause_resume.py` | 9,423 | `5fcdfb058c89f3e8223b4f3ccaef41b8d514ac2e820958f2784085eaf2b2ecb3` |
| `idle_timeout.py` | 5,155 | `b346e700fe4beae3aa1e6483d7d67de4c571d59e9904c841095f6e1fbc4b0682` |
| `virtual_sdcard.py` | 116,736 | `38e769f078ee637c3393008e8d0dbb87dc4261ea1f1cd6ae9061fdb23673dc1e` |
| `gcode_macro.py` | 8,339 | `0c0f14ec0505ea1e33b55d4b146dc2e2eb443eca4a0c1e09a9db6eec652359e7` |
| `machine_state_manager.py` | 17,849 | `8e63a052b2e0ba02d111e59658d4a0af237ec9851817687cd6424ded667f7ccc` |

Anchors below refer to these artifact files, matched release
`print_task_config.py` / `print_stats.py`, and matched `lava/fluidd.cfg`.

## Saved pause, SD activity and print state are separate reports

`pause_resume.py:16–19,57–89` keeps three independent internal flags:
`is_paused`, `sd_paused`, and `pause_command_sent`. Supported status exposes only
`is_paused`. Sending a pause request first stops/requests stopping the SD worker;
PAUSE_BASE then saves `PAUSE_STATE` and sets `is_paused`. The saved coordinates,
the other two flags and successful completion of the outer macro are not returned.

`:90–111` gates PAUSE on print state, may decline an SD-originated request in
an excluded region, and calls INNER_PAUSE. `:121–139` restores saved G-code state
before resuming the worker and clearing `is_paused`. `:140–184` additionally gates
RESUME on paused print state, machine PRINTING/IDLE action and the saved-pause bit,
then calls INNER_RESUME; its error path can change hotend targets. `:185–196`
CLEAR_PAUSE clears flags without restoring coordinates or resuming, and base
cancel separately cancels SD and clears pause. Thus neither true nor false attests
all prerequisites or the success of an entire control chain.

`virtual_sdcard.py:223–263` reports activity from the presence of its worker timer.
Pause, resume and cancel separately change worker/file state. `:752–777` clears
the timer and then updates statistics according to read failure, command failure,
retained file or EOF. `print_stats.py:147–184` separately implements paused and
terminal states; note_pause preserves an existing error state. There is no
supported atomic invariant equating the saved-pause bit, the worker report and
the statistics label. The bridge adds no invented contradiction table.

These observations exposed a concrete software gap: the previous idle calculation
could return true from ready Klipper, terminal/standby statistics, inactive SD and
clear exceptions while ignoring a separately true or unavailable pause report.
Synthetic tests reproduced the positive idle result and phase-race dispatch/
promotion before the change. This is a conservative software fix; no anomalous
hardware state was induced or claimed observed.

## Pause/resume has motion, heat and saved-state dependencies

`fluidd.cfg:336–430` INNER_PAUSE captures the selected head and all four target
temperatures into INNER_RESUME variables, calls PAUSE_BASE, retracts, and may move
to discard position. A runout branch can heat/extrude and invoke feed handling;
an error branch sets an error-pause variable. Positive head targets are lowered
to the macro's pause temperature, fans are changed and idle timeout is changed.
Saved pause can therefore be reported before this outer sequence finishes.

`:432–625` INNER_RESUME depends on saved head/temperatures/E compensation, job
filament-existence/replenishment, batch-feeding state and homing. It can reload
filament metadata, home XY, select a physical head, auto-feed, move to discard,
restore multiple heaters, apply saved flow K, extrude 20 mm, retract and clean,
and finally restore coordinates with RESUME_BASE. The no-Z branch uses MOVE=0
but still has preceding selection/feed dependencies. Current temperature, pressure
advance and a false saved-pause bit do not bound this sequence. The
[startup report](2026-10-25-startup-toolchange.md) and
[head report](2026-10-25-head-extrusion-evidence.md) retain the hidden-demand,
actual trapq, saved-K and machine-space limitations.

## End/cancel, callbacks and flags

| Contract / source | Established semantics | Remaining boundary |
| --- | --- | --- |
| PRINT_END, `fluidd.cfg:216–276` | Retract and state-dependent Z moves; INNER_PRINT_END; conditional unload/park/XY move; heaters/fans/purifier, optional LED, layer-pause reset, motors and idle-timeout changes. | End is an executable motion/thermal/configuration-of-runtime sequence. A completion label alone does not attest physical quality, clearance or each action. |
| CANCEL_PRINT, `:278–334` | Retract/Z movement and INNER_PRINT_END precede CANCEL_PRINT_BASE; further cleanup includes TIMELAPSE_STOP. | Cancellation is not a no-motion/no-camera operation or a generic safe fallback. No cancel request was issued. |
| End unload, `:906–916` | Per-head `extruders_used`, `filament_soft` and `end_unload_filament` select AUTO_FEEDING unload stages. PRINT_END additionally gates this branch on homed XY. | Flags select branches; they do not establish feed-stage motion/heat bounds or completion. |
| Job flags, `print_task_config.py:25–63,529–533` | Status returns the job dictionary, including time-lapse/calibration/replenishment/end flags. Its getter also refreshes filament-existence/edit reports. | These flags have a supported read provider, but this change does not normalize/bind them or infer their effects. Reprint information is a separate nested dictionary. |
| Job reset, `:403–445,1458–1459`; `print_stats.py:167–174` | INNER_PRINT_END sets an internal flag. Finish resets task fields and can persist defaults before updating the statistics label. The internal end-action flag is absent from returned job status. | Reset/false flags do not prove that physical unload/end/camera cleanup ran. No guessed status field or reset/save/load command is used as a read. |
| Layer callbacks, `fluidd.cfg:627–662` | SET_PAUSE_NEXT_LAYER / SET_PAUSE_AT_LAYER store `call` strings; SET_PRINT_STATS_INFO executes the selected string before the base command. | The callback can be supplied through MACRO; a comment suggesting PAUSE/M600 does not restrict it. All of these macros remain rejected. |
| Macro status, `gcode_macro.py:163–164` | Returns runtime macro variables. | Does not itself attest loaded executable template bodies, transitive callees or safe future effects. No arbitrary macro or callback string is published/executed by this bridge. |
| Commented client hooks, `fluidd.cfg:45–47` | `user_pause_macro`, `user_resume_macro` and `user_cancel_macro` appear as commented examples; the inspected executable macros do not reference those names. | Do not report these examples as installed callback execution. Actual layer callbacks and error/idle templates above are separate contracts. |
| Error template, `virtual_sdcard.py:142–143,715–775`; `fluidd.cfg:50–52` | Loads configurable on_error_gcode; inspected configuration selects CANCEL_PRINT. Error action can instead choose PAUSE/PAUSE IS_RUNOUT. | HTTP/command acknowledgment cannot establish that an error callback completed or had no side effects. |
| Idle template, `idle_timeout.py:8–13,26–59,118–125` | Loads configurable idle G-code (default heaters-off/M84), tracks activity-derived Idle/Ready/Printing, and permits runtime timeout changes. | Status returns state/printing_time only. It omits current effective timeout and executable template body; Idle is not saved pause, file completion or physical clearance. |

The reported job flags and macro variables provide bounded future read candidates,
not permission to accept PRINT_END, CANCEL_PRINT, PAUSE/RESUME, layer callbacks,
TIMELAPSE_STOP or any other stock macro. Configuration examples and static artifacts
do not prove the currently loaded template. Hidden callbacks, saved restore state,
transform/provenance, thermal/consumption and camera ownership remain dependencies.

## Implemented enforcement and verification boundary

Both opening status and closing runtime/job reads use the same fixed
`pause_resume=is_paused` projection. Only exact booleans are normalized; arbitrary
peer fields remain private. `runtime_evidence.pause_resume_is_paused` is independent
of statistics and SD. Any positive busy report stays busy, including when pause
evidence is missing. Idle requires explicit unpaused reporting plus all prior
Klipper/statistics/SD/exception checks. Incomplete reads remain partial.

Policy **7** binds the added report through the existing digest/repeated-observation
checks around materials/job evidence, destination preflight and remote bytes.
Missing or changed closing reports prevent preparation; a later true/unknown
pause report blocks dispatch or leaves a dispatched result unknown. Policies
**1–6** cannot dispatch or promote uncertain receipts, including matching bytes
after restart. Historical model defaults permit deserialization only; old terminal
results retain their original time/meaning. No POST is replayed. All existing
path/handle/root, mapping/material/feed/nozzle, thermal/consumption, hash, expiry,
serialization, timestamp and reconciliation-watermark safeguards remain.

HTTP reports are non-atomic even within one query. Equal repeated false reports
cannot rule out intervening pause changes, stale peer data, another client or
buffered motion. The new unestablished dependencies explicitly retain saved pause
restore state and pause/end callback effects. No new motion-safety claim is made.

Tests cover strict unknown/private normalization, independent idle states, fixed
query selection, true/null/missing phase races, old-policy refusal, durable restart
and actual MCP/loopback HTTP schemas and outcomes. Final full verification,
independent review and audit results are recorded in [project state](../../PROJECT_STATE.md)
and the [execution ledger](../superpowers/plans/2026-10-25-pause-end-evidence.md).
The prior run stopped at its usage limit before integration. Its continuation
reconciled the existing change without another live request: fresh full suites
passed **454 tests on each of Python 3.11.14 and 3.13.12**, Ruff check/format and
wheel/source builds passed, and independent review found no actionable issues
or deferred minors. The reviewer separately passed all 454 tests and checked
historical policy-6 schemas and timestamp preservation without replay. Final
audit covered 57 files, 118 local links, both packages and 17 ignore samples,
with no configured private literals/generated artifacts or broken links; all
12 Python source modules match the packages. These are software checks only.

All eight intact exports retain original bytes/hashes and first refusals:
01–04/08 fail `unsupported_command` at EXCLUDE_OBJECT_DEFINE; 05–07 fail
`job_requirements` for ambiguous one-entry consumption/material versus four-entry
nozzle metadata. These are first failures only. No safety/setup commands were
stripped and no metadata mapping was guessed. Upload/stock-profile/control/camera
and full release milestones remain incomplete; software simulation is not hardware
acceptance. Every start still needs its own plate authorization and fresh human
installed/clear-bed confirmation.

Next nonduplicative work: trace `machine_state_manager.get_status` and its action/
transition hooks against virtual-SD/control callers. Determine which supported
reported machine/action values can conservatively block activity beyond printing,
and which transition/inflight state remains internal, before extending idle or
control contracts. Reuse the verified artifact; do not repeat pause/mesh/head
snapshots. Job flags/callback bodies can be addressed separately after their
acceptance semantics and remaining transitive dependencies are bounded.
