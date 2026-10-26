# Machine/action evidence — 2026-10-26

## Established result

The existing five-tool bridge now projects only
`machine_state_manager=main_state,action_code` through both runtime queries.
**Policy 8** binds the two independent reported integer codes to preparations and
upload receipts. Both must explicitly be **0 (IDLE)** before positive idle or
preparation. Any recognized nonzero main state or action independently makes the
printer busy, including when the other report is missing. Missing, null, malformed
or unfamiliar codes remain unknown. Existing positive printing/paused/active-SD/
saved-pause reports still make the printer busy even without machine reports.

One fixed bounded passive GET at **2026-10-26 05:46:40.076982–05:46:40.511219 UTC**
reported exact JSON integers **main_state=0, action_code=0**. This establishes
availability and forms on the installed setup only. No discovery, configuration
snapshot, second probe, live preparation/upload, G-code, camera session/control,
job-parameter, calibration or configuration mutation occurred. Uploads remain
disabled locally and by default. Raw results remain ignored under
`.tmp/machine-state-evidence/`.

No new tool, command, macro or intact stock export is accepted. These are reported
labels, not proof of physical quiescence, successful transitions, drained queues,
loaded hook identity or safe print/control execution.

## Artifact identity and supported provider

Reused the vendor artifact for historically observed firmware
`2.0.0.205_20260914173503` and release source pinned to
`bc271fb351f8c3ad84300e652e46fd93c53b9de1`. Reverified all 20 source-manifest
SHA256/Git-blob entries and matching extracted Klipper files, plus the five
artifact-only entries in the [pause/end report](2026-10-25-pause-end-evidence.md).
The [Orca report](2026-10-25-orca-u1-gcode.md) owns artifact/version identity.
No download, REA reconstruction or target execution was needed. Historical/static
agreement is not loaded-code attestation.

Anchors below refer to extracted `klippy/extras/` files. In particular,
`machine_state_manager.py` is **artifact-only** evidence (17,849 bytes, SHA256
`8e63a052b2e0ba02d111e59658d4a0af237ec9851817687cd6424ded667f7ccc`),
not independently compared public release source.

| Provider / source | Established semantics | Limits |
| --- | --- | --- |
| `machine_state_manager.py:9–94` | Main-state integer members 0–14 cover idle, printing, calibration, leveling, upgrading, abnormal and feed operations. Action members cover idle, homing, plate detection, preheat, print restore/resume/feed/check, cleaning and calibration stages. | Main and action are independent enums; do not derive a strict pair compatibility table. Unknown future integers are not silently accepted. |
| `:167–181,329–333` | Constructor sets both labels to IDLE; shutdown attempts ABNORMAL. Supported `get_status` returns only main_state/action_code without issuing G-code. | Constructor defaults and reported labels do not prove physical idle. The getter omits transition locks, history, rule sets, hook identity and completion. |
| `:192–207,336–389` | Action can change independently; optional main-state verification is separate. Commands permit explicit enum selection. | An IDLE action does not imply an IDLE main state. Direct label setters are mutations, not passive diagnostic substitutes; none was issued. |
| `:209–241,264–300` | State changes validate transition rules under a reactor mutex. Pre-hooks run before update; label update and successful history entry precede post-hooks. Post-hook exceptions are logged. Same-state/same-action requests can return early. | A reported target label or successful history record cannot attest post-hook completion/success. No supported inflight marker or atomic lifecycle read is exposed. |
| `:243–249,302–314` | State update can reset action to IDLE; exit_to_idle changes labels subject to exit rules. | Label reset is not a queue drain, motion wait, calibration result or physical completion acknowledgment. |
| `:164–165,209–241` | Default hook registrations are commented; hook registration APIs exist. No concrete external registrations were found in the searched extracted Klipper Python/config corpus. | This search does not attest the live hook list, extensions or loaded template/code identity. Keep loaded hook identity unknown. |

The bridge recognizes only exact integer members, not bools, integral floats,
enum-name strings or numeric strings. Raw private peer fields and arbitrary
history/error/template text are not returned. It imposes no invented cross-field
truth table. ABNORMAL and other recognized nonzero reports conservatively veto
idle even when exception reporting is clear or incomplete.

## Virtual SD and control ordering

- `virtual_sdcard.py:223–263,264–285`: worker activity, file cancellation,
  statistics updates and machine exit are separate operations. The SD exit helper
  attempts EXIT_TO_IDLE only while machine state reports PRINTING; exceptions are
  logged. No atomic relationship between these reports is established.
