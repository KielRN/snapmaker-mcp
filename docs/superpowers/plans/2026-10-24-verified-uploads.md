# G-code validation and verified uploads implementation plan

> Execute inline using the existing approved design and the owner's explicit
> implementation request. No branch change or live mutation is authorized.

**Goal:** Prepare one selected plain G-code file and verify an upload by remote
SHA256, with durable idempotency and conservative failure handling.

**Architecture:** A fail-closed parser inspects commands and all consumption
entries. Preparation binds immutable bytes, plate, explicit mapping, current
material/feed evidence and printer identity. SQLite receipts and a process/file
lock serialize uploads; an inflight record is committed before the POST. Repeat
IDs return history or reconcile by GET, never resend a POST.

**Tech stack:** Existing Python 3.11+, MCP SDK, HTTPX, Pydantic; standard-library
SQLite, hashing and platform file locks. No slicer or new runtime dependency.

**Spec:** [Bridge design](../specs/2026-10-24-snapmaker-u1-mcp-design.md), sections
Tool contract, Print transaction, Configuration boundaries and Acceptance.

## Constraints and implementation choices

- Stay on `main`; preserve unrelated work; commit/push only after final audit.
- All printer mutations in tests target a loopback simulator. Live upload remains
  disabled by default; hardware acceptance is pending.
- Expose `u1_prepare_print` and `u1_upload_print`; listing/start/controls/camera
  remain outside this milestone. Typed strict arguments, sanitized public errors.
- Default receipt lifetime: 600 seconds. No replay of uncertain uploads, even
  after expiry or restart. Bind operation IDs to complete request fingerprints.
- Plain `.gcode` only; bounded bytes/lines, canonical allowed roots, file-handle
  identity checks and reread hash before mutation. Do not echo local paths.
- A deliberately restricted G-code dialect rejects unresolved macros, arcs,
  offset changes and persistent/machine control commands. All executable moves
  and heaters are inspected; comments alone cannot establish safe temperatures.
- Requirements include per-tool mm/g consumption, material, nozzle and filament
  diameter declarations and layer height. Actual positive extrusion participates
  in used-tool detection, including a zero first consumption entry.
- Explicit logical-to-physical mapping must agree with the current printer;
  this milestone never changes job settings. Nozzle evidence must be explicitly
  configured locally because the existing read contract does not establish it.
- Source identities and unresolved installed-firmware assumptions go in a focused
  research report. Static source evidence is not hardware compatibility proof.

## Review focus

Symlink replacement between preparation and upload; an early zero consumption
entry hiding another tool; accepted POST with lost response; two server processes
sharing receipts; a timeout followed by a late remote write. Each requires a
regression test or a documented conservative refusal.

## Tasks

1. [x] Pin the upload/download envelope and no-queue branch from targeted source;
   record identities and installed compatibility limits.
2. [x] Write failing parser/path tests, observe failure, implement bounded safe
   reads and command/metadata inspection, then run the focused tests.
3. [x] Write failing coordinator/HTTP tests; implement strict inputs, config,
   durable receipts, serialization, preparation checks and verified uploads.
   Exercise missing material, changes, expiry, collisions, errors and recovery.
4. [x] Exercise discovery and the full prepare/upload workflow through real MCP
   subprocesses and a local HTTP simulator, including restart reconciliation.
5. [x] Review changes, update all relevant docs, run full tests/Ruff/builds and
   inspect tracked scope, secret exclusions and package contents.

**Integration:** The owner-directed commit/push to `main` follows the final audit;
Git is the integration receipt. No branch creation/switch or PR is requested.

## Execution record

- Baseline: clean `main`, `49b09de`; 59 tests reported in prior evidence.
- Existing design and this request authorize implementation without another
  approval gate. Internal parser/configuration details are engineering choices.
- No existing Graphify graph; no rebuild performed.
- Pinned upload/application/G-code source hashes verified; contract and hardware
  limits recorded in [upload evidence](../../research/2026-10-24-uploads.md).
- Parser/coordinator/MCP tests were observed failing before implementation.
  Subsequent regression cycles covered E modes/tool origin, negative E, command
  line limits, duplicate claims and read unavailability. Process lock, late write,
  cancellation and actual MCP restart tests exercise durable recovery.
- Independent review reproduced two E-state bypasses; both are fixed. No other
  important findings remained. Its resource concern was addressed with lazy
  bounded passes and worker-thread file inspection. No hardware access occurred.
- Final verification: 123 tests on Python 3.11.14 and 3.13.12, Ruff check/format,
  wheel/source builds. Audit: 27 changed files, all 37 tracked files scanned,
  46 local documentation links and both archives checked. Configured private
  values/generated artifacts were absent; nine runtime ignore samples passed.
- Remote preflight: fetched `origin/main` matched local baseline `49b09de`.
