# Project state

Last updated: 2026-10-25

## Current stage

Unreleased `0.1.0.dev0` now exposes five Python/stdio tools: three installed-U1
read tools plus restricted `u1_prepare_print` / `u1_upload_print`. File transactions
are verified against local simulation and actual MCP subprocesses; uploads remain
disabled by default and unaccepted on hardware. Print controls, broad stock-U1
G-code support and camera implementation remain incomplete. The owner requested
this focused implementation and commit/push on `main`, with no live mutations.

## Verified evidence

- Bounded runtime-evidence follow-up: one seven-object GET at **2026-10-25
  13:59:41 UTC** confirmed reported per-head offsets, global homing origin,
  coordinate/mode fields and populated mesh matrices. Selected head 2 coexisted
  with all heads reported parked and no homed axes. The five-tool bridge now
  normalizes this subset in status and binds repeated observations to policy-4
  preparations/receipts, refusing missing/inconsistent/drifting/backwards-time
  evidence without upload replay. Calibration provenance, full transform chain
  and machine-space motion remain unestablished. All eight intact exports still
  fail. See [runtime evidence](docs/research/2026-10-25-runtime-evidence.md).
- Runtime follow-up verification: **300 tests passed on Python 3.11.14 and
  3.13.12**, including actual MCP/loopback HTTP, runtime races and policies 1–3
  dispatch/reconciliation refusal. Ruff check/format and wheel/source builds
  passed. Independent review ran the full pre-fix 295-test suite and identified
  two P2 contradictions (all-parked selection and empty-mesh extrema); both were
  reproduced in failing normalization/preparation regressions and corrected.
  Final 300-test suites passed after fixes; no finding was deferred. Audit:
  49 source/doc files, 76 local links, both archives and nine ignore samples;
  no configured private value or generated runtime artifact in tracked/package
  scope. Exactly one new live GET; no mutation or hardware acceptance.
- Startup/toolchange follow-up traces physical selection/retries, calibrated
  XYZ/E origins, saved flow K, hidden feed/calibration/purge, homing/mesh and
  pause/object/end/camera branches. Restricted validation now forgets XYZ after
  T and active tool/E after G28, binds positive heater targets to requirements,
  refuses physical heater aliases and enforces firmware selector syntax.
  Policy 3 prevents policy-1/2 dispatch/promotion without replay. All eight
  unchanged normal exports remain rejected; uploads remain disabled. See the
  [focused chain/evidence report](docs/research/2026-10-25-startup-toolchange.md).
- Startup/toolchange verification: **246 tests passed on Python 3.11.14 and
  3.13.12**, including actual MCP/loopback HTTP and policy-2 restart refusal.
  Ruff check/format and wheel/source builds passed. The complete 43-file scope,
  64 local document links, both archives and nine ignore samples passed the
  privacy/artifact audit. Independent final review found no actionable issues;
  it separately passed 187 relevant tests and rechecked the source identities.
  This follow-up issued no live printer request.
- Firmware-matched G-code follow-up: eight representative local exports inspected;
  36 previously unsupported command names plus unsupported parameter forms found.
  **No complete normal export is newly accepted.** Bounded progress/fan/acceleration
  forms and explicit-G17 absolute XY arcs now work in supported synthetic programs.
  Macro/offset/calibration/camera effects remain blocking; three exports also have
  ambiguous one-entry filament/four-entry nozzle metadata. See the
  [version-matched report](docs/research/2026-10-25-orca-u1-gcode.md).
- Fresh read-only capability/configuration evidence confirms firmware
  `2.0.0.205_20260914173503`. Its downloaded vendor artifact matches 14 selected
  Python source files and two configs from pinned release head `bc271fb351f8c3ad84300e652e46fd93c53b9de1`.
  All 87 compared macro executable bodies agree (86 normalized texts match; two
  inline comments account for the other). This is static/version/configuration
  evidence, not attestation of live code or hardware upload/print acceptance.
- Previous independent follow-up review reproduced inherited arc-plane and decimal fan-ID
  syntax issues. Both were regression-tested and fixed. Policy identity 2 blocks
  old-receipt dispatch/promotion while retaining unknown-outcome no-replay rules.
  This is superseded by policy 3's stricter validation.
- Previous follow-up verification: **215 tests passed on Python 3.11.14 and 3.13.12**,
  including actual MCP numeric-form success and stock/unsafe-form refusal.
  Ruff check/format and wheel/source builds passed. Independent recheck found
  no remaining material issue in the reviewed scope. Only live GETs were issued.
