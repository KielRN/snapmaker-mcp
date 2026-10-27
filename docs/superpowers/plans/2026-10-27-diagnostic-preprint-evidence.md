# Diagnostic preprint continuation ledger

Date: 2026-10-27 UTC. Baseline: `bf94ac54a2437b56b94e15f03411c7f2698df23e`.

## Executed scope

- Read the same automation's memory first, then AGENTS/state/roadmap/decisions/
  README. Main was clean and synchronized; no Graphify graph or rebuild. The
  handing-off chat committed to no further project edits. The separate active
  Home3DPrinting chat was inspected for shared-printer activity; no messages sent
  to it and no files changed there. No branch or pull request.
- Reinspected connected ordinary UI using the computer-use skill. Queried the
  existing MCP status/material tools. Prepared one small external model and two
  intact external-slicer exports, then inspected all metadata entries and actual
  setup commands. The native project corrected a local 0.2 mm preset to the
  selected 0.4 mm / 0.20 mm standard process and connected white PLA selection.
  No installed-nozzle or human-clearance attestation was invented.
- Advanced the normal Upload-only path to its second Send page. A premature
  remote-file check stopped before final Send; no Upload replay. Reconciled the
  actual unsubmitted UI and retained one operation/destination/expiry. Embedded
  WebView input refusal persisted after the documented fresh-observation retry;
  operator assistance was requested. The owner replied "sent"; subsequent bounded
  G-code-root readback matched the complete 49,972-byte native file and SHA256.
  Surrounding idle/inactive-SD/runtime/material/thermal/job evidence stayed
  consistent. The final receipt was saved within its original expiry and the
  local OS lock released. No print started or raw response flags captured. See the
  [evidence report](../../research/2026-10-27-diagnostic-preprint-evidence.md).
- Private helper scripts perform bounded reads only and hold a dedicated local
  OS lock across the intended UI operation. SQLite FULL-synced intent precedes
  the UI boundary, including a one-use final-Send marker. No helper POST, start,
  queue, job setter or camera command exists. Bridge local uploads remain disabled
  and have no configured upload journal/roots; these helpers do not configure them.

## Review and fresh verification

- Independent pre-use review found a durable-replay issue in the ignored helper:
  a lost JSON copy could permit another intent despite a saved SQLite record.
  Fixed before any UI Upload click by consulting the durable operation table
  under the held lock. An inert in-memory SQLite check exercised that gate with
  absent/present records. Reviewer reread the fix and cleared the upload-only
  scope with no remaining findings. It separately cleared the first final-Send
  continuation and import guard. It issued no live requests or file writes.
- Fresh parent suites: **706 passed on Python 3.13.12 in 99.57 seconds** and
  **706 passed on Python 3.11.14 in 99.27 seconds**, including actual MCP and
  loopback HTTP. Both processes exited zero. Ruff check and format check passed.
  Source/tests/dependencies are unchanged; software checks do not prove physical
  job suitability, vendor response flags or camera lifecycle.
- Independent final review found no material findings or deferred minors across
  all eight changed documents. It independently hashed both original diagnostic
  files, checked raw native arrays/layer heights and saved before/after receipt
  evidence, and read both full-suite/Ruff logs. It did not rerun the suites/build,
  attest unseen screenshots, wire flags or global printer ownership, or perform
  live calls/writes. Final record-only changes received a separate recheck.
- Fresh Ruff check/format, wheel/source builds, eight original export byte/hash/
  first-refusal checks and the full scope/privacy/link/ignore audit passed.
  Audit: **77 files, 238 local links, two archives and 38 ignore samples**; zero
  configured private-literal, known token-pattern, generated-artifact or broken-
  link findings. All 12 modules match both archives and all eight changed docs
  match the source archive. Git/push receipts remain in the ignored handoff.

## Boundaries carried forward

Policy 10, five tools, all eight original refusals and every bridge safeguard
remain unchanged. The new native diagnostic is also rejected. Full readiness
is incomplete. No physical start or fresh installed/clear-bed confirmation.
The existing automation remains active on its current schedule; no new automation,
credit request or pause-as-ready. Keep exact paths, raw observations, generated
files and operation receipts ignored. Use the same operation's read-only
  evidence and the next concrete preprint question instead of rerunning
closed source traces or repeating a mutation.
