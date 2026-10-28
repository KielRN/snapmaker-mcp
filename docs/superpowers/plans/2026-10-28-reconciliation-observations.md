# Reconciliation observation retention plan

> **For agentic workers:** Use superpowers:executing-plans for the bounded correction and independent final review.

**Goal:** A failed or cancelled evidence sequence cannot discard a newer completed
source observation and let older evidence verify an uncertain upload after restart.

**Architecture:** An optional synchronous observation sink in `Coordinator._evidence`
records valid source times immediately after opening status, materials and closing
runtime reads. Verification supplies a monotonic SQLite sink under the existing
locks. Source times record observation history even when field validation fails;
they do not make the failed evidence acceptable. Increment receipt policy to 11.

**Tech stack:** Existing Python, HTTPX, Pydantic, SQLite and MCP; no dependencies.

**Spec:** [Existing transaction design](../specs/2026-10-24-snapmaker-u1-mcp-design.md)
and [previous watermark correction](2026-10-27-reconciliation-watermark.md).

## Constraints and review focus

Stay on owner-authorized `main`; preserve unrelated work. Keep five tools,
restricted G-code, disabled uploads, original bytes, every existing safety guard
and no-replay behavior. Policies 1–10 cannot dispatch/promote uncertain receipts.
Historical terminal receipts remain historical. No hardware control acceptance.

Exercise later material failures, closing drift/incomplete fields, busy opening
status, cancellation before later reads, backwards/invalid times, equal-time
recovery, process restart and the actual MCP/HTTP boundary. A completed response
with a valid numeric source timestamp has observable history even when other
fields fail validation; missing/invalid timestamps cannot attest newer history.

## One task: retain every completed observation

- [x] Add restart regressions using real coordinator/normalizers/SQLite and synthetic
  HTTP for later read/validation failures, invalid/backwards times and cancellation.
  Prove older matching bytes remain unknown and equal-time recovery sends no POST.
- [x] Add one actual MCP/loopback restart regression and policy-10 refusal cases.
- [x] Run regressions before production edits; retain the expected failures.
- [x] Add the optional `on_observation: Callable[[float], None] | None` sink to
  `_evidence`; call it before later validation/awaits for valid bounded timestamps.
  In `_verify`, synchronously save only a greater watermark, including both
  evidence windows. Retain current validation/error ordering and no POST replay.
- [x] Run targeted checks then both complete Python suites, Ruff and builds.
- [x] Record ordinary preprint UI evidence separately from effective parameters:
  existing remote file located; options displayed but no Send/setter selected.
- [x] Update state/roadmap/decisions/README/changelog; independently review final
  source/tests/docs and package/private-artifact scope, fix material findings.
- [x] Inspect complete tree/branch and prepare an integration gate that stages
  only the reviewed scope after comparing raw hashes and upstream synchronization.

Execute that gate only after final record/package recheck. The actual commit,
push, independent remote match, clean-tree result and automation memory are saved
locally after integration; no self-referential commit identity is embedded here.

## Execution evidence

Initial independent review reproduced two policy-10 failures without tracked edits:
new status 2000 then material timeout, and closing runtime 2000 with offset drift.
Both left a durable watermark of 1000 and incorrectly verified matching bytes at
1500 after restart, with exactly one historical POST. Existing focused checks
passed 82 tests; no hardware request was needed. Local evidence is ignored.

Parent observed **14 expected failures / 28 passes** before production edits,
including actual MCP restart and policy-10 refusal cases. The corrected initial
focused set passed **166 tests**. Independent review then requested explicit
post-download-window regression coverage. The added cases distinguish both
evidence windows. An isolated copy with only the second sink connection omitted
failed **nine cases** (14 passed); the complete new module passed **53 tests**
against production code. This mutation experiment did not alter tracked source.
One temporary test fixture raised its timeout before the selected window; its
failed expectation was corrected to inject only within that window, then the
red/green mutation check was repeated. Both complete suites are rerun after the
test expansion; final results are recorded below.

Final full suites passed **764 on Python 3.13.12 in 105.69 seconds** and
**764 on Python 3.11.14 in 104.87 seconds**, including actual MCP/loopback HTTP.
The independent reviewer separately passed 127 initial focused checks and all
53 expanded observation tests, plus three ignored second-window restart probes.
It confirmed both sink connections and requested the added tracked coverage.

The sink saves only greater bounded numeric source times through the existing
SQLite FULL-sync store, under coordinator/OS locks. Valid time with incomplete,
changed or busy fields is retained history, not acceptable evidence. Missing,
boolean, string, nonfinite, negative and oversized times cannot advance it;
backwards times cannot lower it. Both verification windows and cancellation
during material/closing reads retain earlier completed observations. Restart
refuses older evidence and permits equal-time valid matching bytes with exactly
one historical POST. Abrupt process kill at each new save boundary was not
separately injected; task cancellation and durable close/reopen were tested.
Uncollected observations, atomicity, stale peers, firmware code identity and
physical acceptance remain unestablished. Long-running clients need restarting
to load the new policy; actual MCP tests start fresh subprocesses.

Ordinary saved-file/UI findings are in the
[diagnostic report](../../research/2026-10-27-diagnostic-preprint-evidence.md#subsequent-physical-clearance-and-saved-file-inspection).
No Send/setter/start, new transfer, Play/stop/light, pairing or direct live API
probe was selected. The observed viewer-off transition is not cleanup evidence.
Prior human installed/clear-bed clearance remains historical; startup/effective
parameters still block physical acceptance. No closed firmware/source trace was
repeated and no new file is accepted.

## Final review and package gates

Ruff check/format and wheel/source builds passed. Complete audit checked **79
files, 246 local links, two archives and 43 ignored runtime samples**, with zero
configured private-literal, known credential-pattern, generated-artifact or
broken-link findings. All 12 modules match both archives and all 12 changed/new
source/test/document files match the source archive. All eight original export
bytes/SHA256/first refusals and the native diagnostic bytes/refusal remain
unchanged. Defaults and local uploads remain disabled. Dependencies/configuration
are unchanged. Ignored evidence lives under `.tmp/preprint-options/`.

Independent final review found **no actionable or deferred findings** across the
complete 12-file scope. It independently checked package bytes and artifact
exclusions, read both parent full-suite receipts and bounded audit outputs, and
requested the second-window coverage now included. It did not rerun both full
suites, independently attest UI screenshots, observe physical clearance, prove
camera cleanup or claim hardware compatibility. Two minor timeline/wording
issues were corrected before final review. These verdict-record edits receive
a final package refresh and record-only review/hash check before integration;
unchanged source/tests do not require another full-suite run.

## Next nonduplicative action

The saved-file preprint UI inspection is complete. Effective file-bound hidden
parameters and full stock startup demand still need a supported passive vendor
diagnostic; the inspected UI/source contracts do not provide one. Do not repeat
the same source traces, upload, UI navigation or guessed status/config probes.
Do not submit start/options as experiments. Physical start additionally requires
fresh human installed/clear-bed confirmation and all original safeguards.
Camera ownership/freshness/completed cleanup and print-control/hardware acceptance
remain incomplete. Keep the same automation active; no readiness claim or pause.
