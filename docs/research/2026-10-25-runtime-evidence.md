# Bounded runtime coordinate evidence — 2026-10-25

The subsequent [transform follow-up](2026-10-25-transform-evidence.md) adds a
focused exclusion read/binding under policy 5 and traces lifecycle limitations.
Policy-4 and seven-object-only statements below describe this earlier milestone.

## Established result

One bounded live **GET** for `toolhead`, `gcode_move`, `extruder`, `extruder1`,
`extruder2`, `extruder3` and `bed_mesh` returned all seven objects. The observation
window was **2026-10-25 13:59:41.102857–13:59:41.218730 UTC** (08:59:41 CDT).
The uncompressed response was 16,110 bytes, below the 256 KiB limit, within a
five-second total deadline; no redirect or automatic retry was allowed. Raw data
and offline normalization are ignored. This was the only new live request.

The existing `u1_status` now collects and normalizes that reported subset.
Preparation and upload bind it under **policy 4**, compare repeated observations,
and refuse missing, inconsistent, changed or backwards-time evidence. Exactly
five tools remain. Uploads remain disabled locally and by default. No G-code,
upload, job parameter, camera session, print control, calibration or configuration
operation was sent to the printer; no live preparation was attempted.

**No command, macro or intact normal export is newly accepted.** These are reported
fields and conservative change checks, not a calibrated motion envelope, complete
transform model, running-code attestation or hardware upload/print acceptance.

## Availability, types and consistency

| Object/field | Observed form | Meaning and limit |
| --- | --- | --- |
| `toolhead.homed_axes` | Empty string | No axes reported homed in this observation. Empty is known, distinct from missing. It does not invalidate earlier historical printing evidence. |
| `toolhead.extruder` | `extruder1` | Reported selected physical head 2; does not prove a physically gripped head. |
| `toolhead.position`, `axis_minimum`, `axis_maximum` | Four floats each | Commanded machine-side position and reported kinematic limits, not measured carriage position or a validated firmware-owned path envelope. |
| `gcode_move.position`, `gcode_position`, `homing_origin` | Four floats each | Last position through the move-transform interface, G-code position, and global homing origin respectively. This is not one homing origin per physical head. |
| `absolute_coordinates`, `absolute_extrude` | Booleans | Reported XYZ/E modes. No string/integer coercion. |
| `speed_factor`, `extrude_factor` | Floats | Reported speed override and extrusion factor; source converts internal speed factor by 60. |
| Four `extruder_index` fields | Integers 0–3, matching names | Physical API index consistency, separately from logical mapping. |
| Four `extruder_offset` fields | Three floats each | Effective reported XYZ offsets. Source can substitute `[0,0,0]` when its internal offset is unset; even a well-typed zero does not prove calibration. |
| `activating_move`; park/active/grab pins | Booleans | Per-head reported state, not independent physical inspection. |
| Per-head `state`; `real_extruder_stats` | Fixed park state; `[name, integer]` | All four reported `PARKED` and the repeated aggregate report was `[extruder1,1]`: all parked, no reported gripped tool. Code 0 means source-reported activation, 1 all parked, 2 unresolved. |
| `bed_mesh.profile_name`, extrema, matrices | String; two-float extrema; 11×11 probed and 31×31 interpolated matrices | A populated `default` profile was reported. Public results expose profile/matrix digests and dimensions, not arbitrary profile labels or saved profile contents. Populated does not attest an installed/sole move transform. |
| `base_position`, per-head `homing_origin`, mesh `fade_start`, `fade_end`, `tool_offset` | Absent | Remain unestablished. No zeros, calibration provenance or complete transform chain are inferred. |

All four physical indices and aggregate activation reports agreed. The selected
head's reported offset matched the global origin's XYZ at that instant; the
normalizer does **not** require that relation for every state. Toolhead and
gcode-move XY agreed, while Z differed by about 0.001216 mm. The source permits
different transformed/untransformed positions; equality is not a consistency
requirement and the difference alone does not establish which transform caused it.
Homed-axis, offset and matrix reports can coexist without establishing motion
safety. No movement was requested to test them.

