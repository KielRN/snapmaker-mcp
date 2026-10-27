# Reconciliation cancellation watermark correction

Date: 2026-10-27 UTC · Scope: software correction; hardware readiness incomplete.

## Reconciled baseline and focused contract

Started on clean `main` at `fc40399`; no other active checkout chat, partial work
or existing Graphify graph. Read the automation handoff and repository ledgers.
The metadata, transform, feed/flow and camera source traces remain closed absent
new evidence. No source download, firmware discovery or printer query was needed.

One ordinary desktop observation found Snapmaker Orca still disconnected on Add
Device. No input, Connect, upload, print/control or camera action was issued. An
attended touchscreen pairing reply was requested; no approval was inferred from
silence. That operator dependency and fresh installed/clear-bed confirmation
remain prerequisites for the later diagnostic workflow.

Independent focused audit of existing file/HTTP/receipt safeguards identified no
additional actionable defect. The parent reproduced a specific reconciliation
failure before changing production code:

1. An uncertain upload retains source time 1000 in its durable journal.
2. Read-only reconciliation completes opening evidence at 2000, then waits for
   remote bytes. Cancellation at that wait leaves only the in-memory update.
3. A restarted coordinator reads unchanged evidence at 1500 and matching bytes.
   Baseline incorrectly returns `ok` instead of retaining `unknown`.

The failing regression exercises real coordinator, SQLite journal, file/hash and
normalization code against synthetic HTTP. It closes/reopens the coordinator
after cancellation. It demonstrates invalid promotion, not another POST or an
observed hardware failure. Ignored red/green receipts are retained locally.

## Implementation and acceptance boundary

Persist the completed opening observation's `runtime_eventtime` synchronously,
before the remote-download await, through the existing Store transaction. The
OS/async locks and SQLite FULL synchronization remain. Saving before the digest
comparison also retains a completed newer observation when its bound state
differs. The closing watermark has no intervening await before its existing save.

Policy 10 prevents policy-1–9 preparations from dispatching and their uncertain
uploads from promotion. Historical terminal results stay historical; never replay
a POST. No new journal schema, tool, runtime field, G-code/export acceptance,
configuration or dependency is introduced. Uploads remain disabled by default
and locally. Expiry, path/root/handle, material/feed/mapping/nozzle, thermal/
consumption, hash, serialization and all runtime guards remain.

The regression also proves equal-time recovery after cancellation can verify the
original bytes with exactly one historical POST. Old policy 9 refusal is exercised
both directly and through actual MCP subprocesses/loopback HTTP. This tests task
cancellation and reopening the durable journal; abrupt process termination at the
new boundary was not independently injected. Successful completed observations
must reach the commit before the next await; no software can attest a response
that was never collected. Repeated HTTP snapshots remain non-atomic and cannot
exclude intervening changes or stale peer data.

## Verification and review

Parent full suites passed **706 tests on Python 3.13.12 in 98.18 seconds** and
**706 on Python 3.11.14 in 98.11 seconds**, including actual MCP/loopback HTTP.
Ruff check/format and wheel/source builds passed. All eight original export byte
sizes/SHA256 values and first refusals remain unchanged: 01–04/08 first reject
`EXCLUDE_OBJECT_DEFINE`; 05–07 first reject conflicting metadata cardinalities.
These remain first failures, not complete stock-file acceptance analyses.

Complete scope audit checked 75 tracked/new files, 227 local links, both archives
and 33 ignored runtime samples. Zero configured private-literal, credential-pattern,
generated-artifact or broken-link findings. All 12 modules match both archives;
all 11 changed files match the source archive. Local uploads are still disabled.
Ignored receipts are under `.tmp/reconciliation-watermark/`; no live printer
request or mutation was issued by the software checks.

Independent initial audit confirmed the root cause and save placement, passed
173 file/upload checks and then 23 targeted cancellation/reconciliation checks,
and found no additional actionable file/HTTP/receipt defect. Independent final
review found no actionable findings in the complete 11-file change, reviewed all
parent gate receipts and independently checked current archive byte identity.
It did not repeat the full suites. Verdict-record edits require a final package
refresh and record-only identity check before integration. Abrupt process
termination at the new boundary and all hardware claims remain outside this
verification.

## Next nonduplicative action

Complete one attended ordinary LAN pairing when the owner is ready at the
touchscreen. Then inspect the connected preprint workflow for one exact very
small diagnostic plate sliced externally, preserving all setup/safety and
validation checks. Obtain fresh installed/clear-bed confirmation before start.
No unattended pairing retries or repeated closed source traces. Full stock-file
dependencies, file-bound effective parameters, control/camera contracts and honest
hardware transfer/print/quality acceptance remain unresolved. Keep the automation
active until the intended scope has actual evidence.
