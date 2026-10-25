# Per-head extrusion evidence — 2026-10-25

## Established result and scope

The existing status tool now projects each physical head's reported nozzle
diameter/volume type, pressure advance, smoothing time and motion-queue name
presence/physical index. Policy **6** binds all four heads through the existing
repeated observations and refuses policy-1–5 dispatch or uncertain promotion.
Used-head reported nozzle diameter must agree with both the file requirement
and the existing operator nozzle attestation. No tool or G-code form is added.

**No live request occurred in this round.** Reused the historical seven-object
response from **2026-10-25 13:59:41 UTC**, already saved privately for the
[runtime report](2026-10-25-runtime-evidence.md). All four heads reported 0.4 mm,
`standard`, pressure advance 0.02, smoothing 0.04 and explicit null queue name.
This confirms historical availability/types, not current values or hardware
acceptance. Raw/normalized scratch remains ignored under `.tmp/`.

Exactly five tools remain; uploads are disabled locally and by default. No
preparation/upload, G-code, job parameter, print control, camera, calibration or
configuration request was made to hardware. Simulation does not authorize one.

## Transform diagnostic disposition

First checked the already matched source's relevant read registrations and
status providers against the [transform investigation](2026-10-25-transform-evidence.md).
`bed_mesh.py:135–139` registers dump and abort; the latter is an action.
The status and dump providers still omit chain installation/order, effective
fade/lookup/ZFADE and calibration provenance. The dump's `mesh_args` branch can
change configuration. Exclusion status omits its internal next transform, and
tuning-tower has no status provider. No supported passive diagnostic resolving
these gaps was identified in the inspected source. This is not a claim about
every possible vendor facility. No repeated matrix/configuration probe, guessed
field, REA reconstruction or state-changing diagnostic was used as a substitute.
The independent head-extrusion contract below advances work without revisiting
that dead end; transform/provenance values remain unknown.

## Reused identities and source anchors

Reverified all **20** source-manifest SHA256/Git-blob identities, including
`klippy/kinematics/extruder.py` and `klippy/extras/flow_calibrator.py`; inspected
Klipper release files still equal extracted artifact bytes. Release source is
pinned to `bc271fb351f8c3ad84300e652e46fd93c53b9de1`, artifact version
`2.0.0.205_20260914173503`. The [Orca report](2026-10-25-orca-u1-gcode.md)
owns artifact identity. No new download/discovery or target-code execution.
Agreement does not attest loaded live bytes or calibration history.

Two additional files were verified against the existing artifact manifest,
without claiming independent public-source comparison:

| Artifact-only file | Bytes | SHA256 |
| --- | --- | --- |
| `filament_feed.py` | 103,299 | `fa4d6cb5a1bd92338d234d9a8de6a105e08aa7d2e95a8c5119e02172ab079d43` |
| `filament_parameters.py` | 73,910 | `7af7b9537a1b6e202aae41a7cd95d2b414d2cee1f2fc3e416610529d6dcba7e4` |

### Reported nozzles are persisted software settings

`extruder.py:30–31,425–443` defines supported nozzle sizes/volume types and loads
per-head persistent configuration, which can replace the original config size.
`:1151–1176,1179–1240` updates these settings through control handlers; it does
not measure the physical nozzle. Those endpoints remain unavailable through
the bridge. `:729–752` adds the stored diameter/volume type to heater, park,
offset and stepper status. A label and a physical operator attestation therefore
remain separate evidence sources; neither is silently substituted for the other.

The bridge normalizes exact finite numbers from {0.2, 0.4, 0.6, 0.8} mm and the
fixed `standard`/`high_flow` enum. Unknown forms stay null/missing. For each
actually used mapped head, the reported size, file size and operator-attested
size must all agree; otherwise `nozzle_mismatch`. An unused head can report a
different supported size without inventing file demand, but its value still
participates in receipt binding. No material suitability claim follows merely
from knowing nozzle volume type.

### Pressure advance is distinct from saved calibration K

`extruder.py:305–308` exposes stepper `pressure_advance`, `smooth_time` and
`motion_queue`. `:326–343` updates reported advance/smoothing when scheduling a
lookahead callback; it is not a measurement or proof that every queued physical
step already uses those values. `:352–378` also allows the G-code setter to
return without applying a request while job flow calibration is enabled.

`flow_calibrator.py:250–260,306–326,606–617` separately loads `_current_k` and
applies a saved head value. The class has no `get_status` or supported read
registration for that dictionary. Thus reported advance is not saved K, its
calibration provenance or the value a future PRINT_START will apply. Do not
infer saved K from current advance or invoke a calibration/apply command as a
read. All such stock macros remain refused.

