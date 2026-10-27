# Desktop connection and metadata producer evidence

## Result and scope

The ordinary desktop workflow was inspected under D026. Snapmaker Orca was
running but disconnected. Its normal device discovery found the U1; one Connect
action opened a request to authorize binding on the printer's touchscreen.
The request expired and the UI reported **Binding rejected**. This does not
distinguish an explicit rejection from expiry. No connected device/preprint or
camera view was reached, and no upload, job-parameter, print/control, calibration
or firmware/configuration action was selected. Discovery/binding may exchange
protocol requests; no wire capture was collected or exact request count claimed.
This is new UI evidence on 2026-10-27, not a successful hardware acceptance test.

The independent metadata-producer trace is now closed for the inspected sources.
The server preserves independently parsed array lengths. The preprint client can
instead pad/truncate consumption for display and fall back to a first nozzle.
Neither path proves a file-bound effective parameter table. Policy 9, five tools,
default/local upload disablement and all eight export refusals remain unchanged.

## Evidence identity

Reused the saved image identified in the
[firmware report](2026-10-25-orca-u1-gcode.md), corresponding to historical
firmware `2.0.0.205_20260914173503`. Extracted only three previously missing
Moonraker producer modules, without executing vendor code or downloading the
image again. Each matches the already pinned public tree
`a308cfae31b7eb70ebf96bc73e6968d9792e4d73` byte for byte. Only the two missing
public modules were fetched; the third public copy was already saved.