- Previous upload milestone: **123 tests passed on Python 3.11.14 and 3.13.12**.
  Ruff checks/formatting and wheel/source builds passed. Real MCP subprocesses
  exercised five-tool discovery, preparation, HTTP multipart uploads, corruption,
  material/mapping/path failures, HTTP-200 errors and restart reconciliation.
  Additional tests cover expiry, late writes, cancellation, duplicate IDs/claims,
  state races and a second process holding the journal lock.
- Independent upload review reproduced G91/M82 and tool-change E-origin bypasses;
  both are regression-tested and fixed. Cold retraction is also accounted for.
  A resource concern was resolved with bounded lazy parsing and worker threads.
  The narrow source contracts and limitations are recorded in
  [upload evidence](docs/research/2026-10-24-uploads.md). No hardware interaction
  occurred during this milestone; no upload enablement or live settings changed.
- Historical read baseline: 59 tests passed on Python 3.11.14 and 3.13.12. Ruff checks/formatting and wheel/
  source-distribution builds passed. Tests exercise actual stdio MCP plus local
  HTTP simulation, without hardware or credentials.
- Independent review reproduced compression memory amplification and SDK logging
  of malformed request payloads. Both fixes were regression-tested and rechecked;
  no findings remained.
- Local Codex entry `snapmaker_u1` was registered. Its configured command/env were
  exercised by the official MCP client: initialize, exactly three tools listed,
  all three calls `ok`, empty stderr, **2026-10-24 17:34:05 UTC**. Discovery in
  this chat was subsequently confirmed by a discovered `u1_capabilities` call at
  **2026-10-24 17:54:59.822526 UTC**, returning `ok` and the same firmware.
- Live reads reported firmware `2.0.0.205_20260914173503`, Moonraker `2.0.0`,
  Klipper ready while printing, active virtual SD, and selected physical tool 2
  (`extruder1` / T1). Exceptions were empty in that snapshot.
- All four enabled toolhead sensors and feed modules reported filament present
  and completed/error-free loading. Four loaded states and the 32-slot mapping
  were returned. This is time-specific sensor evidence, not physical inspection
  or a continuing loading guarantee.
- All live checks were reads. No upload/control, motion, camera start/stop,
  firmware/configuration, or calibration action was issued.
- Isolated REA 6.7.0/Node 24.22.1 and checksum-verified Rizin 0.9.1 now support
  focused native inspection. Seven DLL functions (34,540 bytes) and seven more
  GUI excerpts were inspected without executing target code. The native WCP
  camera branch reaches JSON-RPC over TLS MQTT; pinned Orca 2.4.0 source describes
  certificate bootstrap and response correlation. This is static evidence, not
  an installed-printer camera transaction. Full doctor/Ghidra readiness is not claimed.
- The native camera branch drops the GUI's optional `clientid`. A 300-second GUI
  renewal/close timer is established; server expiry and ownership are not. See
  the [camera report](docs/research/2026-10-24-camera.md) for anchors and limits.

Raw replies, local config, receipts, app excerpts, and REA artifacts are ignored.
Tracked fixtures are synthetic. [Read evidence](docs/research/2026-10-24-read-contracts.md)
records pinned public source and installed-contract limits.

## Remaining gaps and next actions

1. Broader firmware versions, real outages, and active exceptions have
   simulated/source evidence, not hardware acceptance.
2. Validate the native camera branch against installed firmware with one bounded,
   redacted passive trace of an ordinary operator-authorized transaction. No
   camera opening/closing is authorized by this investigation. Server ownership,
   expiry, credential provisioning, freshness and safe cleanup remain prerequisites
   for camera tools; the trace alone will not resolve them all.
3. Obtain separately authorized hardware acceptance of multipart upload/download,
   exact path/flag envelope, no-start/no-queue behavior, authentication and recovery.
   Bind the traced stock-U1 macro/offset/mesh, per-head thermal/consumption and
   conditional runtime dependencies before accepting normal Orca U1 profiles.
   The reported coordinate/mesh subset is now collected and bound; next resolve
   active transform lifecycle, exclusion and mesh fade/tool-offset/provenance
   through focused source and supported reads. This does not bound the remaining
   macro chains. Current restricted files and journals are described in
   the [upload evidence](docs/research/2026-10-24-uploads.md).
4. Implement future print job-parameter/start/controls after their contracts are
   resolved. The preparation/upload implementation applies no job parameters.
5. Obtain specific-job authorization and fresh clear-bed confirmation before any
   start/control hardware acceptance. Print completion/quality checks remain.

The [roadmap](ROADMAP.md) owns milestone status. This milestone is neither a
release nor full print/camera capability.