## Source, configuration and calibration provenance

This work reused `.tmp/u1-profile-research/`, the vendor firmware artifact for
observed version `2.0.0.205_20260914173503`, and release source pinned to
`bc271fb351f8c3ad84300e652e46fd93c53b9de1`. All 20 existing source manifest
Git-blob/SHA256 entries were reverified. Existing version/configuration evidence
is historical and was not re-fetched. Neither it nor this query attests which
Python bytes the running process loaded. Artifact identity and macro comparison
remain in the [prior report](2026-10-25-orca-u1-gcode.md).

Relevant matched anchors:

- `toolhead.py:625–638` merges kinematic status and emits commanded position and
  selected object. Artifact `corexy.py:98–104` emits homed axes and axis limits.
- `gcode_move.py:91–109` obtains G-code position by subtracting base from last
  position and dividing E by extrusion factor; it emits homing origin and modes,
  not raw base position or transform-chain identity. `:80–89` allows replacing
  the move transform. Position field names must not be collapsed into one frame.
- `extruder.py:562–572` prefers backup base positions to configured ones;
  `:705–728` derives relative offsets; `:729–755` emits reported offsets and
  activation fields. The zero fallback at `:740` cannot establish provenance.
  `:830–854` distinguishes selected object from aggregate physical activation.
- `park_detector.py:70–85` derives fixed park-state strings from pin reports;
  optional/ignored active-pin configuration affects that derivation. Pins and
  derived state are retained without inventing a new electrical truth table.
- `bed_mesh.py:248–277` emits the current profile, matrices and extrema; its
  empty sentinel is empty name, zero extrema and `[[]]` matrices. `:154–243`
  uses additional fade, tool-offset and interpolation/splitting state not exposed
  in those fields. Saved profiles are not evidence of an applied transform.
- `extruder_config_bak.py:67–107` reads backup base positions from a separate
  persistence file. The existing `configfile` reply includes an empty backup
  section and park geometry options, but no per-head base positions. It does not
  expose that file's contents or prove which values were used in this process.

Additional artifact-only files rechecked against the existing artifact manifest
(not independently claimed to match downloaded public source):

| Source | Bytes | SHA256 |
| --- | --- | --- |
| `park_detector.py` | 5,045 | `f748abab39b254a07cd4f1d1a6bec7b01b5e8f94fea0d8a440025c6107dceefe` |
| `corexy.py` | 5,089 | `47a83a9e103b57ee0e5b673b7ec08b28352c24ddcee26503688749e4181b63ac` |
| `extruder_config_bak.py` | 12,758 | `56be84ec9b7f30cfa496e86591fe5e767ce79d716fd93fdf112dabc25001e5da` |

Historical mapping/material evidence establishes the object names and 32-slot
contract, not today's loading or mapping. New preparations still read fresh
mapping/material/feed evidence; no live preparation or receipt used the old
snapshot. No source download, paid graph rebuild, new REA reconstruction or
target-code execution was necessary: the narrow contracts were in matched Python.

## Implemented normalization and receipt contract

The fixed status query adds `gcode_move` and `bed_mesh`; no user-supplied object,
endpoint or field query is added. Other read/failure/size/deadline rules remain.
Typed output includes known fields, nulls, fixed missing-field/inconsistency codes
and an explicit list of unestablished dependencies. Signed finite vectors have
exact lengths; booleans/numeric strings are refused as numbers. Normalization
bounds magnitudes at 1,000,000 and each rectangular matrix at 128×128; these are
resource/representation limits, **not** physical safety limits. Profile input is
bounded to 256 characters and hashed. Hashes cover normalized complete current
matrices; saved profiles and arbitrary extra fields are excluded. An empty mesh
is distinguished from a missing/malformed or contradictory report.