- `:540–569`: SD worker setup/seek precede SET_MAIN_STATE PRINTING, which precedes
  `print_stats.note_start`. A label/statistics/worker combination can therefore
  reflect intermediate progress. Machine state is an additional veto, not a
  replacement for any prior SD/statistics/pause check.
- `:467–485`: power-loss restore requires main IDLE; clearing recovery information
  separately refuses PRINTING and can stop timelapse/reset job information.
  Neither command is used as a read or accepted in restricted G-code.
- `:1274–1287`: refreshing saved move environment requires machine PRINTING and
  paused print statistics independently. Those labels alone do not expose the
  saved environment or establish its correctness.
- `:1629–1644,1948–1967`: restore enters PRINTING/PRINT_PL_RESTORE before parsing
  saved data; success resets action before resuming SD. Failure can reset main
  IDLE after other cleanup. Therefore idle labels cannot attest successful restore
  or absence of earlier side effects.
- `pause_resume.py:140–164`: resume separately checks paused statistics, machine
  PRINTING/IDLE action and saved pause. The outer macro can feed/home/select/heat/
  purge/clean/restore coordinates, as traced in the pause report. `fluidd.cfg`
  action markers at 521–523,624,868–874,1262–1281 bracket selected sequences;
  their labels do not certify all transitive physical effects.

Supported reads therefore add useful conservative activity evidence, while
`machine_transition_completion` and `loaded_state_hook_identity` remain explicit
unestablished dependencies. HTTP provider reads, including one query, remain
non-atomic; repeated equal IDLE labels cannot exclude intervening changes, stale
peer data, other clients or buffered motion. No unsafe state was induced on hardware.

## Receipt enforcement, verification and next action

Both opening status and closing runtime/job snapshots select the same fixed two
fields. Missing/changed reports block preparation, dispatch or uncertain-result
promotion through the existing repeated-read and timestamp checks. Policy 8
refuses policy-1–7 dispatch/promotion, including matching bytes after restart.
Historical fields default to unknown solely for deserialization; terminal results
retain original meaning and observation time. No upload is replayed. Existing
path/root/handle, mapping/material/feed/nozzle, thermal/consumption, hash, expiry,
serialization and reconciliation-watermark safeguards remain.

Regressions first reproduced ignored reports, positive idle with busy/unknown
machine state, phase races and policy-7 reuse. Actual MCP/loopback HTTP covers
schemas, main/action drift, missing reports, restart/no-replay and old-policy
refusal. The [execution ledger](../superpowers/plans/2026-10-26-machine-state-evidence.md)
records full verification and independent review. These are software checks,
not hardware upload/control/camera acceptance.

Full suites passed **520 tests on Python 3.11.14 and 3.13.12**; Ruff check/format
and wheel/source builds passed. Independent fresh-context review found no
actionable findings or deferred minors, separately passed all 520 tests on
Python 3.13.12 and verified historical policy-7 shapes with new fields absent,
terminal timestamp preservation and no replay. Exact artifact AST comparison
confirmed all 15 main-state and 43 action members. Final audit: 60 source/doc
files, 130 local links, both archives and 19 ignore samples; no configured private
literals/generated artifacts, credential-pattern matches or broken links. All
12 source modules match both packages. Hardware/loaded-code/physical acceptance
remains outside these software checks.

All eight intact exports retain original bytes/hashes and first refusals:
01–04/08 `unsupported_command` at EXCLUDE_OBJECT_DEFINE; 05–07 `job_requirements`
for one-entry consumption/material versus four-entry nozzle metadata. These are
first failures only. No safety/setup commands were stripped or mappings guessed.
Transform/provenance, actual trapq, saved K, hidden feed/thermal/consumption,
startup/metadata, pause/end callbacks and camera lifecycle remain unresolved.

Next nonduplicative work: trace supported `print_task_config.get_status` job flags
and their read-time side effects against startup/end/feed/camera consumers. Define
which bounded reported booleans/arrays can be bound privately without treating
reset flags as completed actions or accepting macro bodies. Reuse the existing
artifact and saved reports; do not repeat machine/pause/head/mesh snapshots.
If decisive callback or physical evidence remains unavailable, record that exact
limit and advance a separate bounded camera lifecycle/source contract. Hardware
acceptance still needs separate authorization; every print start also needs its
specific plate and fresh human installed/clear-bed confirmation. Readiness and
the upload/profile/control/camera/release milestones remain incomplete.
