# Flow calibration precedence and bounded search

Date: 2026-10-27 UTC. Saved-source continuation of the
[feed resolver report](2026-10-26-feed-resolution-evidence.md).
**No live request**, authentication, target-code execution, diagnostic G-code,
calibration or configuration change. This is static evidence, not installed
execution or hardware acceptance. Runtime behavior and policy 9 are unchanged.

## Result and source identity

The calibration handler has finite local search branches: at most **six**
measurements for dichotomy, **five** for linear fitting and **four** for each OS
variant per invocation. This resolves the previously open search-count question.
It does not establish an observable total material/thermal/time budget: effective
parameters, saved environment/K, macro effects and action completion remain
unreported. No supported passive provider for those values was found in the
inspected calibrator. No new field, tool, command or stock export is accepted.

Reused five saved files, without discovery, download or a whole-artifact sweep.
The four Python copies match the extracted firmware bytes and the existing pinned
public-source SHA256/Git-blob manifest. The configuration matches the existing
firmware manifest. Historical firmware `2.0.0.205_20260914173503` and release
`bc271fb351f8c3ad84300e652e46fd93c53b9de1` retain the identity limits in the
[Orca report](2026-10-25-orca-u1-gcode.md); no loaded-code attestation follows.

| File | Bytes | SHA256 |
| --- | --- | --- |
| `flow_calibrator.py` | 65,741 | `c8e9576a2ce891877c8bc8b216ca80790b12b89d92a703c3c0a2a4c6e7e4ebfa` |
| `gcode.py` | 23,030 | `e857546ab17e0bca13a0286cf8ea50f2271382702412a2df269183f12bc8e484` |
| `toolhead.py` | 38,248 | `f28887bb85dcfd1ac530b4381bc3bf0b6103af247027870ab1a98024038f5188` |
| `kinematics/extruder.py` | 124,627 | `2085de67fb9a7d6c799a958c2a2ece639cc8f136f9dec792fa68eb2c359ce8f5` |
| `fluidd.cfg` | 62,146 | `68de851e0659e1f0553a737ea8c7eff848bbb264e0b9ba5ca6174c4c697f36fc` |

Anchors below refer to `flow_calibrator.py` unless another file is named.
Source/AST checks and raw verification remain ignored under
`.tmp/flow-calibration-evidence/`. The vendor module was never imported or run.

## Effective parameters are a field-specific merge

| Source/anchor | Effective contribution and limits |
| --- | --- |
| `:149–161,251–327` | Constructor loads saved factors/environment. Validation checks truthiness, rather than complete numeric types/ranges; failure can remove/recreate configuration. Saved values are not necessarily built-in defaults. Do not invoke the loader as a read probe. |
| `:642–711` | Uses the currently selected extruder, despite help mentioning TARGET. Reads job/material resolver state and an enabled negative runout sensor veto. FORCE bypasses certain preference/completion/material compatibility checks, not the whole handler. No FORCE use is authorized. |
| `:713–745` | Starts with 250 °C, saved environment acceleration/speeds/loop/K bounds and default K/max K. A successful resolver merge replaces temperature, acceleration, slow/fast speed and K values/bounds. It does not replace loop count. Resolver fallback/rollback remains as previously documented. |
| `:747–799` | Only while print statistics say printing/paused, copies the hidden second job-parameter dictionary. Scans logical entries mapped to this physical head; skips a candidate only when both g and mm usage compare below `0.00001`, taking the first remaining entry. This is not a finiteness check or alias aggregation. Valid file settings replace only temperature, acceleration and slow/fast speed. They do not replace K bounds/default or loop count. Any failure leaves the prior values. |
| `:763–790` | File temperature must fall between heater limits. Volume speed, flow ratio, line/layer geometry and selected normal/high-flow wall acceleration have local range tests. Uses fixed 1.75 mm filament area, clamps fast speed/acceleration to extruder limits, floors slow speed at 0.16 and requires fast > slow. The selection is not proof of file identity or correct array mapping. |
| `:801–843` | Explicit TEMP/speeds/acceleration/loop/K bounds/distances override their individual defaults. Algorithm defaults to OS_DECEL for high-flow, otherwise LINEAR_FITTING. STARTV defaults to the speed midpoint; distances derive from speeds/acceleration, with different OS ramp distances. The saved environment's start/distance entries are not these command defaults. |
| `:845–867,979–985,1047–1053` | Softness disagreement selects a different max-K limit. Linear/OS branches rerun the resolver but retain the earlier temperature/distance/loop dictionary and earlier K defaults/limit; they widen the limit to include the selected upper K. There is no one immutable resolved material snapshot. |

Explicit LOOP and the three distances have only nonnegative minima here, with
no local maximum. OS_COUNT is separately limited to 1–100 and controls calculator
sampling; it does not multiply extrusion-loop count. Explicit MIN/MAX are
bounded to 0–1 with MIN < MAX. Explicit speeds have no local upper maximum, and
ACCEL has a minimum of 5 and no local maximum. Lower-level move checks remain,
but calibration replaces their E-acceleration cap as described below; they do
not preserve the pre-calibration maximum.

Crucially, `gcode.py:59–90` returns an omitted parameter's default **before**
parsing/range validation. The stated explicit limits cannot be applied blindly
to saved/resolver defaults. Later ordering checks are not a complete finiteness,
type or physical-suitability check. `LOOP=0` also does not mean zero movement.
The bridge must not infer safe values from a help string or nominal table row.

## Finite measurement counts, conditional direct-E arithmetic