Preparation requires the supported subset with no missing fields or identified
inconsistencies. It reads runtime with status, reads materials, then reads runtime
again with job identity. Normalized runtime values must agree, and source event
times must satisfy runtime-start ≤ materials ≤ runtime-end. Event times are
metadata outside the state digest, so an equal later observation remains usable.
The public preparation records the normalized subset, local observation window,
both source event times and `atomic_across_requests=false`. Unexposed dependencies
remain explicitly unestablished even when this subset is complete.

The private evidence digest binds this entire normalized subset alongside the
existing policy, printer/job identity and mapping/material/feed/nozzle evidence.
Upload rechecks it before and after destination preflight and before and after
the remote byte/hash read. Source times cannot go backwards relative to bound
preparation or dispatch/reconciliation observations. The latest successfully
collected time watermark is persisted even when a reconciliation finds no file.
Runtime drift before dispatch rejects; after dispatch it stays unknown without
another POST. Policy 4 refuses policies 1–3 for new dispatch or uncertain-result
promotion, including matching remote bytes. Historical terminal results retain
their original observation/expiry; they are not refreshed by repeated IDs.

These reads are **not atomic**, including fields obtained in one HTTP query.
Repeated equal observations can miss intervening changes (ABA), later motion,
cached peer responses or another client's action immediately afterward. A
nondecreasing timestamp does not prove authenticity or freshness of all fields.
This is a conservative binding of reported evidence, not a global printer lock,
running-code attestation or permission to execute unresolved setup/transform paths.

## Corpus, verification and remaining step

All eight intact export bytes and SHA256 values were rechecked unchanged.
01–04 and 08 still first fail `unsupported_command` at EXCLUDE_OBJECT_DEFINE;
05–07 still first fail `job_requirements` because one-entry consumption/material
metadata conflicts with four-entry nozzle metadata. No metadata is replicated or
guessed. Resolving those first errors still leaves the startup, toolchange,
calibration, transform, hidden thermal/consumption, pause/end and camera chains
in the [startup/toolchange report](2026-10-25-startup-toolchange.md) unbounded.

Synthetic tests cover signed/unknown fields, zero fallback interpretation,
all-parked selection, matrix/type/size failures, private extra fields, changed
offsets/mesh/modes/origins/positions/homing/selection, observation races and
backwards/stale source times. Actual MCP/loopback HTTP tests cover discovery and
schemas, preparation evidence, drift refusal, old-policy restart refusal and
uncertain reconciliation without replay. Existing path, consumption, thermal,
material/feed, mapping, hash, expiry and serialization tests remain. Final counts,
independent review and audit results are recorded in PROJECT_STATE.md.

Independent review reproduced two additional source-backed contradictions:
status-1 aggregate name differing from selected toolhead, and empty-name/empty-
matrix mesh with nonzero extrema. Both were reproduced by failing normalization
and preparation tests before fixes; both now return inconsistency and refuse
preparation. The final complete suites pass 300 tests on each of Python 3.11.14
and 3.13.12; Ruff and both builds pass. The reviewer ran the complete pre-fix
295-test suite; post-fix verification was performed by the implementer. No finding
was deferred. Full transform/calibration/hardware acceptance remains outside
these software results.

The smallest next evidence task is a **focused source/read-only contract for the
active transform lifecycle**, particularly exclusion state and mesh fade/tool
offset/provenance. Determine what an ordinary supported read actually exposes;
keep absent fields unknown. Configuration and another matrix snapshot cannot
alone attest the installed transform chain. The remaining feed/flow/retry/end/
camera chains still require separate bounded contracts before stock acceptance.

Separately authorized hardware upload acceptance remains one uniquely named
validated restricted file, `print=false`, exact response-path/false flags and
remote SHA256, with before/after job/virtual-SD/queue observations. It establishes
transfer only and was not enabled or performed. A print still requires resolved
motion/dependency contracts, specific-plate authorization and fresh human
installed/clear-bed confirmation, followed by separate first-layer/completion/
quality evidence. Milestones remain incomplete.
