# Matched startup/toolchange effects — 2026-10-25

## Result and evidence boundary

This follow-up hardens restricted validation; **no additional stock command or
intact normal export is accepted**. Tool selection invalidates inferred XYZ;
full G28 invalidates inferred active tool and E origin; positive heater targets
participate in material requirements; aliased physical mappings and firmware-
incompatible selectors are refused. Receipt policy is 3.

The [prior report](2026-10-25-orca-u1-gcode.md) records the observed firmware,
vendor image identity and release head
`bc271fb351f8c3ad84300e652e46fd93c53b9de1`. This investigation reused those
ignored files, verified all 20 existing source-manifest Git blob/SHA256 entries,
and checked the additional extracted files against the existing artifact manifest.
No new discovery/download, REA reconstruction, target-code execution or printer
request was needed. The image/config match does **not** attest running code.

Source anchors below refer to that release's `lava/fluidd.cfg`,
`lava/printer.cfg`, `klippy/kinematics/extruder.py` and `klippy/extras/*.py`.
Additional artifact-only source identities (not claimed independently compared
to public release source):

| Artifact source | Bytes | SHA256 |
| --- | --- | --- |
| `filament_feed.py` | 103,299 | `fa4d6cb5a1bd92338d234d9a8de6a105e08aa7d2e95a8c5119e02172ab079d43` |
| `filament_parameters.py` | 73,910 | `7af7b9537a1b6e202aae41a7cd95d2b414d2cee1f2fc3e416610529d6dcba7e4` |
| `homing_precise_corexy.py` | 32,633 | `23246d33e9781e00409b1eda8874b89dc2fadc1bfa8368c02a2ea64ffeb9e3f3` |
| `probe_inductance_coil.py` | 100,151 | `5beaa343012a48c29953f4aece0d12967b85169f05a60973d0df897105ea185b` |
| `extruder_config_bak.py` | 12,758 | `56be84ec9b7f30cfa496e86591fe5e767ce79d716fd93fdf112dabc25001e5da` |

## Selection, coordinates and E

`extruder.py:447–550` registers literal T0–T3. `gcode.py:201–230` dispatches
literal command names; T01 is not T1. `cmd_SWITCH_EXTRUDER_ADVANCED`
(`extruder.py:1330–1344`) maps the logical index through
`print_task_config.get_extruder_map_index` unless A0 requests physical selection.
M104/M109 use the same default mapping for explicit T, but omit T to address the
currently active physical heater (`extruder.py:1120–1136,1267–1278`). Their T
parameter uses `get_int`; decimal spellings such as T1.0 fail in firmware.

The complete selection path is not a coordinate-only operation:

1. `cmd_SWITCH_EXTRUDER` (`:1345–1410`) retries park/pick failures, may force a
   park on retry or a pogo-pin error, and marks XY unhomed on failure. A final
   attempt may relax an activation check; this is firmware behavior, not bridge
   permission to bypass a sensor.
2. `_cmd_SWITCH_EXTRUDER` (`:1411–1530`) may call G28 XY (or G28 without the
   override), waits for moves and checks physical activation. Its same-head
   early return depends on grip/park reports **and** the toolhead's current object.
3. It saves modes, base/homing/last positions, speed/flow factors, fan and
   acceleration; then performs park and pick through direct `manual_move`
   sequences (`:1531–1760`). X paths depend on park position, grab direction,
   horizontal travel and retraction distance; Y paths depend on insertion buffer
   and idle/park coordinates. Physical status polling and retries select paths.
   The carriage is not returned to the pre-switch print point.
4. The `finally` path restores saved modes/base/homing/speed/flow and adjusts E
   base by the actual E difference (`:1767–1792`). On success it activates the
   selected extruder, rebinds probe/fan, and applies that head's XYZ offset with
   `SET_GCODE_OFFSET ... MOVE=0` (`:1795–1818`).

Offsets derive from configured or backup per-head base positions
(`extruder.py:562–572,698–728,901–911`): X/Y reference the midpoint of the
valid heads' extrema; Z references the first valid head's base Z. It is not a
simple tool-number translation or an assumption that every offset is zero.
`gcode_move.py:77–81` resets E base on activation. Its G1 adds `base_position`
to absolute XYZ (`:118–150`); SET_GCODE_OFFSET changes that base and homing
origin even with MOVE=0 (`:257–279`). Hence unchanged carriage coordinates can
have different G-code coordinates after selection.

