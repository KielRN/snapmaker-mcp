# Hidden feed parameter resolution

Date: 2026-10-26. Focused saved-source follow-on to the
[camera-worker investigation](2026-10-26-camera-worker-evidence.md), advancing an
independent stock-file blocker. **No live request**, G-code, configuration read/
write, target execution or hardware acceptance. No production behavior changed.

## Identity and new result

Reused only these two saved artifact files, checked against the existing firmware
manifest. This is not a new comparison to public source or loaded-code attestation.
Historical firmware/release identities remain those in the
[Orca report](2026-10-25-orca-u1-gcode.md).

| Artifact file | Bytes | SHA256 |
| --- | --- | --- |
| `filament_parameters.py` | 73,910 | `7af7b9537a1b6e202aae41a7cd95d2b414d2cee1f2fc3e416610529d6dcba7e4` |
| `filament_feed.py` | 103,299 | `fa4d6cb5a1bd92338d234d9a8de6a105e08aa7d2e95a8c5119e02172ab079d43` |

The [startup report](2026-10-25-startup-toolchange.md) already establishes hidden
feed strokes/retries/flush. The new narrow finding is that **even an individually
present material temperature can be discarded** when later flow-table validation
fails. Reading a built-in temperature row or a reported material/nozzle label
cannot establish the temperature the running feed resolver will return.

## Resolution and rollback anchors

- `filament_parameters.py:1541–1607`: loads five separate nozzle tables with
  create-if-missing behavior; ready handling can replace older/missing versions
  and persist defaults. Loading/updating tables is not a passive evidence probe.
  Static built-ins do not attest the in-memory/configured tables.
- `:1612–1634`: supported status is empty. Search precedence, independently for
  each key, is exact vendor/type/subtype, vendor/type/generic, generic/type/subtype,
  then generic/type/generic. A selected result can mix fallback levels across
  keys; there is no single selected material row/provenance report.
- `:1636–1708`: constructs generic unknown defaults, selects diameter-specific
  defaults/table using narrow open intervals around 0.2/0.4/0.6/0.8 mm; only
  0.4 mm explicitly selects `high_flow`, otherwise the standard table is used.
  Unsupported diameter returns the original generic defaults. Missing/`NONE`
  vendor or main type returns the diameter-specific defaults.
- `:1710–1773`: tentatively resolves load/unload/print temperature, softness,
  K values and flow limits. It then requires positive volumetric speed/process
  acceleration/process slow speed and `fast_v > slow_v`. Any exception in this
  block returns the **earlier diameter-specific default copy**, discarding even
  successful temperature/softness lookups. An outer exception returns the
  original generic defaults. These are actual fallback returns, not errors
  exposed through the empty status provider.
- `:1775–1803`: each temperature/softness/K wrapper reruns the complete resolver.
  `filament_feed.py:682–713,782–783` calls load-temperature and softness wrappers
  separately, with separate job getter calls; no common immutable selection or
  atomicity is established. Missing objects take a separate feed-temperature
  constant and false-softness fallback. Current reports do not identify which
  branch ran.
- `filament_parameters.py:1827–1833`: `FILAMENT_PARA_GET_ALL_INFO` prints all five
  dictionaries. It is a G-code command, outside this investigation's permitted
  passive tools; it supplies neither per-call resolved provenance nor completion.
  No command was sent or added to the allowlist.

These observations do not bound motor demand, retries, cleaning macros, flow
search, saved K, replenishment or action completion. A fallback constant is not a
safe material limit. Do not derive file acceptance from this static resolver.

## Next nonduplicative action

Trace the saved flow-calibrator's **effective parameter precedence and loop/search
termination**, starting `cmd_FLOW_CALIBRATE` and its measurement helpers. Determine
which caller/file/explicit parameters override the resolver and whether all
positive direct-E demand can be bounded across retries, aborts and algorithms.
Use inert source/AST inspection and synthetic bridge fixtures only; do not run
the vendor module, issue diagnostic G-code, reread hidden tables or guess arrays.
Implement a reported-field extension only if a supported, useful exposed contract
is established. Otherwise record the precise missing provider/provenance state.

Policy 9, five tools, disabled uploads and all path/handle, material/feed/nozzle,
thermal/consumption, hash/time/expiry/serialization/no-replay guards remain.
All eight original exports retain their prior first failures. Camera, transforms,
stock-file, controls and honest hardware acceptance remain readiness gaps. Review
and verification belong in the
[execution ledger](../superpowers/plans/2026-10-26-camera-worker-evidence.md).