Normalization accepts exact finite nonnegative advance up to 1e6 (a resource
policy, not a physical safety limit) and smoothing in [0, 0.2] seconds, including
zero. Booleans, strings, nonfinite values and out-of-range forms stay unknown.

### Queue name does not attest stepper attachment

`extruder.py:277,305–325` initializes `motion_queue=None`; explicit sync later
updates both trapq and name, while explicit detach clears both. Crucially,
`:479–484` directly attaches the head's own trapq during construction **without
updating the name**. A null report can therefore describe either this normal
constructor path or an explicit detach. Reading it cannot distinguish them.
Nor does a name independently attest current C-level trapq or running code.

`motion_queue_named=false` means an explicit null name was reported, and the
projected physical index is null. A canonical `extruder`/`extruder1`/`extruder2`/
`extruder3` name gives true plus 1/2/3/4. Missing or malformed gives null and a
fixed missing-field code. No raw arbitrary name is published, no attachment
boolean is fabricated, and a named different head alone is not labeled a
contradiction. Actual trapq attachment remains an explicit unestablished
dependency. No queue-sync/detach command is newly accepted.

### Hidden thermal/feed demand remains unbounded

Artifact `filament_feed.py:513–515,682–714` keeps the attempt limit as an internal
configuration value and resolves load heat/softness from job vendor/type/subtype
plus nozzle diameter/volume type, with fallback branches. `:1611–1641` status
only exposes per-channel presence, auto-disable, state/error/action fields; it
omits the retry limit, resolved temperatures and motor/purge distances.
Artifact `filament_parameters.py:1612–1613` returns an empty status dictionary;
`:1635–1779` resolves temperatures/flow from separate nozzle-specific loaded
tables, material keys and fallback logic. A type label does not establish the
selected table's values. Configuration loading/updating is not a passive read.

The [startup report](2026-10-25-startup-toolchange.md) traces motor stages,
20/30 mm feed strokes, retries, default 80 mm flush and repeated direct-E flow
measurements. Collecting nozzle/advance reports does not bound those branches,
saved K, purge demand, thermal limits or per-job completion/replenishment flags.
These remain unknown; no stock macro becomes a no-op or accepted command.

## Receipt enforcement and verification

No route/object query was added: existing head reads already return this subset.
Fixed public fields and missing codes omit raw labels/configuration. Missing
evidence on any head blocks preparation. Normalized values join the existing
runtime digest and repeated-read checks around materials/job evidence,
destination preflight and remote bytes. Drift blocks dispatch or leaves an
already dispatched outcome unknown; reconciliation never replays a POST.
Ordered source times and the persisted watermark, expiry, locks, file handles,
path/root, mapping/feed/material, temperature and consumption guards remain.
Optional head-model defaults only deserialize historical receipts. Policy 6
prevents policy-1–5 dispatch/promotion even if remote hashes match after restart.
HTTP reads remain non-atomic; equal values cannot exclude intervening changes,
stale peer data or another client. No physical-readiness claim is introduced.

Tests first reproduced absent normalization/nozzle enforcement and old-policy
reuse. A separate failing run reproduced all 20 field/phase drift cases through
actual coordinator behavior before implementation. Synthetic malformed/null and
nozzle tests, loopback HTTP/actual MCP schema and restart tests now exercise the
expanded contract. Final full-suite/review/audit results belong in
[project state](../../PROJECT_STATE.md) and the
[execution plan](../superpowers/plans/2026-10-25-head-extrusion-evidence.md).

Complete suites passed **403 tests each on Python 3.11.14 and 3.13.12**; Ruff
check/format and wheel/source builds passed. Independent fresh-context review
found no actionable findings, separately passed all 403 tests on Python 3.13.12,
50 malformed/privacy cases and canonical queue projections, and checked source/
artifact/historical evidence identities. Audit covered 54 files, 104 local links,
both archives and 14 ignore samples without configured private-literal or
generated-artifact matches. Hardware/physical acceptance was not judged.

All eight original hashes/byte lengths and first refusals were rechecked:
01–04/08 fail `unsupported_command` at EXCLUDE_OBJECT_DEFINE; 05–07 fail
`job_requirements` for one-entry material/consumption vs four-entry nozzles.
No bytes, setup/safety commands or metadata mappings were changed. Startup,
transforms, hidden demand, pause/end/camera and metadata remain blocking.

Next nonduplicative safe work: trace firmware-matched pause/end configurable
callbacks and job flags into a bounded supported read contract, including which
values are actually exposed and which remain private/unavailable. Do not repeat
head/mesh snapshots or guess saved K/feed temperature from current reports.
Hardware upload acceptance still requires separate authorization and proves
transfer only; start always additionally requires the selected plate and fresh
human installed/clear-bed confirmation. Full readiness remains unestablished.
