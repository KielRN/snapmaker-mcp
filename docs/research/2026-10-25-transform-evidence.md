# Transform lifecycle evidence — 2026-10-25

## Established result

One focused read-only GET at **2026-10-25 15:23:02.528809–15:23:02.829570 UTC**
(10:23:02 CDT) requested only
`exclude_object=excluded_objects,current_object,in_excluded_region`. Its 151-byte
uncompressed HTTP-200 reply reported an empty list, explicit null current object
and boolean false region flag, with no error envelope. This answers availability
and type questions; it does **not** establish that a transform was removed.
No discovery, mesh/configuration reread or second live request was needed.
Raw reply and probe script remain ignored under `.tmp/transform-evidence/`.

The existing status/receipt contract now projects and binds those three fields
under **policy 5**. Excluded/current labels appear only as bounded hashes and
counts/presence. Missing, malformed or drifting reports prevent dispatch or
uncertain-result promotion through the existing repeated-read checks. Exactly
five tools remain; uploads remain disabled locally and by default. No live
preparation, upload, G-code, job-parameter, camera, print-control, calibration or
configuration operation occurred. Slicing remains outside this repository.

**No additional command, macro or intact export is accepted.** This is reported
evidence collection, not a complete movement model or hardware acceptance.

## Source identity and focused lifecycle trace

Reused the vendor artifact for observed firmware `2.0.0.205_20260914173503` and
release source pinned to `bc271fb351f8c3ad84300e652e46fd93c53b9de1` under
`.tmp/u1-profile-research/`. All 20 existing source-manifest Git-blob/SHA256
entries were reverified; the inspected Klipper release files also still match
the extracted artifact bytes. No new source download, REA reconstruction or
target-code execution was needed. Artifact/version/configuration agreement is
historical/static evidence, not attestation of bytes loaded by the live process.
The [Orca report](2026-10-25-orca-u1-gcode.md) owns the artifact identity.

Additional artifact-only files were checked against the existing artifact
manifest, without claiming an independent comparison to public release source:

| File | Bytes | SHA256 |
| --- | --- | --- |
| `tuning_tower.py` | 4,668 | `9efe0d4cb8a8e79f2cc6b6f57f9ecc5a4d13a90664f02b7928aab8ed5ad2878e` |
| `webhooks.py` | 24,958 | `dc2b2539456a103cd37cb1333216682ccb16d3b43a10820d509ea5d4362ad796` |

Anchors below refer to the pinned `klippy/extras/` files unless specified.

### Exclusion state is distinct from transform installation

- `exclude_object.py:39–73`: the first `_exclude_object` request calls
  `_register_transform`, which wraps the current transform through
  `gcode_move.set_move_transform(self, force=True)`. Registration can return
  early while a tuning tower is active. Its internal `next_transform`, per-head
  E offsets/history and five initial extrusion moves are not status fields.
- `:79–100`: reset-file clears object/list/region state before trying to restore
  `next_transform`. Restoration can return early while tuning is active, leaving
  the wrapper installed despite empty lists and false region state.
- `:279–335,378–389`: START/END update the current label; definitions/markers do
  not by themselves install the exclusion transform. Removing one exclusion or
  resetting the exclusion list does not unregister it. Thus identical empty
  reports can follow different transform histories. An exclusion list can also
  be nonempty even when registration was skipped by tuning.
- `:161–277`: moves update internal state, may suppress moves while printing,
  retain/adjust per-head E history, and forward transformed positions. The region
  flag can lag a changed START/END/reset-list marker until a later move. A true
  region flag with null current object or an empty list is not necessarily an
  inconsistent snapshot. No invented membership/region truth table is enforced.
- `:246–253`: supported status exposes only definitions, excluded labels, current
  label and region flag. It omits transform installation/order, E offsets/history
  and initialization counters. The focused query excludes definitions and their
  arbitrary metadata/geometry because they cannot establish the running chain.
- Artifact `tuning_tower.py:48–51,103–109` can itself wrap/restore the chain;
  `is_active` is internal, and this file has no `get_status`. Querying guessed
  tuning/transform fields would not resolve that gap.