| Module | Bytes | Git blob matching image |
| --- | --- | --- |
| [metadata.py](https://github.com/Snapmaker/u1-moonraker/blob/a308cfae31b7eb70ebf96bc73e6968d9792e4d73/moonraker/components/file_manager/metadata.py) | 50,748 | `ea053eb6e37993dac3ff386373622fa7ebb5cabf` |
| [klippy_apis.py](https://github.com/Snapmaker/u1-moonraker/blob/a308cfae31b7eb70ebf96bc73e6968d9792e4d73/moonraker/components/klippy_apis.py) | 22,224 | `20e73cd65acbaf8cdb27d15b11ea1082eba23487` |
| [snapmakercloud.py](https://github.com/Snapmaker/u1-moonraker/blob/a308cfae31b7eb70ebf96bc73e6968d9792e4d73/moonraker/components/snapmakercloud.py) | 77,553 | `cb593118338c42458bbfdca150a17cf34425579c` |

SHA256 respectively: `07c1e72d9f0cbcc2d6dfc3021c1b1bd9c6727ec20c2623463e1722cd3e756c7a`,
`b16eb19f9f2237eb0d1cae08c8cfc1e245619a2f0b5e910c0798bf7379800e7d`,
`3a6ab1ccbdd2cf8e241eb5f614068e7a064cb6904e0fdc7d8b1381220e312523`.
Rechecked the saved Snapmaker Orca 2.4.0 JavaScript bundle against the
[camera report's identity](2026-10-24-camera.md): 5,967,127 bytes, SHA256
`17ccfb0c7cecdd4fc146c4018b414fc6b4011a9858813aafc2e02bc48dd24dcb`.
These are static artifact/source identities, not live loaded-code attestation.
Raw extraction, AST checks, UI notes and integration receipts remain ignored in
`.tmp/desktop-metadata-evidence/`; machine identifiers are not published here.

## Server: raw metadata becomes start parameters

- `metadata.py:407–429` recognizes Orca/Snapmaker Orca with the Prusa-family
  parser. `get_slicer:1268–1295` uses first/tail text windows with
  `READ_SIZE=1,048,576`;
  `extract_metadata:1297–1315` calls each supported parser independently.
- Grams (`476–482`), millimeters (`633–639`), material string (`500–501`) and
  nozzle list (`573–579`) come from separate footer patterns. There is no common
  cardinality check or broadcast in these methods. The numeric helper (`67–76`)
  extracts unsigned decimal substrings/`nil`; it is not a strict signed/exponent
  token validator and must not replace bridge validation.
- `_fill_metadata:288–317` in `klippy_apis.py` maps `filament_weight` to
  `FILAMENT_USED_G`, splits material on semicolons (empty entries become `NONE`),
  and includes available raw values for a fixed list of 19 fields. Lists use
  Python string representation. It neither aligns the nozzle/consumption arrays
  nor reads back the resulting hidden table.
- `start_print_advanced:347–379` builds
  `SDCARD_PRINT_FILE_WITH_PARAMETERS`, appends uppercased option names/string
  values, then metadata. Options and metadata can therefore supply duplicate
  names. This builder provides no bridge-grade typed allowlist or value escaping
  for those inputs. Do not copy it into a future bridge control tool.
- The same method schedules MD5 logging separately, before reading cached file
  metadata and submitting G-code. That background log is not an atomic SHA256/
  metadata/selected-file receipt. A returned G-code result and the subsequent
  `job_start_complete` event do not prove the expected active file/SD state.
- `snapmakercloud.py:205–235` forwards local-file options/plate to its handler.
  Its G-code path (`1581–1645`) checks availability, waits for or requests missing
  metadata, then invokes `start_print_advanced`. This establishes the static
  producer-to-setter route alongside the
  [previous consumer trace](2026-10-27-job-parameter-evidence.md), not effective
  installed parameters, a complete material budget or safe motion acceptance.

Metadata extraction also has a conditional file-rewrite path:
`extract_metadata:1302–1305` can call `process_objects:1223–1266` when object
processing is requested and supported object markers are present. That function
writes preprocessed G-code to a temporary file and moves it over the selected
file, then extraction rereads it. This is not a passive parsing guarantee.
Installed enablement and whether a particular export takes this branch were not
observed. Keep post-upload remote SHA256 verification and reject changed bytes;
never normalize or preprocess an original export to bypass bridge validation.

## Client: display fallback is separate from submission

Saved bundle anchors:

- `139177–139230`: file-task metadata comes from `server.files.metadata` for a
  nonempty filename. Color is renamed, weight is also assigned to `filament_used`,
  and selected string fields split on semicolons.
- `150031–150079`: `aqa` sizes consumption from the material-list length. Grams
  are padded with zero/truncated by `V4/E3`; present millimeters use `-1` fallback.
  If millimeter metadata is absent, the client assigns the grams list to that
  display field without unit conversion. These are vendor display semantics,
  never valid bridge consumption rules.
- `150080–150095`, `150404–150473`: nozzle keys have explicit priority, and file
  display entries choose the corresponding nozzle when present, otherwise the
  first available nozzle. This does not establish physical array correspondence.
- `151632–151655`, `151785–151789`: submission options copy preferences and add
  mapping pairs from current selection; a noninteger target becomes `-1`.
- `38840–38896`, `39647–39712`, `139680–139716`, `137766–137781`: the local-print
  path passes options to `server.files.start_local_print` under its version gate.
  A compatibility path writes mapping/used-head/preferences G-code before plain
  start, including a fallback for one particular failure code/message. This is
  not an operation journal or reconciliation contract. Never adopt that retry
  pattern for an uncertain bridge mutation.

The server, rather than these display entries, supplies cached metadata to the
with-parameters G-code call. A synthetic one-material/one-consumption/four-nozzle
example therefore remains unequal at that boundary. Following the complete
producer route does not justify dropping nozzle entries, broadcasting material
or guessing physical mapping in exports 05–07. All original bytes remain intact.

## Acceptance blocker and next action

Complete the vendor touchscreen LAN authorization during an attended connection
attempt, then inspect the connected device and ordinary preprint workflow for
one documented very small diagnostic plate. Do not repeatedly request pairing
in unattended runs or change authentication/configuration to bypass it. No
diagnostic file/plate was selected in this run, so no dimensions/time/material/
physical-tool or clearance claim is made. Obtain current human installed-plate/
clear-bed confirmation before any start; the earlier clear-bed statement does
not establish current installation or uninterrupted physical state.

Close this source trace unless changed evidence presents a specific new question.
Transform provenance, complete stock-file effects/demand, effective parameters,
controls, camera lifecycle and honest hardware acceptance remain incomplete.