The inspector now forgets **all** XYZ after every T, including a repeated T.
An absolute G0/G1 with explicit X/Y/Z can reestablish G-code-space position;
relative, partial-axis and arc moves cannot use stale coordinates. Absolute E
still needs G92 E after selection. These checks do not bound the intervening
park/pick/retry paths, inherited offsets or calibrated machine-space motion.
Full G28 is still firmware-owned; it is not a zero-offset reset.

## Startup, physical heat and hidden consumption

`PRINT_START` (`fluidd.cfg:193–209`) loops over **all physical heads** and calls
`FLOW_APPLY_CALIBRATE_K`, resets startup-line/feed macro variables, disables
motors with M84, resets E and sets speed to 100%. The flow call
(`flow_calibrator.py:606–627`) applies saved `_current_k` through the extruder
stepper's pressure advance setter (`:378–383`). It does not itself extrude, but
it changes subsequent extrusion planning. It does not establish a zero flow
multiplier or neutralize every inherited transform. Persisted K is not supplied
by the six metadata fields the bridge currently inspects.

`SM_PRINT_CHECK_SWITCH_EXTRUDER` (`fluidd.cfg:866–874`) loops over physical
`extruders_used` and calls T{i} A0, independently of the visibly active logical
filament. `SM_PRINT_EXTRUDER_PREHEAT` (`:876–884`) conditionally issues
M104 with physical T/A0. Those flags must agree with mapped file requirements;
neither RFID nor a one-filament label establishes them.

`SM_PRINT_AUTO_FEED` (`fluidd.cfg:886–904`) maps the physical head to a feed
module/channel then calls `FEED_AUTO LOAD=1 PRINTING=1`. Its transitive path:

- `filament_feed.py:1721–1839`: may skip for completed/error-free loading,
  absent port filament during printing, missing module, disabled auto mode or
  disabled/missing sensor. Otherwise it runs `_do_feed`; saved target restoration
  depends on machine state and uses physical T/A0, including error cleanup.
- `:682–714,782`: load temperature and soft/hard behavior derive from runtime
  vendor/type/subtype, nozzle diameter and nozzle volume type through
  `filament_parameters`, not simply the visible M109. Missing objects have
  fallback values; a fallback is not material-suitability evidence.
- `:968–1117`: preheat at material load temperature minus 70, possible XY
  homing, physical selection, drive engagement and sensor-dependent feeding
  precede discard motion and a material-temperature wait. Feed motor strokes
  themselves are not represented by file E moves.
- `:1132–1247`: each load attempt can extrude two 20 mm hard-filament strokes
  or three 30 mm soft strokes. Failed attempts clean and add another 40/50 mm.
  The configured attempt count is bounded 3–50 (`:513–515`), but the bridge
  does not currently capture it or the branch state. Success calls
  `INNER_FLUSH_FILAMENT`, with a default **80 mm** positive E, material-temp
  wait, heater changes, cleaning and state-dependent retraction
  (`fluidd.cfg:1135–1172`). This is not a zero-consumption setup marker.

`SM_PRINT_FLOW_CALIBRATE` (`print_stats.py:255–299`) resolves INDEX mapping or
physical EXTRUDER/current head, possible replenishment, physical used flags,
global/per-head flow flags and persistent per-job completion flags. If enabled,
it selects physical T/A0, invokes FLOW_CALIBRATE and persists completion.

`FLOW_CALIBRATE` (`flow_calibrator.py:642–1182`) checks filament/sensors and
compatibility; chooses built-in settings, then valid file settings, then explicit
parameters. Temperature, volume/flow ratio, line/layer geometry, nozzle volume
type, acceleration, algorithm and sample loops affect demand (`:724–870`).
It homes XY if necessary, moves to discard, waits for heat and repeatedly
measures K. `_prepare_phase` / `_extrude_loop` (`:384–428`) use **direct manual
E movement**. One non-aborted measure alone requests
`start_dist + loop*(slow_dist + fast_dist) + 5*slow_dist`; the search can repeat
measurements. Sensor-based aborts and algorithm branches matter. Completion
can persist K, clean, move to idle and turn off heat (`:1143–1182`). A file's
visible G1 high water is not an envelope for this chain.

`SM_PRINT_PREEXTRUDE_FILAMENT` (`print_stats.py:207–253`) has its own logical
completion flags, mapped used head and target-temperature fallback. Its inner
macro (`fluidd.cfg:1250–1282`) saves/restores state, moves to discard, waits,
enables flow-K behavior, extrudes default 20 mm (10 for soft), retracts, cleans
and moves. Startup lines (`:937–1016`) are additional conditional purge paths.

