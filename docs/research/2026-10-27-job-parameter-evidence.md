# Hidden job-parameter parsing and file association

Date: 2026-10-27 UTC. Saved-source investigation only; **no live request**,
authentication, preparation, upload, G-code, camera, control, job-parameter,
calibration or configuration operation. Runtime, five tools and policy 9 remain
unchanged. No command or intact export becomes acceptable.

## Evidence identity and scope

Continue the [flow-calibration handoff](2026-10-27-flow-calibration-evidence.md)
using the saved artifact for historical firmware `2.0.0.205_20260914173503`.
The [Orca report](2026-10-25-orca-u1-gcode.md) owns the artifact identity and
release pin `bc271fb351f8c3ad84300e652e46fd93c53b9de1`. Check only five relevant
files against the existing artifact manifest; no download, discovery, REA,
whole-image audit or vendor-module execution. `print_task_config.py` and
`print_stats.py` also match the saved pinned public SHA256/Git blobs.

Additional artifact-only anchors, with no independent public-source comparison
or loaded-code attestation claimed:

| File | Bytes | SHA256 |
| --- | --- | --- |
| `virtual_sdcard.py` | 116,736 | `38e769f078ee637c3393008e8d0dbb87dc4261ea1f1cd6ae9061fdb23673dc1e` |
| `klippy.py` | 37,619 | `d7433a2321f31afb431fe3bcd38f62cdd997afd7c2eaef0ab4f90c82bd14c6a9` |
| `queuefile.py` | 10,688 | `fce61a3256e376b566b8676c8b95f9c3082846881995af8cb0369af581938157` |

The [job-preference report](2026-10-26-job-flag-evidence.md) already establishes
that `get_status` omits the second dictionary. No guessed-field or hidden-file
read can turn that absence into supported provenance. This investigation traces
the dictionary's producer, persistence and lifetime, not its current contents.
Anchors refer to saved Klipper files, with extras basenames unless specified.

## Table construction and parsing

`print_task_config.py:65–80,104–115` loads a separate `print_task_2.json` with
32-slot logical arrays. Constructor reset uses the default `is_finish_print=False`
and retains this second table. `_early_check:193–270` checks the first dictionary,
not second-table array lengths/types. `klippy.py:109–160` falls back on missing/
unreadable/non-dictionary JSON and fills missing top-level keys after a successful
load; it does not validate supplied second-table values against their defaults.
Persisted values are neither file identity nor validated current job evidence.

`cmd_SET_PRINT_TASK_PARAMETERS:1091–1456` reads optional arguments, refuses
statistics state printing/paused, copies current first-table preferences/materials,
but rebuilds the second table from defaults and resets the map/use flags. It
requires all four extruder objects and reads their reported nozzle properties.
The command does not take a filename, byte hash, plate or parameter generation.
`SLICER` / `SLICER_VERSION` are read but unused by this method.

`_parse_str_to_list:1072–1077` uses `ast.literal_eval` and requires a list. This
avoids arbitrary expression execution but does not provide bounds or consistent
element validation. These are observed vendor semantics, not bridge input rules:

| Input / anchor | Established treatment |
| --- | --- |
| `MAP_TABLE`, `:1158–1178` | List of logical/physical index pairs; at most 32 pairs. Integer checks and upper limits exist, but no explicit lower-bound, duplicate or alias check. Python booleans satisfy `isinstance(value, int)`; negative indices can use Python indexing semantics. Omitted entries retain the default map. |
| Preference arrays, `:1180–1218` | Flow list identifies physical indices; end-unload list is positional physical-head truth values, truncated to four. Their integer tests also accept booleans. Flow indices lack an explicit lower check. Scalar preference integers have 0/1 parser bounds. |
| Width/height, `:1103–1104,1220–1224` | Optional float parsing with no local min/max; omitted values remain zero. This method establishes no positive finite geometry contract. |
| Type/nozzle/temperature/ratio, `:1226–1286` | At most 32 entries, copied by logical position. Type requires strings; nozzle diameter requires floats, whereas temperature and ratio accept int/float (including booleans). Ratio checks only `>0.001`. Each field's local exception handler logs and replaces that whole array with defaults; it does not necessarily reject the command. |
| Process flow and outer-wall pairs, `:1288–1328` | Default category order is standard/high-flow, reversed only for a leading high-flow/standard pair. One speed/acceleration value replaces standard only; two replace both. Other lengths leave defaults. Defaults are speed 200 and acceleration 5000 for both categories; conversion errors reset both values. These two entries are volume categories, not two physical tools. |
| Max volumetric speed / volume type / usage, `:1330–1390` | At most 32 entries by logical position; numeric arrays accept int/float, volume types require strings without an enum check here. Per-field failure restores the whole array to zero or standard. There is no local nonnegative/finite bound for usage or volumetric speed. |

The default `filament_diameter` array is never populated by this setter. A
partially invalid field can erase earlier valid entries in that field while
other fields survive. A parse acknowledgment cannot establish exact requested
parameters, full demand, safe ranges or unchanged persistent state. Do not copy
these permissive semantics into the bridge or execute the command as a probe.

## Logical roles do not resolve export metadata