`_prepare_phase` / `_extrude_loop` (`:384–408`) directly request an E increment
of start distance, then slow/fast increments for each loop and an unconditional
five-slow-distance tail after the loop. For finite nonnegative distances and a
nonnegative integer loop count, a completed measure's direct requested increment
is:

`D = start_dist + loop * (slow_dist + fast_dist) + 5 * slow_dist`

This is requested E-coordinate distance from these helpers, not measured motion,
physical filament consumption, pressure-advance motor travel or a full macro
envelope. Zero loops retain the start and tail. Failure can interrupt a measure.

| Algorithm / anchors | Upper measurement calls in this invocation | Conditional direct-helper request ceiling |
| --- | --- | --- |
| DICHOTOMY `:941–972` | Two endpoints plus at most four iterations; zero area can break early. Initial computed next K is range-tested; subsequent iterations are not guarded by that same check. | `6 * D` |
| LINEAR_FITTING `:974–1033` | Two endpoints, midpoint, optional default point, zero-crossing point. Bad endpoint ordering/near-equal area can abort. No unbounded retry loop. | `5 * D` |
| OS_ACCEL / OS_DECEL / OS_ACCEL_DECEL `:1035–1107` | Default K, lower K, upper K, midpoint. Fits select/fallback/clamp a result without another measure. | `4 * D` |

The ceilings assume the stated valid parameters and count only these direct
helpers. They are not a common safe cap across unknown parameters, repeated
invocations or outer workflow retries. An unrecognized algorithm has no matching
measurement branch, but setup/heating/events and final actions can still run;
it is not a harmless no-op. No new algorithm or macro is allowed by the bridge.

## Aborts, heat, cleanup and physical limits

- `:352–365,384–408,431–442`: cancel/runout/tangle handlers set shared abort
  state. Preparation has no abort check; the loop checks before individual slow/
  fast requests and raises afterward. Its final tail has no abort check. These
  are checkpoints, not guaranteed immediate physical stopping. Already queued
  motion or a preparation after an intervening event is not disproved.
- `:410–460,907–912`: each measure moves to discard and waits for its selected
  heater target; measurement finally attempts acceleration restoration and client
  finishing, which can itself fail or interrupt later cleanup.
  It then invokes the end-of-measure macro before calculation. A later failure
  cannot undo earlier heat/movement. No per-invocation wall-clock bound follows.
- `fluidd.cfg:1225–1248`: measurement-end commands include fan changes, 170 °C
  target, three-second dwell and cutoff/rough-clean/discard calls. Calibration-end
  includes a 170 °C wait, heater-off and those nested macros with another clean
  action. These effects are outside D; successive measures can heat back up.
  Nested movement/material demand and installed macro identity remain unresolved.
- `:939–940,1109–1190`: begin notification occurs before the inner search try.
  End notification precedes success/fallback persistence, cleaning, abort reset,
  idle movement/wait and heater-off. Out-of-range can save default K and mark
  calibration complete while printing. Other abort/error paths differ; exceptions
  in callbacks/cleanup can interrupt later actions. No unconditional restoration
  of the original K/smoothing/heater target or complete cleanup receipt is shown.
- `toolhead.py:81–92,339–344` and `kinematics/extruder.py:639–644,760–816`:
  calibration events change motion flags; calibration enables pressure advance
  for positive E-only motion and alters junction handling. Heater/extrude-only
  distance/velocity checks remain. However, `_prepare_phase` (`:385–387`) calls
  `set_max_accel(accel)`, whose setter (`kinematics/extruder.py:1305–1308`)
  directly replaces `max_e_accel`. The E-only acceleration limit at `:779–780`
  therefore uses this temporary value, not the prior configured cap; restoration
  is attempted in the measurement finally. This does not prove unbounded executed
  acceleration. These checks do not turn D into a complete motor/material budget
  or attest actual trapq attachment.
- `:108–147,213–249`: the calculator's 30-second join can leave a daemon I/O
  thread alive; it is not an overall motion/cleanup deadline. Debug sample writing
  waits on a child process without a shown timeout. No helper/FIFO was opened.

The class registers command/event handlers (`:273–294`) and has **no get_status**.
Its saved K/environment, current calibration state, resolved parameters/provenance,
search progress and completed cleanup are not exposed by this provider. Do not
guess object fields, read hidden configuration as effective state, or use command
diagnostics as passive reads. Existing current advance/job preference labels
cannot replace these missing facts.

## Consequences, verification and next action

Keep five tools, policy 9, disabled uploads and every existing path/handle,
mapping/material/feed/nozzle, thermal/consumption, hash/time/expiry/serialization/
watermark/no-replay guard. No evidence or acceptance semantics changed, so no
policy increment is warranted. All eight original exports retain their previous
first failures; no original bytes/setup/safety commands are changed.

Inert AST checks verify source identities, provider absence, explicit argument
checks, direct increment expressions and the three search-count ceilings.
Bridge software suites, independent review, builds and full scope/package/
privacy/link/ignore audit are recorded in the
[execution ledger](../superpowers/plans/2026-10-27-flow-calibration-evidence.md).
Neither those checks nor static count arithmetic establish firmware execution,
effective parameters, material suitability or hardware acceptance.

The next independent source question is the hidden second job-parameter
dictionary: trace its **field-specific parsing/defaults, logical versus physical
array selection and reset/reprint/file association** from the saved
`print_task_config.py` loader/setter and its file producer. Earlier job research
already records that the dictionary is not returned by status; do not repeat that
absence check. Determine what provenance/correspondence is still missing without
guessing array mappings or changing the three metadata rejections. Do not repeat
calibrator search tracing, camera/transform snapshots, downloads or live probes.
Readiness remains incomplete, with hardware mutations separately unauthorized.
