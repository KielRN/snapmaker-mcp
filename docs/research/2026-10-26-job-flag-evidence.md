# Reported job preferences and their limits

Date: 2026-10-26. Source/artifact investigation and software implementation only;
**no live request**, preparation, upload, G-code, camera, print-control,
job-parameter, calibration or configuration operation in this round.

## Evidence identity and scope

Reuse the previously verified vendor artifact for observed firmware
`2.0.0.205_20260914173503` and the selected source pinned to
`bc271fb351f8c3ad84300e652e46fd93c53b9de1`. No new download, discovery, REA,
target execution or repeated identity audit. The existing manifest covers the
matched `print_task_config.py`, `print_stats.py`, `bed_mesh.py` and `fluidd.cfg`.
Anchors below refer to those saved bytes, not repository main or attested loaded
code. New focused artifact-only consumer anchors (no independent public-source
comparison claimed):

| Extracted module | SHA256 |
| --- | --- |
| `timelapse.py` | `584da4f5e962d53be05b59171ae0732f597c43ca9393f3b5741dcea27c9d6143` |
| `filament_entangle_detect.py` | `056ca8d4e9df02836b7633b406a678c41922fab454c31c526355d31b9dbdeb72` |

The previous [transform investigation](2026-10-25-transform-evidence.md) found
no supported passive diagnostic for installation/order, effective fade/lookup/
ZFADE or calibration provenance. These remain unknown; job flags do not close
that gap. This run follows the distinct job-flag contract in the prior handoff.

## Supported getter and lifecycle

| Anchor | Established behavior and limit |
| --- | --- |
| `print_task_config.py:25–63` | Default dictionary contains job preferences and a separate nested `reprint_info`. Defaults are software initialization, not performed actions. |
| `:402–444` | Reset clears mapping/use/replenishment and several job flags; completion reset also clears the second parameter dictionary. Preferences and completion evidence are different. Not every preference is reset identically. |
| `:446–493` | Reprint apply/capture copies selected nested/current fields; a later start can replace current values. `set_new_print_info` resets the internal end-action flag. Neither operation is an authorization. |
| `:495–533` | `get_status` first refreshes filament existence/edit flags, then returns a shallow dictionary copy. It calls feed and toolhead-sensor getters. It does not itself issue G-code, save configuration, calibrate, start/stop a camera or control a print. It is not a pure, atomic snapshot: in-memory reports can change on read and nested lists are shared. |
| `:511–527` | Filament existence starts optimistic and is not equivalent to completed physical loading. The bridge continues to require its independent enabled sensor and completed/error-free feed evidence; it does not use this existence flag as proof. |
| `:710–812,1092–1449` | Preference/job-parameter commands parse and update different subsets, copy some fields into reprint state and persist data; entanglement setters can send an event. None is newly supported by the bridge. The second parameter dictionary is not returned by this getter. |
| `:1458–1459` | `INNER_PRINT_END` only sets the internal `is_exec_print_end_action` flag. That flag is not in the supported status dictionary and does not itself establish completion of the end macro. |

Field projection happens after the provider runs. Selecting fewer fields does
not avoid its refresh calls. Existing materials reads already use this provider;
adding it to runtime observations increases read-time refreshes. Source inspection
found report updates, not hardware/configuration commands on that getter path.
This is static evidence, not an assertion about every installed implementation.

## Consumers: preferences are not results

- `bed_mesh.py:716–733`: an inductance-probe calibration request may return
  early while printing when `auto_bed_leveling` is false. True does not prove a
  mesh was measured, installed or remains effective. Other state still matters.
- `print_stats.py:267–298`: flow calibration uses the logical/physical map,
  replenishment history, used heads, requested flow flags and separate completion
  data. It can select a head, run calibration and save completion data. The two
  exposed flow flags cannot replace that state or the saved calibration K.
- `print_task_config.py:902–1075`: auto-replenishment depends on paused state,
  feed/sensors, backup material, resume variables, nozzle properties and optional
  color matching. It can change the map/use/flow/replenishment and reprint state,
  heater/restore state and invoke resume. A preference is not a bounded feed or
  thermal/consumption contract. Replenishment history is not collected here.
- `filament_entangle_detect.py:133–158,199–209`: detection also depends on
  initialization, skip state, printing and feed reports; sensitivity changes its
  threshold. Requested enable/sensitivity do not prove active protection.
- `fluidd.cfg:254–277,905–915`: end handling can unload used, non-soft heads,
  park/move, disable heat/fans and optionally switch off the LED. Unload flags are
  physical-head preferences; softness, macro bodies, motion and completion remain
  separate dependencies. The commented cancel LED example is not execution.
- `timelapse.py:73–75,79–145,148–181,183–224`: start additionally requires MQTT,
  no ignore flag and inactive local recording; success sets a local active bit.
  Start can switch on the cavity LED and send `camera.start_timelapse`. Stop
  clears the local bit even after failed RPC, or immediately if MQTT is missing.
  False preference/local activity cannot prove the server stopped. Time-lapse
  recording is separate from live-camera ownership, expiry, freshness and close.
- `shaper_calibrate` is a supported stored preference and setter input; this
  focused consumer search did not identify an execution gate using that job key.
  Do not invent a calibration-completion meaning for it.

## Implemented bounded contract

`runtime_evidence.job` contains only eight exact booleans: `time_lapse_camera`,
`auto_bed_leveling`, `flow_calibrate`, `shaper_calibrate`,
`auto_replenish_filament`, `replenish_ignore_color`, `filament_entangle_detect`
and `end_led_turn_off`; two exact four-boolean physical T0–T3 lists,
`flow_calib_extruders` / `end_unload_filament`; and sensitivity exactly
`low` / `medium` / `high`. Numeric/string coercion, extra/short arrays and unknown
enum values are refused as unknown. False remains known false. Raw dictionaries,
nested reprint values and arbitrary strings are omitted. The fixed 14-field
projection also retains the three fields already consumed by materials.

Policy **9** binds these reports in both runtime observations around materials/
job identity, before dispatch and around remote bytes/reconciliation. Missing,
malformed or changed reports block dispatch/promotion; policies 1–8 cannot be
reused. Existing time ordering/watermark, expiry, serialization, path/handle,
mapping/material/feed/nozzle, thermal/consumption, hash and no-replay checks stay.
Historical field defaults only permit receipt deserialization; terminal results
retain their original meaning/time. Idle classification is unchanged: flags are
preferences, not activity labels. No new tool, command, macro or intact export
is accepted. Uploads remain disabled locally and by default.

Equal repeated reports cannot exclude intervening changes, stale peer data or
other clients. `job_action_completion` and `reprint_and_job_parameters` remain
explicitly unestablished, alongside every prior transform/feed/pause/hook gap.
There is no new hardware availability/type/behavior claim for these fields.

## Verification and next action

The [execution ledger](../superpowers/plans/2026-10-26-job-flag-evidence.md)
records tests, independent review, package/privacy audits and integration.
Readiness and hardware acceptance remain incomplete.

Next investigate the distinct artifact time-lapse RPC response/correlation and
failure lifecycle before expanding camera tools. In particular, local inactive
state after failed stop is not server cleanup evidence. Reuse saved artifact and
prior camera research; no camera start/stop or repeated job/mesh/head query.