Auto replenishment (`print_task_config.py:902–1070`) can change physical
mapping/used/calibration flags, cool the old head, update persisted job state and
invoke RESUME with the replacement. Freezing today's mapping is not a lifetime
guarantee. Future support must either bound and bind the replacement chain or
refuse it; silently assuming it never occurs is insufficient.

Two concrete restricted-dialect fixes follow from these findings:

- Every **positive** explicit nozzle target now marks its logical entry used,
  requiring positive declared mm/g, heat requirements and fresh physical
  material/feed/nozzle evidence even without visible E. An undeclared 140 °C
  preheat is conservatively refused; S0 alone creates no material requirement.
- Requested physical mappings must be injective across declared entries.
  Otherwise `M109 T1 S210; M104 T0 S0` could cool the very same physical heater
  while logical T1 still appears warm. `mapping_ambiguous` refuses preparation
  and fresh upload evidence until physical heater/E accounting can support aliases.
  This deliberately refuses some potentially valid shared-head jobs.

## Cleaning, homing and transforms

`MOVE_TO_DISCARD_FILAMENT_POSITION` (`fluidd.cfg:179–186`) chooses offsets by
the current **physical** head and calls `MOVE_TO_XY_IDLE_POSITION_EXTRUDER`.
The handler (`extruder.py:1820–1864`) derives idle X from park geometry and
grab direction, handles physical-head-specific adjustment, optionally moves Z,
chooses XY ordering from current carriage Y and temporarily changes acceleration.
It issues direct machine moves; treating its numeric offsets as absolute file
coordinates is wrong.

Rough cleaning calls that discard chain then relative brushing; the combined
variant also invokes cutoff and randomized discard. Those inner macros have
head-dependent X direction, relative Y, acceleration/feed changes, and a
persistent-in-process `random_pos % 6` (`fluidd.cfg:788–864,1018–1133`). Fine
cleaning calls idle, moves relatively, contacts the bed, then wipes.
`PROBE_BED_CONTACT` (`probe_inductance_coil.py:200–230`) can invoke a configured
`_PROBE_BED_CONTACT` macro or a PROBE fallback and raise Z on failure. Probe
results and optional macro bodies are unresolved inputs, not fixed endpoints.
`DETECT_BED_PLATE` (`:1495–1580`) moves between solid/hole probe locations and
has separate success/failure lifts and error effects.

G28's override (`homing_xyz_override.py:379–480`) can hop Z before homing,
run the XY template, load the default mesh, preprocess/reselect a physical head
(`:154–160`), probe at the configured or I/J location, and rebase Z. The matched
XY template (`printer.cfg:511–537,626–632`) changes driver currents, calls
advanced precise homing, then restores currents. The latter has retry/calibration
branches (`homing_precise_corexy.py:558–578`). Homing is not ordinary motion
inside the file's 0–270 cube, and requires its own bounded acceptance.

Z homing (`homing_xyz_override.py:287–332`) incorporates the selected head's Z
offset and, with a mesh, rebases/rebuilds it and saves the default profile. It
also clears mesh on some failure paths. Therefore the inspector now discards
active tool/E knowledge after full G28; subsequent implicit-heater or E commands
need explicit selection again. The bridge does not issue G28 during research.

`BED_MESH_CALIBRATE` (`bed_mesh.py:717–735`) conditionally skips while printing
if auto leveling is disabled; otherwise it clears the current mesh, updates
parameters and starts probing. The mesh transform accounts for interpolated Z,
fade, tool offset and split moves (`bed_mesh.py:154–243`). Inspecting G-code Z
alone cannot bound transformed physical Z. Neither calibration nor partial G28
is newly accepted.

## Layer, object, end and camera effects

- `SET_PRINT_STATS_INFO` (`fluidd.cfg:647–662`) can invoke a configurable pause
  command, clear its flags and then call the base statistics handler. The
  configurable call is an unresolved branch; no assumption that it is always
  PAUSE, or that PAUSE has no motion/retraction, is justified.
- `EXCLUDE_OBJECT_DEFINE` records definitions (RESET also resets exclusion
  state); START/END change current-object state. DEFINE alone does not install
  the move transform. An exclusion request does (`exclude_object.py:39–100,
  279–380`), and normal/excluded transitions adjust E and movement
  (`:151–277`). Future support needs the full exclusion lifecycle and external
  state binding, not just ignored markers. All these commands remain refused.