- `:1393–1396`: either logical grams or millimeters strictly above `0.0001`
  marks the mapped physical head used. Aliases aggregate only the boolean use
  flag here, not a physical material-demand sum.
- `:1398–1405`: if a nozzle argument was supplied, every used physical head is
  compared with **logical nozzle entry zero**, within `0.001`. It does not compare
  each head with its corresponding logical entry. This consumer's behavior does
  not establish whether a slicer header's four nozzle entries describe tools,
  logical filaments or another producer convention.
- `:1407–1421`: supplied volume types are instead checked by logical index and
  mapped physical head; actual high-flow permits a differing requested type.
  The skip condition uses both usage values below the threshold, while used-head
  marking uses strict above. These are different conditions at equality.
- `:1423–1440`: compatibility checks use current first-table physical material
  vendor/type/subtype and actual reported nozzle properties, not the hidden
  logical filament-type array. Effective resolver/material suitability remains
  a separate dependency documented in the [feed report](2026-10-26-feed-resolution-evidence.md).

All eight original exports remain byte/SHA256-identical and rejected: 01–04/08
first fail `unsupported_command` at EXCLUDE_OBJECT_DEFINE; 05–07 first fail
`job_requirements` for one-entry consumption/material versus four-entry nozzle
metadata. These are first failures only. No producer correspondence, array
broadcast, setup removal or macro no-op is inferred from the vendor consumer.

## Reset, reprint and selected-file ordering

| Anchor | Established behavior and limit |
| --- | --- |
| `print_task_config.py:403–445` | Ordinary reset clears current mapping/use and selected preferences while retaining the second table. Finish reset additionally replaces/persists the second table with defaults. Reset of reports does not prove physical cleanup. |
| `:447–477` | Reprint apply/capture copies seven first-table fields, including map/use and selected preferences. It neither captures nor restores the second table, a filename or byte hash. |
| `:479–489` | At work start, if no physical use flag is true, derive use from logical **grams >0** only. This differs from the setter's grams-or-mm `>0.0001`; it does not scan G-code or aggregate consumption. Then back up physical material and capture first-table reprint fields. |
| `print_stats.py:158–183` | Complete/error/cancel handling calls finish reset before checking whether a print start time exists. The second table can be cleared without an established print having started. |
| `virtual_sdcard.py:361–405` | The with-parameters start path calls the setter before `_reset_file`, filename retrieval/validation, prestart macro and file open. A later failure need not undo assigned/persisting parameters. This path is a start operation, never a passive parameter calculator. |
| `:298–306,490–512`; `print_stats.py:102–104,299–313` | Ordinary SD reset and file selection reset statistics/print-job calibration flags. These paths do not themselves reset or bind the second table. File selection records the filename after opening, not a hash-to-parameters receipt. |
| `virtual_sdcard.py:541–569,1910–1920,1952–1958` | Worker start captures new-print info before seek/state/start; power-loss recovery applies first-table reprint info before reopening with `reprint=True`; its failure path uses ordinary reset. Neither path establishes second-table/file correspondence. Full recovery/motion effects are outside this trace. |

The plain start path `virtual_sdcard.py:319–357` does not call the parameter
setter. Do not assume a new file selection reconstructs hidden parameters from
its G-code. The earlier [flow report](2026-10-27-flow-calibration-evidence.md)
documents how the calibrator can consume retained hidden values while printing/
paused; visible job preferences do not attest those values or their origin.

## Persistence is enqueue acceptance, not an atomic job receipt

`print_task_config.py:1442–1447` assigns both in-memory dictionaries before two
separate persistence calls. False persistence results are logged, not rolled
back. `klippy.py:162–185` serializes and calls `queuefile.async_write_file` with
`safe_write=True`, then reports success on enqueue. The calls do not form one
transaction with each other or with file selection.

`queuefile.py:14–34,45–96,156–193` creates nonsynchronous operations and enqueues
without waiting. The worker writes a temporary file then replaces one target;
later failures are delivered only for synchronous operations. This path has no
completion future or successful-disk-write receipt for its caller. Per-file
replacement does not establish pairwise atomicity, crash durability or a bound
selected-file association. No write or queue worker was invoked to investigate.

## Outcome and next distinct contract

The bounded setter/table/persistence/reset trace is closed absent changed
evidence. Supported status still lacks the effective second table and its
validated, file-bound provenance; repeated equal preferences cannot establish
it. No useful new exposed contract was established, so runtime/policy/fields,
all prior safeguards and disabled uploads stay unchanged. Transform chain/
effective mesh/calibration, full hidden demand, hooks, camera lifecycle and
hardware acceptance remain unresolved; readiness remains incomplete.

Next locate the **upstream file-metadata-to-parameter producer**, rather than
repeat the consumer or query hidden files: use saved client source/tree and
targeted preprint/metadata call sites to identify where raw export cardinalities
become setter arguments. Follow only a specific missing producer contract;
record unavailable artifacts instead of rebuilding the whole application. No
new live query, guessed array mapping, parameter mutation or start is authorized.
The [execution ledger](../superpowers/plans/2026-10-27-job-parameter-evidence.md)
records independent review, software verification and integration gates.