`move_transform_installed` therefore stays **null**, including when every queried
exclusion field is known. No active/inactive or removed/installed claim is derived.

### Mesh/profile reports omit decisive runtime values

- `bed_mesh.py:99–154`: bed mesh installs a movement transform during object
  construction, independently of whether a mesh exists. Fade parameters come
  from configuration; a nonpositive fade distance replaces start/end with an
  internal disable sentinel. Configuration values are not direct runtime fade
  state or evidence that this object remains at the head of the chain.
- `:161–243`: `set_mesh` validates/computes the fade target, resets ZFADE tool
  offset, installs the current mesh, initializes splitting and resets the G-code
  last position. `get_position` inverts the Z compensation; `move` applies mesh,
  fade and splitting. Even fully faded moves can add the fade target.
- `:248–277`: status returns a cached profile label, matrices and extrema plus
  saved profiles/probe progress. The current profile name identifies the mesh
  object's label, not calibration time, sensor history, physical correctness or
  an exclusive/active transform chain. Saved profiles are a separate collection.
- `:328–340,1816–1828`: BED_MESH_OFFSET can change XY lookup offsets and ZFADE,
  then reset G-code position without updating the cached status. Consequently
  equal profile/matrix digests can coexist with different effective transforms.
  These commands remain rejected; none was issued to investigate them.
- `:734–884,2156–2183`: probing can build/save a mesh; loading can instead use
  persisted custom profile data or configured saved points and rebuild it. The
  public current label/matrices do not identify which provenance produced it.
- `:342–366,702–714`: the dump endpoint adds mesh parameters, generated probe
  paths/configuration and probe offsets, but still does not expose the running
  chain, effective fade/lookup/ZFADE or calibration history. Supplying `mesh_args`
  can call `update_config`; it must not be treated as an unconditional passive
  read. No dump request was made, and no new endpoint is added to the bridge.

Effective fade/start/end/target, lookup XY offsets, ZFADE, calibration provenance
and loaded-code identity remain unestablished. The prior seven-object observation
already demonstrated that fade/tool-offset fields are absent in status. Repeating
that snapshot or querying nonexistent fields would add no lifecycle evidence.

### Coordinate relationships and limits

| Report | Matched-source meaning | Limit |
| --- | --- | --- |
| `toolhead.position` | `toolhead.py:625–638`: commanded position passed toward kinematics. | No measured carriage location or physical motion/grip proof. |
| `gcode_move.position` | `gcode_move.py:80–112`: last position at the move-transform interface; reset queries that interface's position getter. | Can differ from toolhead position due to mesh, exclusion or another wrapper; no transform attribution from the difference alone. |
| `gcode_move.gcode_position` | `:91–109`: XYZ = last minus base; E = (last E minus base E) / extrusion factor. | Algebra can reconstruct an apparent base from consistent reports, but HTTP fields are not an atomic attested state. No derived base field is introduced. |
| `gcode_move.homing_origin` | `:77–79,183–194,255–279`: global homing position; SET_GCODE_OFFSET updates it and base, while G92 can change base independently. | Not raw base, not four per-head origins and not guaranteed equal to a selected head's reported calibration offset. |

Absolute XYZ commands add base; E also depends on modes and extrusion factor.
Selection/homing/direct moves reset state through the paths traced in the
[startup report](2026-10-25-startup-toolchange.md). Frame equality is not an
acceptance invariant. This follow-up makes no new movement or coordinate-space
safety claim, and does not collapse reported offsets into backup/configured
calibration. Firmware's zero-offset fallback remains a reported value only.

Artifact `webhooks.py:500–552` queries each status provider and projects requested
fields; its common event time does not attest an atomic physical state. HTTP
snapshots, including a single query, remain non-atomic. Repeated equal values
cannot exclude intervening changes, stale peer data or another client's action.

## Implemented collection and receipt binding