- `PRINT_END` (`fluidd.cfg:216–278`) uses runtime client retract settings,
  conditionally lifts Z, sets `INNER_PRINT_END`'s replenishment-suppression flag,
  may unload every physical used head, parks, moves XY, turns heaters/fans off,
  changes purifier/optional LED and pause/idle variables and disables motors.
  `_CLIENT_RETRACT → _CLIENT_EXTRUDE` (`:664–702`) depends on can-extrude,
  mode and optional firmware retraction. `SM_PRINT_END_AUTO_UNLOAD_FILAMENT`
  (`:906–915`) reaches the feed unload stages and their material-dependent
  heat/retract/cleaning path. End behavior is part of the required envelope.
- `TIMELAPSE_START/STOP/TAKE_FRAME` reach MQTT camera RPC, guarded by distinct
  job/active/ignore flags (`timelapse.py:79–224`). STOP's FORCE branch can act
  without local active state; no bridge ownership guarantee follows. Defect
  commands can light LEDs, move/probe/lift for bed inspection, request camera
  detection and pause on outcomes (`defect_detection.py:374–616,700–997`).
  Disabled flags may skip a branch; their names do not establish inertness or
  safe camera ownership. No camera interaction was performed.

## Runtime evidence required before broader acceptance

The next development step is a bounded **read-only evidence contract**, not
macro execution. It must account for missing/unexposed fields and observation
races; raw configuration is private. At minimum, establish how to read and bind:

| Dependency | Required evidence / unresolved acceptance |
| --- | --- |
| Physical selection / coordinates | Actual active/grip/park states; homed axes; G-code base/homing origin and modes; every head's effective offsets, backup precedence and park geometry; bounds for all retry/failure moves. |
| Transforms | Active mesh/profile, interpolation/fade/tool offset and exclusion state/transform lifecycle; changes made by probing and other clients. |
| Per-head heat / material | Mapping, used/replenished flags, module/channel mapping, all sensors, vendor/subtype, nozzle diameter/volume, material load/print temperature resolution and heater limits. |
| Consumption / flow | Feed attempt limits/motor stages, purge/retract state, flow algorithm/loop parameters, saved K and per-job completion flags; bound positive E and physical demand across all branches. |
| Pause / end / camera | Exact configurable macro bodies and variables, end-unload flags, callback chains, camera flags and ordinary ownership/lifecycle contracts. |
| Receipt freshness | A normalized digest including these dependencies, policy version and expiry; repeated checks before dispatch/start. HTTP reads are not an atomic machine snapshot. |

The existing three read tools do not provide this whole contract. Reading a few
offsets alone cannot establish it. Keep macros blocked until the complete
transitive effects can be bounded; no general Jinja or raw-G-code tool is added.

The smallest next evidence probe is one bounded read-only object query for
`toolhead`, `gcode_move`, all four `extruder` objects and `bed_mesh`, paired with
the existing mapping/configuration evidence. Establish the actual availability,
types and consistency of homed axes, selected head, `extruder_offset`,
`homing_origin`, machine/G-code positions and active mesh fields. Missing fields
must stay unknown. Such a snapshot would test the proposed coordinate-evidence
reader, not prove the complete offset/mesh/toolchanger envelope or authorize
movement. No such new live query was performed in this follow-up.

## Corpus, tests and next acceptance

All eight original bytes/hashes were rechecked and inspected unchanged:
01–04 and 08 still first fail `unsupported_command` at EXCLUDE_OBJECT_DEFINE;
05–07 still first fail `job_requirements` for one-entry consumption/material and
four-entry nozzle metadata. Even resolving those first errors would leave the
startup/cleaning/flow/mesh/end/camera blockers above. There is still no multicolor
toolchange acceptance corpus, and no metadata replication/physical assignment
is inferred. Stable hashes remain in the prior report; private outcomes are ignored.

Synthetic parser/coordinator regressions reproduced the gaps before fixes.
Actual MCP stdio/loopback HTTP tests exercise explicit post-selection XYZ success,
relative/partial/arc refusal, heater/material refusal, selector and mapping
refusal, G28 identity loss and policy-2 restart refusal. Policies 1/2 cannot
dispatch or promote uncertain results under policy 3; matching remote bytes do
not override a policy mismatch. Existing no-replay, hash, expiry and failure
coverage remains. Verification/review totals are recorded in PROJECT_STATE.md.

No live request or configuration change was issued. Uploads remain disabled,
five tool names remain, and hardware acceptance is pending. The smallest
separately authorized hardware transfer step remains a unique restricted file
uploaded with `print=false`, followed by exact remote-byte/SHA256 and before/
after idle/filename/virtual-SD/queue observations. It proves transfer only.
Full stock-profile hardware testing needs the evidence contract above first,
then specific-plate authorization and a fresh human installed/clear-bed check;
first-layer, completion and quality require separate observation.
