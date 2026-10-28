# Response evidence correction — 2026-10-28

Base: `a150477fe8fa233c162768b37ac1caff86f81176`, clean `main`. This is an
independent software contract after the completed observation-retention fix.
No live printer query, desktop operation, source download, upload/start or camera
operation was issued. Hardware readiness remains incomplete.

## Reproduced defects and correction

1. Default `json.loads` retained only the last repeated object member. An otherwise
   complete synthetic status with `is_active: true` then `false` produced
   `ok`, inactive SD and positive idle. Contradictory upload start/queue/root/path
   members were also collapsed before acknowledgment checks.
2. A firmware-version regex restored raw labels after the privacy projection had
   rejected them. A version-shaped API key, numeric key substring, configured
   address prefix or overlong version could bypass the intended filters.

An independent reviewer separately reproduced both defects. These are malformed
peer/privacy contract failures, not observed printer faults. No firmware trace or
hardware probe is needed to establish Python's duplicate-member behavior.

Use one duplicate-rejecting object hook for all parsed printer JSON. It applies
at every depth, including arrays, equal duplicate values and escaped key names.
It permits the same field in separate objects. Affected responses return sanitized
`invalid_response` with no normalized evidence; capabilities can retain partial
data from other valid endpoints. A malformed/ambiguous upload
acknowledgment remains terminal `unknown`/`upload_contract`, flags unconfirmed,
and repetition after restart returns the historical result without another POST.
The raw-download JSON probe only classifies error envelopes: parsing does not
accept bytes, and failed parsing still leaves remote bytes subject to exact
size/SHA256 checks. No arbitrary path or endpoint is added.

Move the firmware-format exception into the bounded display projection, exempting
only generic address detection. Configured credentials/hostname and label length
remain checked. Ordinary firmware output remains supported.

Policy **12** fences policies 1–11 for new dispatch and uncertain-result promotion,
because their evidence may have discarded duplicate fields. Terminal history is
unchanged. All prior path/handle/root, mapping/feed/nozzle/material, thermal and
consumption, hash/time/expiry/serialization and no-replay safeguards remain.
No tool, dependency, configuration or G-code acceptance is added.

## Verification and review

The initial 13-case regression run failed 12 and passed the separate-object
positive control before implementation. The completed 17-case module passes,
including pre-dispatch refusal, ambiguous-ack restart, recoverable reconciliation
read failure, secret/host/length projection and real MCP subprocesses over a
loopback HTTP server. An isolated baseline-source rerun fails 14 and passes 3:
its two MCP children load the current editable install, so those two passing
checks are current-code verification, not baseline red evidence.

Fresh complete suites passed **785 tests on Python 3.13.12 in 112.68 s** and
**785 on Python 3.11.14 in 112.95 s**, each exit 0. Ruff check/format and wheel/
source builds passed. All eight original exports retain their bytes, hashes and
first refusals. The separate native diagnostic remains byte-identical and
rejected. Software checks do not establish hardware compatibility.

The initial independent reviewer ran 89 existing checks and the two synthetic
reproductions. A fresh final reviewer separately ran 59 targeted tests including
real MCP and old-policy refusal. It also passed four adversarial duplicate-read
shapes (including escaped and surrogate-equivalent keys), four duplicate-ack
shapes, six label checks, and actual-MCP credential redaction with empty stderr.
It found no actionable code issues. Its documentation precision suggestion about
partial capabilities was applied: other successful endpoints can retain data.
The reviewer independently compared all 12 wheel modules and all 81 existing
source-distribution files with the checkout, without mismatches. It inspected
both full-suite receipts rather than rerunning both full suites.
The current complete audit checks 81 files, 250 local links, both archives and
47 ignore samples with zero configured private-literal/generated-artifact or
broken-link findings. Known credential-pattern scans also found zero matches in
tracked/new files and both archives. All 14 changed files match the source
archive; all 12 modules match both archives. Default/local uploads are disabled;
dependencies and local configuration are unchanged. Raw scripts/results stay
ignored under `.tmp/json-evidence/`;
initial independent probes stay in `.tmp/read-contract-review/`.

## Remaining readiness and next action

No supported passive contract binds effective hidden parameters and complete
startup demand to the saved diagnostic file. The prior transfer/preprint/source
investigations are closed; repeating them or starting as an experiment does not
resolve that gap. Fresh installed/clear-bed human confirmation would also be
required after uncertain intervening activity. Controls and camera lifecycle
remain unimplemented; transform/provenance and stock-file dependencies remain
unknown. Uploads stay disabled locally and by default.

Next obtain a new supported passive effective-parameter/startup diagnostic from
the vendor, or a concrete new supported read-only contract. Do not repeat this
JSON/privacy correction, closed firmware traces or the existing file transfer.