The transport accepts only the fixed exclusion field projection; arbitrary field
names, full exclusion-object reads, hosts and endpoints remain unavailable to
tool callers. Both opening status and closing runtime/job snapshots use that
same projection. A peer that returns additional definitions, profile/chain labels
or arbitrary metadata cannot publish them through normalization.

The normalized exclusion record contains excluded count and SHA256, current label
presence and SHA256, reported region boolean and null installation state. Explicit
null current object means known absence; missing or malformed is unknown. Lists
are bounded to 1,024 unique labels and labels to 256 characters. Their sorted
canonical hash binds the exact label set without publishing names; current-label
hash distinguishes changes even when both labels are present. These are resource
limits, not physical safety limits. Booleans/numbers are never coerced to labels
or region flags. Missing/oversized/malformed reports mark fixed missing-field
codes and block preparation. There is no default empty-list success.

Policy **5** binds the expanded normalized record through the existing evidence
digest. Repeated reads bracket materials/job identity, destination preflight and
remote byte verification; field changes prevent dispatch or leave dispatched
results unknown. Source-time ordering and the persistent reconciliation watermark
remain unchanged. Policies **1–4** cannot dispatch or promote uncertain receipts,
including matching remote bytes after restart. No upload is replayed. Historical
terminal results keep their original meaning/time. Optional model defaults exist
only to deserialize historical receipts, not to bypass the policy check.

All path/handle, mapping/material/feed/nozzle, thermal/consumption, file/hash,
expiry, serialization and reconciliation safeguards remain. Known exclusion
reports do not prove complete transform knowledge, and preparation still grants
no print authorization.

## Verification, corpus and remaining evidence

Synthetic regressions first reproduced absent collection/unknown handling,
policy-4 reuse and exclusion changes ignored around preparation/transfer. Actual
MCP subprocesses exercise public schemas, expanded receipts, missing exclusion
refusal, drift/restart no-replay and policy-4 refusal. Final suite, independent
review and audit evidence is recorded in PROJECT_STATE.md and the
[focused plan](../superpowers/plans/2026-10-25-transform-evidence.md).

Complete suites passed **342 tests on each of Python 3.11.14 and 3.13.12**.
Ruff check/format and wheel/source builds passed. Independent fresh-context
review found no actionable findings and separately passed all 342 tests on
Python 3.13.12, checked source identities/claims and probed historical defaults
and malformed reports. Hardware compatibility, loaded-code identity, physical
transform state and calibration validity were explicitly outside its judgment.
Audit covered 51 source/doc files, 89 local links, both archives and 11 ignored
runtime samples, with no configured private-value or generated-artifact matches.

All eight original export hashes/bytes remain unchanged and all are rejected:
**01–04 and 08** first fail `unsupported_command` at EXCLUDE_OBJECT_DEFINE;
**05–07** first fail `job_requirements` because one-entry consumption/material
metadata conflicts with four-entry nozzle metadata. These are first failures
only. Startup/toolchange/calibration, hidden thermal/consumption, transforms,
pause/end/camera and metadata relationships remain unbounded. No setup/safety
commands were removed, metadata guessed or macro whitelisted as a no-op.

The smallest remaining transform evidence is an ordinary vendor-supported,
read-only diagnostic that explicitly reports chain order/installation and
effective mesh fade/lookup/ZFADE together with versioned calibration provenance.
The inspected supported status/dump contracts do not provide that evidence.
Until such a diagnostic is identified and verified, preserve these unknowns;
another matrix/config snapshot or state-changing G-code probe cannot substitute.
Other macro/feed/flow/end/camera contracts still need focused work before stock
profile acceptance.

A separately authorized minimal upload acceptance remains one uniquely named
validated restricted file with `print=false`, exact root/path/false flags and
downloaded SHA256, plus before/after job/virtual-SD/queue observations. It tests
transfer only and was neither enabled nor performed. Printing still needs
resolved motion/dependencies, specific-plate authorization, fresh human installed/
clear-bed confirmation and separate first-layer/completion/quality evidence.
The upload, stock-profile, controls, camera and release milestones stay incomplete.
