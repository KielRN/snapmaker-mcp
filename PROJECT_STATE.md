# Project state

Last updated: 2026-10-24

## Current stage

The first read-only Python/stdio milestone is implemented as unreleased
`0.1.0.dev0`: `u1_capabilities`, `u1_status`, and `u1_materials`. The owner directed
this design's implementation and subsequently requested a push to `main`.
Future print transactions and camera implementation remain proposed; this does
not complete the full bridge.

## Verified evidence

- 59 tests passed on Python 3.11.14 and 3.13.12. Ruff checks/formatting and wheel/
  source-distribution builds passed. Tests exercise actual stdio MCP plus local
  HTTP simulation, without hardware or credentials.
- Independent review reproduced compression memory amplification and SDK logging
  of malformed request payloads. Both fixes were regression-tested and rechecked;
  no findings remained.
- Local Codex entry `snapmaker_u1` was registered. Its configured command/env were
  exercised by the official MCP client: initialize, exactly three tools listed,
  all three calls `ok`, empty stderr, **2026-10-24 17:34:05 UTC**. Discovery in
  this already-running chat is unobserved; reload/new-session discovery remains
  a client check.
- Live reads reported firmware `2.0.0.205_20260914173503`, Moonraker `2.0.0`,
  Klipper ready while printing, active virtual SD, and selected physical tool 2
  (`extruder1` / T1). Exceptions were empty in that snapshot.
- All four enabled toolhead sensors and feed modules reported filament present
  and completed/error-free loading. Four loaded states and the 32-slot mapping
  were returned. This is time-specific sensor evidence, not physical inspection
  or a continuing loading guarantee.
- All live checks were reads. No upload/control, motion, camera start/stop,
  firmware/configuration, or calibration action was issued.
- REA 6.7.0 and checksum-verified Node 24.22.1 are isolated. CLI/MCP worked and
  focused camera/lifecycle excerpts parsed. Full-bundle analysis hit its heap
  limit; full doctor readiness and native analysis remain unavailable. See the
  [camera report](docs/research/2026-10-24-camera.md).

Raw replies, local config, receipts, app excerpts, and REA artifacts are ignored.
Tracked fixtures are synthetic. [Read evidence](docs/research/2026-10-24-read-contracts.md)
records pinned public source and installed-contract limits.

## Remaining gaps and next actions

1. Confirm client host discovery after reload. Broader firmware versions, real
   outages, and active exceptions have simulated/source evidence, not hardware
   acceptance.
2. Resolve the native camera messaging boundary and actual wire/authentication
   contract, ownership, expiry, freshness and safe cleanup before camera tools.
3. Implement file/per-tool-consumption/path validation, upload/download hash
   verification, persistent receipts, serialized controls and uncertain-outcome
   reconciliation in later milestones.
4. Obtain specific-job authorization and fresh clear-bed confirmation before any
   start/control hardware acceptance. Print completion/quality checks remain.

The [roadmap](ROADMAP.md) owns milestone status. This milestone is neither a
release nor full print/camera capability.
